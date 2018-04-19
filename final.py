import requests
import json
import secrets
import sqlite3
import random
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.graph_objs import *
import webbrowser

#A user will enter a search for a place. This will provide a rating and/or review back to the user, 
#along with a list of nearby places with nearby ratings and images if found. 
#--------------------------------------------------------------------------------------------
#-----API Keys: (imported from secrets.py)
#--------------------------------------------------------------------------------------------
google_apikey = secrets.google_places_key
yelp_client = secrets.YELP_ClientID
yelp_apikey = secrets.YELP_APIKey
flickr_apikey = secrets.FLICKR_KEY
mapbox_apikey = secrets.mapbox_accesstoken


#--------------------------------------------------------------------------------------------
#-----CACHING & REQUESTING DATA
#--------------------------------------------------------------------------------------------
CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}
    

def params_unique_combination(baseurl, params_d, private_keys=["api_key"]):
    if params_d is not None:
        alphabetized_keys = sorted(params_d.keys())
        res = []
        for k in alphabetized_keys:
            if k not in private_keys:
                res.append("{}-{}".format(k, params_d[k]))
        return baseurl + "_".join(res)
    else:
        return baseurl


def make_request_using_cache(url, params = None, headers = None):
    # unique_ident = get_unique_key(url) 
    unique_ident = params_unique_combination(url, params)   
    if unique_ident in CACHE_DICTION:    ## first, look in the cache to see if we already have this data
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]    
    else:    ## if not, fetch the data afresh, add it to the cache, then write the cache to file
        print("Making a request for new data...")
        resp = requests.get(url, headers = headers, params=params) # Make the request and cache the new data
        # print(resp)
        if params is None:
            CACHE_DICTION[unique_ident] = resp.text #storing entire text of html
        elif url == "https://api.flickr.com/services/rest/":
            text = resp.text[14:-1]
            CACHE_DICTION[unique_ident] = json.loads(text)
        else:
            CACHE_DICTION[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION) #using json as dictionary format in the cache
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]


#--------------------------------------------------------------------------------------------
#-----CLASS DEFINITIONS
#--------------------------------------------------------------------------------------------
class GooglePlace():
    def __init__(self, name, latitude, longitude, rating):
        self.name = name
        self.lat = latitude
        self.lon = longitude
        self.rating = rating

    def __str__(self):
        return self.name + ' (' + str(self.lat) + ', ' + str(self.lon) + ')'

class YelpPlace():
    def __init__(self, name, latitude, longitude, rating, review_count, price, searchterm, url):
        self.name = name
        self.lat = latitude
        self.lon = longitude
        self.rating = rating
        self.review_count = review_count
        self.price = price
        self.searchterm = searchterm
        self.url  = url

    def __str__(self):
        return self.name + ' (' + str(self.lat) + ', ' + str(self.lon) + ') is rated ' + str(self.rating) 

class FlickrPhoto():
    def __init__(self, title, latitude, longitude, farmid, serverid, id, secret, req, searchterm):
        self.title = title
        self.farmid = farmid
        self.serverid = serverid
        self.id = id
        self.secret = secret
        self.lat = latitude
        self.lon = longitude
        self.req = req
        self.searchterm = searchterm

    def __str__(self):
        return 'https://farm{}.staticflickr.com/{}/{}_{}_h.jpg'.format(self.farmid,self.serverid,self.id,self.secret)


#--------------------------------------------------------------------------------------------
#-----INITIALIZE DATABASE
#--------------------------------------------------------------------------------------------
DBNAME = 'final.db'

