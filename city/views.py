from django.shortcuts import render
from django.http import JsonResponse
import sys

from city.models import City


def suggestions(request):
    try:
        query = request.GET.copy()
        cities = City.objects.all()
        n_results = get_number_of_results(query)

        handle_closeto(query, cities)

        top_cities = get_top_cities(cities, query)

        return build_response(top_cities[:n_results], "Query Success")

    except Exception as e:
        return build_response([], str(e))


def get_number_of_results(query):
    try:
        n = 10 if "n" not in query else int(query["n"])
        del query["n"]
        return n
    except:
        raise Exception("Invalid n parameter: " + query["n"])


def handle_closeto(query, cities):
    if "closeto" in query:
        close_city_name = query["closeto"]
        close_city = City.objects.get(name=close_city_name)
        query["longitude"] = close_city.longitude
        query["latitude"] = close_city.latitude
        del query["closeto"]
        cities.filter(pk=close_city.pk)

def get_top_cities(cities, query):
    return sorted(cities, key=lambda x: x.calculate_score(query), reverse=True)

def build_response(cities, message):

    response = {
        "suggestions": [c.dictionary() for c in cities],
        "message": message
    }

    return JsonResponse(response)
