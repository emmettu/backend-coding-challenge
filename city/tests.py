from django.test import TestCase, Client
import json
import sys

from .models import load_data, City


class LoadDataTest(TestCase):

    def test_load_data(self):
        load_data()
        cities = City.objects.all()
        self.assertEqual(len(cities), 5339)
        city = cities[0]
        self.assertEqual(city.name, "Abbotsford")
        self.assertEqual(city.latitude, 49.05798)
        self.assertEqual(city.longitude, -122.25257)
        self.assertEqual(city.population, 151683)


class SortTest(TestCase):

    def setUp(self):
        City(
            name="city1",
            population=100,
            latitude=20,
            longitude=20
        ).save()

        City(
            name="city2",
            population=200,
            latitude=40,
            longitude=40
        ).save()

        City(
            name="city3",
            population=300,
            latitude=80,
            longitude=80
        ).save()

    def test_population(self):
        self.assertCity("/suggestions/?population=200", "city2")

    def test_latitude(self):
        self.assertCity("/suggestions/?latitude=80", "city3")

    def test_longitude(self):
        self.assertCity("/suggestions/?latitude=40", "city2")

    def test_name(self):
        self.assertCity("/suggestions/?q=c1", "city1")
        self.assertCity("/suggestions/?q=c2", "city2")

    def test_multiple(self):
        self.assertCity("/suggestions/?q=c3&population=290&latitude=60", "city3")

    def test_closeto(self):
        self.assertCity("/suggestions/?closeto=city1", "city2")
        self.assertCity("/suggestions/?closeto=city3", "city2")

    def test_result_number(self):
        for i in range(10):
            City(
                name=str(i),
                population=1,
                latitude=1,
                longitude=1
            ).save()
        cities, _ = self.get_cities("/suggestions/?q=test")
        self.assertEqual(len(cities), 10)

        cities, _ = self.get_cities("/suggestions/?q=test&n=12")
        self.assertEqual(len(cities), 12)

    def test_message(self):
        cities, message = self.get_cities("/suggestions/?q=test&n=12")
        self.assertEquals(message, "Query Success")

        cities, message = self.get_cities("/suggestions/?population=fail")
        self.assertNotEquals(message, "Query Success")

        cities, message = self.get_cities("/suggestions/?population=10&fail=True")
        self.assertNotEquals(message, "Query Success")

    def assertCity(self, query, city_name):
        cities, _ = self.get_cities(query)
        self.assertEqual(cities[0]["name"], city_name, cities)

    def get_cities(self, query):
        client = Client()
        response = client.get(query)
        json_data = json.loads(response.content)
        return json_data["suggestions"], json_data["message"]