def init_db(db_name):
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
    except Error as e:
        print(e)

    create_table_google = '''
        CREATE TABLE 'GooglePlaces' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT,
            'Latitude' REAL,
            'Longitude' REAL,
            'Rating' REAL
            );
        '''
    create_table_yelp = '''
        CREATE TABLE 'YelpPlaces' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'SearchId' INTEGER,
            'SearchName' TEXT,
            'Name' TEXT,
            'Latitude' REAL,
            'Longitude' REAL,
            'Rating' REAL,
            'ReviewCount' INTEGER,
            'Price' TEXT,
            'URL' TEXT
            );
        '''
    create_table_flickr = '''
        CREATE TABLE 'FlickrImages' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'SearchId' INTEGER,
            'SearchName' TEXT,
            'ReqId' INTEGER,
            'Title' TEXT,
            'FarmId' TEXT,
            'ServerId' TEXT,
            'PhotoId' TEXT,
            'Secret' TEXT,
            'URL' TEXT
            );
        '''
#SearchId is primary key from google places
#SearchName is name of location we are searching for photos around
#ReqId is whether the place lives in google (1) or yelp (2)  

    cur.execute(create_table_google)
    cur.execute(create_table_yelp)
    cur.execute(create_table_flickr)

    conn.close()


#--------------------------------------------------------------------------------------------
#-----GATHER DATA FROM SOURCES
#--------------------------------------------------------------------------------------------
#Google Places API (Challenge Score: 2)
def get_place_info(searchterm):
    textsearchurl = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
    textparams = {'query':searchterm, 'key':google_apikey}
    
    print('-----------------')
    print("Google Places API")
    textresp = make_request_using_cache(textsearchurl,textparams)
    places = []
    if len(textresp['results']) != 0:
            for ea in textresp['results']:
                lat = ea['geometry']['location']['lat']
                lon = ea['geometry']['location']['lng']
                name = ea['name']
                if 'rating' in ea:
                    rating = ea['rating']
                else:
                    rating = "None"
                places.append(GooglePlace(name, lat, lon, rating))
    else:
        print("No place found in Google Place Search")
    # for obj in places:
    #   print(obj)
    return places


#Yelp Fusion (Challenge Score: 4)
def get_yelp_info(lat,lon,searchterm):
    yelp_baseurl_search = 'https://api.yelp.com/v3/businesses/search'
    yelp_headers = {'Authorization': 'Bearer %s' % yelp_apikey, }
    yelp_parameters = {}
    yelp_parameters["latitude"] = lat
    yelp_parameters["longitude"] = lon
    
    print('-----------------')
    print("Yelp Search API")
    yelpresp = make_request_using_cache(yelp_baseurl_search, params = yelp_parameters, headers = yelp_headers)
    yelpplaces = []
    for ea in yelpresp['businesses']:
        name = ea['name']
        latitude = ea['coordinates']['latitude']
        longitude = ea['coordinates']['longitude']
        rating = ea['rating']
        review_count = ea['review_count']
        url = ea['url']
        if 'price' in ea:
            price = ea['price']
        else:
            price = "None"
        yelpplaces.append(YelpPlace(name, latitude, longitude, rating, review_count, price, searchterm, url))
# for obj in yelpplaces:
#   print(obj)
    return yelpplaces


#Instagram API (Challenge Score: 6) #no longer works??
#Flickr API (Challenge Score: 2)
def get_flickr_photos(lat,lon, searchterm, request):
    flickr_baseurl = "https://api.flickr.com/services/rest/"
    flickr_parameters = {}
    flickr_parameters["method"] = "flickr.photos.search"
    flickr_parameters["api_key"] = flickr_apikey
    flickr_parameters["format"] = "json"
    flickr_parameters["lat"] = lat
    flickr_parameters["lon"] = lon
    flickr_parameters["tag_mode"] = "all"

    print('-----------------')
    print("Flickr Data")
    flickrresp = make_request_using_cache(flickr_baseurl, params = flickr_parameters)
    photos = []
    if request == "Google":
        req = 1
    else:
        req = 2
    for ea in flickrresp['photos']['photo']:
        id = ea['id']
        farmid = ea['farm']
        serverid = ea['server']
        secret = ea['secret']
        if 'title' in ea:
            title = ea['title']
        else:
            title = "None"
        photos.append(FlickrPhoto(title, lat, lon, farmid, serverid, id, secret, req, searchterm))
    # for obj in photos:
    #   print(obj)
    return photos


