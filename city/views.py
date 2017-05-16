from django.shortcuts import render
from django.http import JsonResponse
import sys

from city.models import City

# Create your views here.


def suggestions(request):
    query = request.GET.copy()

    cities = City.objects.all()
    if "closeto" in query:
        close_city_name = query["closeto"]
        close_city = City.objects.get(name=close_city_name)
        query["longitude"] = close_city.longitude
        query["latitude"] = close_city.latitude
        del query["closeto"]
        cities.filter(pk=close_city.pk)

    top_cities = sorted(cities, key=lambda x: x.calculate_score(query), reverse=True)
    return build_response(top_cities[:10], "Query Success")


def build_response(cities, message):

    response = {
        "suggestions": [c.dictionary() for c in cities],
        "message": message
    }

    return JsonResponse(response)
