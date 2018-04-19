**SI507 Final Project** <br /> 
**Winter 2018**  <br />
  
**DATA SOURCES USED:**<br />
Google Places API (https://developers.google.com/places/)<br />
Yelp Fusion API (https://www.yelp.com/fusion)<br />
Flickr API (https://www.flickr.com/services/api/flickr.photos.search.html)<br />
Mapbox API (https://www.mapbox.com/api-documentation/)<br />

In order to access data sources, api keys/access tokens are required. Copy and paste these keys/tokens into the file "examplesecrets.py" and rename to "secrets.py"<br />

Requirements.txt contains all needed modules to successfully run final.py<br />

**MAJOR DATA STRUCTURES AND FUNCTIONS:**<br />

The code is organized into sections: <br />
API Keys <br />
    Imported from secrets.py<br />

CACHING & REQUESTING DATA<br />
    All data is cached in the function "make_request_using_cache()", with all cached data in the file, "cache.json"<br />
    
CLASS DEFINITIONS<br />
    GooglePlace (Name, Latitude, Longitude, Rating)<br />
    YelpPlace (Name, Latitude, Longitude, Rating, Review Count, Price, URL)<br />
    FlickrPhoto (Title, Latitude, Longitude, FarmId, ServerId, PhotoId, Secret)<br />
    
INITIALIZE DATABASE<br />
    Database is "final.db", with three tables (GooglePlaces, YelpPlaces, FlickrImages)<br />
    
GATHER DATA FROM SOURCES<br />
    
ADD TO DATABASE<br />
    
RETRIEVE DATA FROM DATABASE<br />
    The functions "getnearby_fromdb()" and "getflickr_fromdb()" make queries to the database to retrieve data for the presentation options. <br />
    
DATA PRESENTATION<br />
    showlist() - Shows list of nearby places to give user option to select Yelp Review page to view in browser<br />
    showmap_mapbox() - Shows map of searched place with nearby places using mapbox with plotly in browser<br />
    showratings() - Shows a bar chart of ratings of nearby places using plotly in browser<br />
    showimage() - Shows the user-selected image in the browser<br />
    
USER INTERFACE<br />
    Handles all user interface functions. <br />


**TO RUN PROGRAM FROM COMMAND LINE:**<br />
Type "python3 final.py"<br />

Program will randomly generate 10 places to get started. You can choose to view one of those places or enter a new search term. After selecting your choice, you will be presented with 4 presentation options:<br />

1. View Yelp Review page of a nearby place of your choice in your browser<br />
2. View a map with the place and several nearby places in your browser<br />
3. View a chart that gives ratings comparisons for several nearby places in your browser<br />
4. View an image that was taken nearby in your browser<br />
