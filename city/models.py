"""Classes related to the City model

This module contains the ScoreCalculator and City classes.
"""
from django.db import models
import csv
import sys
import math
import json
from difflib import SequenceMatcher


class ScoreCalculator:
    """Calculates the score between an object and a query

    This class is initialized with a querystring dictionary
    and a city to be matched against. The calculate_score method
    determines a score from (0 to 1) based on how closely the
    city matches the query dictionary
    """
    def __init__(self, city, query):

        self.score_map = {
            "population": self.score_population,
            "latitude": self.score_latitude,
            "longitude": self.score_longitude,
            "q": self.score_name
        }

        self.query = query
        self.city = city

    def calculate_score(self):
        """Calculate the (0-1) score of the city agianst the query
        for each key in the query.

        The score is calculated by looking up the score function for
        the key in the score map, and running it, adding the result to
        total_score. total_score is then divided by the number of keys
        to produce an average score which is then returned.
        """
        total_score = 0
        for k in self.query.keys():
            total_score += self.score_map[k]()

        return total_score / len(self.query)

    def score_population(self):
        """Normalized diff of the query and city populations.
        """
        desired_pop = int(self.query["population"])
        city_pop = self.city.population
        return self.normalized_diff(desired_pop, city_pop, City.MAX_POP, City.MIN_POP)

    def score_latitude(self):
        """Normalized diff of the query and city latitudes.
        """
        desired_lat = float(self.query["latitude"])
        city_lat = self.city.latitude
        return self.normalized_diff(desired_lat, city_lat, City.MAX_LAT, City.MIN_LAT)

    def score_longitude(self):
        """Normalized diff of the query and city longitudes.
        """
        desired_lon = float(self.query["longitude"])
        city_lon = self.city.longitude
        return self.normalized_diff(desired_lon, city_lon, City.MAX_LON, City.MIN_LON)

    def score_name(self):
        """[0-1] difference of the query and city names.

        SequenceMatcher.ratio() is used to generate a [0-1] difference
        between the 'q' parameter and the city name.
        """
        desired_name = self.query["q"]
        city_name = self.city.name
        return  SequenceMatcher(None, desired_name, city_name).ratio()

    def normalized_diff(self, true, desired, maximum, minimum):
        """Calculate the difference between two values between 0 and 1.

        Given two values, and their minimums and maximums, normalize the
        values between 0 and 1 and then take the difference between them.
        return 1 minus the difference in the values
        """
        adjusted_true = self.normalize(true, maximum, minimum)
        adjusted_desired = self.normalize(desired, maximum, minimum)
        diff = abs(adjusted_true - adjusted_desired)
        return 1 - diff

    def normalize(self, value, maximum, minimum):
        """Normalize a given value between 0 and 1
        Given a value and the known min and max values, place it
        between 0 and 1 inclusively.
        """
        return (value - minimum) / (maximum - minimum)


class City(models.Model):
    """Model representation of a city.

    Stores a cities name, latitude, longitude, and population.
    Stores the maximum and minimum values of these parameters.

    Provides methods for working with cities, such as calculating
    scores and returning the dictionary representation.
    """
    MAX_POP = 0
    MIN_POP = 0
    MAX_LAT = 0
    MIN_LAT = 0
    MAX_LON = 0
    MIN_LON = 0

    name = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    population = models.IntegerField()

    def calculate_score(self, query):
        """Uses ScoreCalculator class to calculate a score given a query
        """
        self.score = ScoreCalculator(self, query).calculate_score()
        return self.score

    def dictionary(self):
        """Returns the dictionary representation of the city.
        """
        return {
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "population": self.population,
            "score": "{0:.2f}".format(self.score)
        }


def load_data():
    """Loads cities_canada-usa.tsv into the database.
    """
    csv.field_size_limit(sys.maxsize)
    with open("./data/cities_canada-usa.tsv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        next(f)

        cities = []
        for row in reader:
            cities.append(build_city(row))

        City.objects.bulk_create(cities)

    set_max_min()


def build_city(row):
    """Given a tsv row, builds the corresponding City object.
    """
    _, _, name, _, lat, lon, _, _, _, _, _, _, _, _, pop, _, _, _, _ = row

    city = City(
        name=name,
        latitude=float(lat),
        longitude=float(lon),
        population=int(pop),
    )
    return city


def set_max_min():
    """Sets the minimum and maximum values for the different query params.
    """
    cities = City.objects.all()
    City.MAX_LON = cities.latest("longitude").longitude
    City.MIN_LON = cities.earliest("longitude").longitude
    City.MAX_LAT = cities.latest("latitude").latitude
    City.MIN_LAT = cities.earliest("latitude").latitude
    City.MAX_POP = cities.latest("population").population
    City.MIN_POP = cities.earliest("population").population