#--------------------------------------------------------------------------------------------
#-----ADD TO DATABASE:
#--------------------------------------------------------------------------------------------
def insert_google_data(places,db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    for obj in places:
        checkloc = '''
                    SELECT Name
                    FROM GooglePlaces
                    WHERE GooglePlaces.Name = ?'''
        check = cur.execute(checkloc,[obj.name]).fetchall()
        
        if len(check) > 0:
            print("Already exists in GooglePlaces")
            break
        else:
            insertions = (obj.name, obj.lat, obj.lon, obj.rating)
            insertstatement = '''
                INSERT INTO 'GooglePlaces' (Name,Latitude,Longitude,Rating)
                VALUES (?,?,?,?)
                '''
            cur.execute(insertstatement,insertions)
            conn.commit()

    conn.close()

def insert_yelp_data(yelpplaces,db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    for obj in yelpplaces:
        # print(obj)
        checkloc = '''
                    SELECT Name
                    FROM YelpPlaces
                    WHERE YelpPlaces.Name = ? AND YelpPlaces.SearchName = ?'''
        check = cur.execute(checkloc,(obj.name, obj.searchterm)).fetchall()

        if len(check) > 0:
            print("Already exists in YelpPlaces")
            break
        else:
            getkeystatement = '''
                    SELECT Id, Name 
                    FROM GooglePlaces
                    WHERE GooglePlaces.Name = ?'''
            cur.execute(getkeystatement, [str(obj.searchterm)])


            for ea in cur:
                # print("ea in yelpplaces", ea)
                SearchId = ea[0]

            insertions = (SearchId, obj.searchterm, obj.name, obj.lat, obj.lon, obj.rating, obj.review_count, obj.price, obj.url)
            insertstatement = '''
            INSERT INTO 'YelpPlaces' (SearchId,SearchName,Name,Latitude,Longitude,Rating,ReviewCount,Price,URL)
            VALUES (?,?,?,?,?,?,?,?,?)
            '''
            cur.execute(insertstatement,insertions)
            conn.commit()

    conn.close()

def insert_flickr_data(photos,db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    for obj in photos:
        checkloc = '''
                    SELECT PhotoId,SearchName
                    FROM FlickrImages
                    WHERE FlickrImages.PhotoId = ? AND FlickrImages.SearchName = ?'''
        check = cur.execute(checkloc,(obj.id, obj.searchterm)).fetchall()
        
        if len(check) > 0:
            print("Already exists in FlickrImages")
            break
        else:
            if obj.req == 1:
                getkeystatement = '''
                        SELECT Id 
                        FROM GooglePlaces
                        WHERE GooglePlaces.Name = ?'''
                cur.execute(getkeystatement, [str(obj.searchterm)])

                for ea in cur:
                    SearchId = ea[0]
            else:
                getkeystatement = '''
                        SELECT Id 
                        FROM YelpPlaces
                        WHERE YelpPlaces.Name = ?'''
                cur.execute(getkeystatement, [str(obj.searchterm)])

                for ea in cur:
                    SearchId = ea[0]
                # print(ea[0])

            insertions = (SearchId, obj.searchterm, obj.req, obj.title,obj.farmid,obj.serverid, obj.id, obj.secret, obj.__str__())
            insertstatement = '''
            INSERT INTO 'FlickrImages' (SearchId,SearchName,ReqId,Title,FarmId,ServerId,PhotoId,Secret,URL)
            VALUES (?,?,?,?,?,?,?,?,?)
            ''' 
            cur.execute(insertstatement,insertions)
            conn.commit()

    conn.close()


#--------------------------------------------------------------------------------------------
#-----RETRIEVE DATA FROM DATABASE
#--------------------------------------------------------------------------------------------
def getnearby_fromdb(searchterm):
    nearby = []
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    sql = '''SELECT Name, Latitude, Longitude, Rating, ReviewCount, Price, SearchName, URL
            FROM YelpPlaces
            WHERE SearchName = ?
            '''
    result_list = cur.execute(sql,[searchterm]).fetchall()
    for ea in result_list:
        nearby.append(YelpPlace(ea[0],ea[1],ea[2],ea[3], ea[4], ea[5], ea[6], ea[7]))

    conn.close()

    return nearby


def getflickr_fromdb(searchterm, searchlat,searchlon):
    images = []
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    sql = '''SELECT Title, SearchName, URL
            FROM FlickrImages
            WHERE SearchName = ?
            '''
    result_list = cur.execute(sql,[searchterm]).fetchall()
    for ea in result_list:
        # images.append(FlickrPhoto(ea[0],searchlat,searchlon,ea[1],ea[2],ea[3],ea[4],ea[5],ea[6]))
        images.append([ea[0],ea[1],ea[2]])
    
    return images


#--------------------------------------------------------------------------------------------
#-----DATA PRESENTATION:
#--------------------------------------------------------------------------------------------
#Open image links for places
#Map of place + nearby places
#Comparison chart of ratings for place and nearby places
#List of places nearby with overview
def disp_options():
    display = '''
        1. Show Yelp Review of Nearby Places
        2. Show Map
        3. Show Ratings Comparison
        4. Show Images taken Nearby
        5. New Search
        '''
    return display


def showlist(searchterm):
    num = 1
    places = getnearby_fromdb(searchterm)
    for item in places:
        print('{}. {} ({}) '.format(num, item.name,item.rating))
        num += 1

    select = input('Select Place: ')
    webbrowser.open(places[int(select)-1].url)



def getmaxmin(data_lat,data_lon):
    
    min_lat = 10000
    max_lat = -10000
    min_lon = 10000
    max_lon = -10000

    for str_v in data_lat:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in data_lon:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    lat_axis = [min_lat, max_lat]
    lon_axis = [min_lon, max_lon]


    max_range = max(abs(max_lat - min_lat), abs(max_lon - min_lon))
    padding = max_range * .50
    lat_axis = [min_lat - padding, max_lat + padding]
    lon_axis = [min_lon - padding, max_lon + padding]

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    return (center_lat,center_lon,lat_axis,lon_axis)


def showmap(searchname, searchlat, searchlon):
    nearbylat = []
    nearbylon = []
    nearbyname = []

    nearbyplaces = getnearby_fromdb(searchname)
    for ea in nearbyplaces:
        nearbylat.append(ea.lat)
        nearbylon.append(ea.lon)
        nearbyname.append(ea.name)


    (center_lat, center_lon, lat_axis, lon_axis) = getmaxmin(nearbylat,nearbylon)
    
    Place = dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = [searchlon],
        lat = [searchlat],
        text = [searchname],
        mode = 'markers',
        marker = dict(
            size = 10,
            symbol = 'star',
            color = 'red',
        name = 'Search Place'
        ))

    Nearby = dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = nearbylon,
        lat = nearbylat,
        text = nearbyname,
        mode = 'markers',
        marker = dict(
            size = 6,
            symbol = 'circle',
            color = 'blue',
        name = 'Nearby Places'
        ))
    data = [Place, Nearby]

    layout1 = dict(
        title = 'Nearby Places<br>(Hover for names)',
        geo = dict(
            scope='usa',
            projection=dict( type='albers usa' ),
            showland = True,
            landcolor = "rgb(250, 250, 250)",
            subunitcolor = "rgb(100, 217, 217)",
            countrycolor = "rgb(217, 100, 217)",
            lataxis = {'range': lat_axis},
            lonaxis = {'range': lon_axis},
            center= {'lat': center_lat, 'lon': center_lon },
            countrywidth = 3,
            subunitwidth = 3
    
        ),
    )
    
    fig1 = dict(data=data, layout=layout1 )
    py.plot(fig1, validate=False, filename='Nearby Places' )


def showmap_mapbox(searchname, searchlat, searchlon):
    nearbylat = []
    nearbylon = []
    nearbyname = []

    nearbyplaces = getnearby_fromdb(searchname)
    for ea in nearbyplaces:
        nearbylat.append(ea.lat)
        nearbylon.append(ea.lon)
        nearbyname.append(ea.name)


    (center_lat, center_lon, lat_axis, lon_axis) = getmaxmin(nearbylat,nearbylon)
    
    data = Data([
    Scattermapbox(
        lat=[searchlat],
        lon=[searchlon],
        mode='markers',
        marker=Marker(
            size=10,
            symbol = 'star',
            color = 'rgb(255, 0, 0)'
        ),
        text=[searchname],
        hoverinfo = 'text'
            ),
        Scattermapbox(
        lat=nearbylat,
        lon=nearbylon,
        mode='markers',
        marker=Marker(
            size=8,
            color = 'rgb(0, 0, 255)'
        ),
        text=nearbyname,
        hoverinfo = 'text'
            )
            
        ])
    layout = Layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_apikey,
        bearing=0,
        center=dict(
            lat=center_lat,
            lon=center_lon
        ),
        pitch=0,
        zoom=12
        ),
    )

            
    fig1 = dict(data=data, layout=layout )
    py.plot(fig1, validate=False, filename='Nearby Places' )


