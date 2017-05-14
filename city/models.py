from django.db import models
import csv
import sys

# Create your models here.

class City(models.Model):
    name = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    population = models.IntegerField()


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
