import math

class Location:
	def __init__(self, latitude, longitude):
		self.latitude = latitude
		self.longitude = longitude

	def __eq__(self, other):
		return self.latitude == other.latitude and self.longitude == other.longitude

	@staticmethod
	def distanceBetween(lat1, long1, lat2, long2):
		# Use the Haversine formula: https://en.wikipedia.org/wiki/Haversine_formula
		(lat1Rad, long1Rad) = (lat1 * math.pi / 180, long1 * math.pi / 180)
		(lat2Rad, long2Rad) = (lat2 * math.pi / 180, long2 * math.pi / 180)

		term1 = math.sin(0.5*(lat1Rad - lat2Rad)) ** 2
		term2 = math.cos(lat1Rad) * math.cos(lat2Rad) * (math.sin(0.5*(long1Rad - long2Rad))**2)
		centralAngle = 2 * math.asin(math.sqrt(term1 + term2))
		distKm = centralAngle * 6371.009 # in km
		return distKm