def showratings(searchterm):
    nearby = getnearby_fromdb(searchterm)
    places = []
    ratings = []
    for ea in nearby:
        places.append(ea.name)
        ratings.append(ea.rating)


    trace0 = go.Bar(
    y = places,
    x = ratings,
    orientation = 'h',
    marker=dict(
        color='rgb(26, 118, 255)',
        line=dict(
            color='rgb(26, 118, 255)',
            width=1.5,
        )
    ),
    )

    data = [trace0]
    layout2 = go.Layout(
    title='Nearby Ratings',
    )

    fig2 = dict(data=data, layout=layout2)
    py.plot(fig2, filename='Nearby Ratings')



def showimage(searchterm, searchlat,searchlon):
    images = getflickr_fromdb(searchterm,searchlat,searchlon)
    rand_num = []
    selectimages = []
    ct = 0
    sel = 1
    while ct < 10:
        rand_num.append(random.randint(0,199))
        ct += 1
    for num in rand_num:
        print("{}. {}".format(sel,images[num][0]))
        sel += 1
        selectimages.append([images[num][0],images[num][1],images[num][2]])

    select = input("Which image do you want to see? ")
    webbrowser.open(selectimages[int(select)-1][2])


#--------------------------------------------------------------------------------------------
#-----USER INTERFACE:
#--------------------------------------------------------------------------------------------
#Select from a random list of places - display a list of places with identifiers
#Enter a search term
def user_search(searchterm):
    DBNAME = 'final.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    selectsearchstatement = '''
                SELECT Name,Latitude,Longitude,Rating
                FROM GooglePlaces
                WHERE GooglePlaces.Name = ?
                '''
    searchresult = cur.execute(selectsearchstatement,[searchterm]).fetchall()

    if len(searchresult) > 0:
        print(type(searchresult))
        print(len(searchresult))
        places = []
        for ea in searchresult:
            places.append(GooglePlace(ea[0], ea[1], ea[2], ea[3]))
        # for ea in searchresult:
        #   print(ea[0],ea[1],ea[2],ea[3])
    else:
        print("No results in existing database - New search")
        places = get_place_info(searchterm)
        
        insert_google_data(places,DBNAME)
        
        for ea,val in enumerate(places):
            yelpplaces = get_yelp_info(places[ea].lat,places[ea].lon, places[ea].name)
            photos = get_flickr_photos(places[ea].lat,places[ea].lon, places[ea].name, "Google")

            insert_yelp_data(yelpplaces,DBNAME)
            insert_flickr_data(photos,DBNAME)

    conn.close()
    return places

def generate_userlist():
    #select 10 places form googleplaces to display
    rand_num = []
    placelist = []
    ct = 0
    while ct < 10:
        rand_num.append(random.randint(0,99))
        # rand_num.append(random.randint(0,3))
        ct += 1
    # print(rand_num)

    DBNAME = 'final.db'
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    sql = '''SELECT Name, Latitude, Longitude, Rating
            FROM GooglePlaces'''
    results = cur.execute(sql).fetchall()

    for num in rand_num:
        placelist.append(GooglePlace(results[num][0],results[num][1],results[num][2],results[num][3]))
    
    conn.close()
    return placelist

def user_interface():
    response = ''
    pres = 0
    num = 1
    num2 = 1
    while response != 'exit':
        num = 1
        print('-----------')
        places = generate_userlist()
        for ea in places:
            print("{}. {}".format(num, ea))
            num += 1
        # print(places)
        response = input('Select a place from the list OR enter a name of a place: ')
        if response != 'exit':
            if len(response) <= 2:
                print('-----------')
                print(places[int(response)-1])
                print('Select Display Opton:')
                print(disp_options())
                pres = 1
                presentationchoice = input('What would you like to see? ')
                if int(presentationchoice) == 1:
                    showlist(places[int(response)-1].name)

                elif int(presentationchoice) == 2:
                    # showmap(places[int(response)-1].name, places[int(response)-1].lat, places[int(response)-1].lon)
                    showmap_mapbox(places[int(response)-1].name, places[int(response)-1].lat, places[int(response)-1].lon)
                elif int(presentationchoice) == 3:
                    showratings(places[int(response)-1].name)

                elif int(presentationchoice) == 4:
                    showimage(places[int(response)-1].name,places[int(response)-1].lat, places[int(response)-1].lon)

                elif int(presentationchoice) == 5:
                    continue

                else:
                    print("Unknown Command")

            elif len(response) > 2:
                num2 = 1
                result = user_search(response)
                print('-----------')
                if len(result) > 0:
                    for ea in result:
                        print("{}. {} ({}, {})".format(num2,ea.name,ea.lat,ea.lon))
                        num2 += 1
                    if len(result) > 1:
                        select = input('Select desired place: ')
                        result = result[int(select)-1]
                    else:
                        result = result[0]
                    print('Select Display Opton:')
                    print(disp_options())
                    pres = 1
                    presentationchoice = input('What would you like to see? ')
                    if int(presentationchoice) == 1:
                        showlist(result.name)

                    elif int(presentationchoice) == 2:
                        # showmap(result.name, result.lat, result.lon)
                        showmap_mapbox(result.name, result.lat, result.lon)

                    elif int(presentationchoice) == 3:
                        showratings(result.name)

                    elif int(presentationchoice) == 4:
                        showimage(result.name,result.lat, result.lon)

                    elif int(presentationchoice) == 5:
                        continue
                    
                    else:
                        print("Unknown Command")
                else:
                    print("Unable to find in Google Place Search")



#--------------------------------------------------------------------------------------------
#-----MAIN FUNCTION:
#--------------------------------------------------------------------------------------------

if __name__ == "__main__":
    user_interface()


    # init_db(DBNAME)
    # searchterm = "Yosemite National Park"
    # searchterm = "Lake Tahoe"
    # searchterm = "Michigan League"
    # searchterm = "New Orleans City Park"
    # places = get_place_info(searchterm)
    # yelpplaces = get_yelp_info(places[0].lat,places[0].lon, places[0].name)
    # photos = get_flickr_photos(places[0].lat,places[0].lon, places[0].name, "Google")

    # insert_google_data(places,DBNAME)
    # insert_yelp_data(yelpplaces,DBNAME)
    # insert_flickr_data(photos,DBNAME)

    # user_search("Yosemite National Park")