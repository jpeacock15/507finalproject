#You must create at least 3 test cases and use at least 15 assertions or calls to ‘fail( )’. 
#Your tests should show that you are able: 
	#to access data from all of your sources 
	#that your database is correctly constructed and can satisfy queries that are necessary for your program
	#that your data processing produces the results and data structures you need for presentation

import unittest
from final import *

class TestDatabase(unittest.TestCase):
	
	def test_googleplaces(self):
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		sql = '''SELECT Name
				 FROM GooglePlaces'''
		results = cur.execute(sql)
		result_list = results.fetchall()
		self.assertIn(('Yosemite National Park',),result_list)
		self.assertGreater(len(result_list), 100)

		sql = '''SELECT Name,Latitude,Longitude
				  FROM GooglePlaces
				  WHERE Name = "Michigan League"
				  '''
		results = cur.execute(sql)
		result_list = results.fetchall()

		self.assertEqual(result_list[0][1], 42.2790304)
		self.assertEqual(result_list[0][2], -83.7376361)

		conn.close()

	def test_yelpplace(self):
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		sql = '''SELECT SearchName,Name,Latitude,Longitude,Rating
				FROM YelpPlaces
				WHERE SearchName = "Michigan League"
				ORDER BY Rating DESC
				'''
		results = cur.execute(sql)
		result_list = results.fetchall()

		self.assertEqual(len(result_list),20)
		self.assertEqual(result_list[0][4], 4.5)

		sql = '''SELECT Latitude,Longitude
				FROM YelpPlaces
				WHERE Name = "Frita Batidos" AND SearchId = 3
				'''
		results = cur.execute(sql)
		result_list = results.fetchall()

		self.assertEqual(len(result_list),1)
		self.assertEqual(result_list[0][0], 42.2803651)
		self.assertEqual(result_list[0][1], -83.7491532)

		conn.close()

	def test_flickr(self):
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()

		sql = '''SELECT SearchName, Title, URL
				FROM FlickrImages
				'''
		results = cur.execute(sql)
		result_list = results.fetchall()

		self.assertEqual(result_list[0][2][:5],"https")
		self.assertEqual(result_list[0][2][-3:],"jpg")

		sql = '''SELECT SearchName,Title
				FROM FlickrImages
				WHERE SearchId = 3
				'''
		results = cur.execute(sql)
		result_list = results.fetchall()

		self.assertEqual(result_list[0][0], "Michigan League")
		self.assertGreater(len(result_list), 200)

		conn.close()

class TestAccess(unittest.TestCase):
	
	def test_googlequery(self): 
		searchterm = "Yosemite National Park"
		q1 = get_place_info(searchterm) #returns list of GooglePlace instances
		self.assertIs(type(q1),list)
		self.assertEqual(q1[0].name,searchterm)


	def test_yelpquery(self):
		searchterm = "Yosemite National Park"
		lat = 37.8651011
		lon = -119.5383294
		q3 = get_yelp_info(lat,lon,searchterm) #returns list of YelpPlace instances

		self.assertIs(type(q3),list)
		self.assertEqual(q3[1].searchterm,searchterm)
		self.assertIsInstance(q3[1],YelpPlace)
		

	def test_flickrquery(self):
		searchterm = "Yosemite National Park"
		lat = 37.8651011
		lon = -119.5383294
		request = "Google"
		q5 = get_flickr_photos(lat,lon, searchterm, request) #returns list of FlickrPhoto instances
		
		self.assertIsInstance(q5[0], FlickrPhoto)
		self.assertEqual(q5[0].lat, lat)
		

class TestPresentationStructure(unittest.TestCase):
	
	def test_map(self):
		try:
			searchterm = "Yosemite National Park"
			lat = 37.8651011
			lon = -119.5383294
			showmap_mapbox(searchterm, lat, lon)
		except:
			self.fail()

	def test_ratingschart(self):
		try:
			searchterm = "Yosemite National Park"
			showratings(searchterm)
		except:
			self.fail()

	def test_nearbyplace(self):
		try:
			searchterm = "Yosemite National Park"
			showlist(searchterm)
		except:
			self.fail()




unittest.main()