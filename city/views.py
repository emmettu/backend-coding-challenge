from django.shortcuts import render
from django.http import JsonResponse

from city.models import City

# Create your views here.


def suggestions(request):
    query = request.GET

    cities = City.objects.all()

    top_cities = sorted(cities, key=lambda x: x.calculate_score(query), reverse=True)
    return build_response(top_cities[:10], "Query Success")


def build_response(cities, message):

    response = {
        "suggestions": [c.dictionary() for c in cities],
        "message": message
    }

    return JsonResponse(response)
