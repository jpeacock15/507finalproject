SI507 Final Project
Winter 2018

DATA SOURCES USED:
Google Places API (https://developers.google.com/places/)
Yelp Fusion API (https://www.yelp.com/fusion)
Flickr API (https://www.flickr.com/services/api/flickr.photos.search.html)
Mapbox API (https://www.mapbox.com/api-documentation/)

In order to access data sources, api keys/access tokens are required. Copy and paste these keys/tokens into the file "examplesecrets.py" and rename to "secrets.py"

Requirements.txt contains all needed modules to successfully run final.py

MAJOR DATA STRUCTURES AND FUNCTIONS:

The code is organized into sections: 
	API Keys 
		Imported from secrets.py
	CACHING & REQUESTING DATA
		All data is cached in the function "make_request_using_cache()", with all cached data in the file, "cache.json"
	CLASS DEFINITIONS
		GooglePlace (Name, Latitude, Longitude, Rating)
		YelpPlace (Name, Latitude, Longitude, Rating, Review Count, Price, URL)
		FlickrPhoto (Title, Latitude, Longitude, FarmId, ServerId, PhotoId, Secret)
	INITIALIZE DATABASE
		Database is "final.db", with three tables (GooglePlaces, YelpPlaces, FlickrImages)
	GATHER DATA FROM SOURCES
	ADD TO DATABASE
	RETRIEVE DATA FROM DATABASE
		The functions "getnearby_fromdb()" and "getflickr_fromdb()" make queries to the database to retrieve data for the presentation options. 
	DATA PRESENTATION
		showlist() - Shows list of nearby places to give user option to select Yelp Review page to view in browser
		showmap_mapbox() - Shows map of searched place with nearby places using mapbox with plotly in browser
		showratings() - Shows a bar chart of ratings of nearby places using plotly in browser
		showimage() - Shows the user-selected image in the browser
	USER INTERFACE
		Handles all user interface functions. 


TO RUN PROGRAM FROM COMMAND LINE:
Type "python3 final.py"

Program will randomly generate 10 places to get started. You can choose to view one of those places or enter a new search term. After selecting your choice, you will be presented with 4 presentation options: 
	1. View Yelp Review page of a nearby place of your choice in your browser
	2. View a map with the place and several nearby places in your browser
	3. View a chart that gives ratings comparisons for several nearby places in your browser
	4. View an image that was taken nearby in your browser
