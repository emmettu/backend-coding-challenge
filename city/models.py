from django.db import models
import csv
import sys
import math
import json
from difflib import SequenceMatcher

# Create your models here.
class ScoreCalculator:
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
        total_score = 0
        for k in self.query.keys():
            total_score += self.score_map[k]()

        return total_score / len(self.query)

    def score_population(self):
        desired_pop = int(self.query["population"])
        city_pop = self.city.population
        return 1 / (math.log(abs(city_pop - desired_pop) + 1) + 1)

    def score_latitude(self):
        desired_lat = float(self.query["latitude"])
        city_lat = self.city.latitude
        return 1 / (math.log(abs(city_lat - desired_lat) + 1) + 1)

    def score_longitude(self):
        desired_lon = float(self.query["longitude"])
        city_lon = self.city.longitude
        return 1 / (math.sqrt(abs(city_lon - desired_lon)) + 1)

    def score_name(self):
        desired_name = self.query["q"]
        city_name = self.city.name
        return SequenceMatcher(None, desired_name, city_name).ratio()


class City(models.Model):
    name = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    population = models.IntegerField()

    def calculate_score(self, query):
        return ScoreCalculator(self, query).calculate_score()

    def dictionary(self):
        return {
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "population": self.population
        }

def load_data():
    csv.field_size_limit(sys.maxsize)
    with open("./data/cities_canada-usa.tsv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        next(f)

        cities = []
        for row in reader:
            cities.append(build_city(row))

        City.objects.bulk_create(cities)


def build_city(row):
    _, _, name, _, lat, lon, _, _, _, _, _, _, _, _, pop, _, _, _, _ = row

    city = City(
        name=name,
        latitude=float(lat),
        longitude=float(lon),
        population=int(pop),
    )
    return city
