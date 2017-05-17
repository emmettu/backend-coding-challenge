"""Handles the rendering displaying of routes to the user.
"""
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import sys

from city.models import City


def suggestions(request):
    """Handles the /suggestion/ route.

    Given a suggestion, gets the query results and loads the
    City objects into memory.

    Populates the latitude and longitude values with those of
    the city specified in closeto (if the user provided that param)

    Gets the top cities, and returns the json response.
    """
    try:
        query = request.GET.copy()
        cities = City.objects.all()
        n_results = get_number_of_results(query)


        if "closeto" in query:
            close_city = handle_closeto(query, cities)
            cities = cities.exclude(name__iexact=query.pop("closeto")[0])

        top_cities = get_top_cities(cities, query)

        return build_response(top_cities[:n_results], "Query Success")

    except Exception as e:
        return build_response([], str(e))


def get_number_of_results(query):
    """Determines the number of results to return to the viewer

    Given a query, checks for the 'n' param and returns it if
    valid, else it returns a default of 10.
    """
    try:
        return int(query.pop("n")[0]) if "n" in query else 10
    except:
        raise Exception("Invalid n parameter")


def handle_closeto(query, cities):
    """Adjust the queries lon and lat values based on the closeto param.

    Given a query and list of cities, finds the closeto city, and sets
    the lat and lon params of the query to be that of the closeto city.
    The closeto city is removed from cities to prevent it from showing
    up in the returned json.
    """
    close_city_name = query["closeto"]
    close_city = City.objects.filter(name__iexact=close_city_name).first()
    query["longitude"] = close_city.longitude
    query["latitude"] = close_city.latitude
    return cities

def get_top_cities(cities, query):
    """Sort top cities by their scores and return them.
    """
    return sorted(cities, key=lambda x: x.calculate_score(query), reverse=True)

def build_response(cities, message):
    """Generate the JSON response.
    """
    response = {
        "suggestions": [c.dictionary() for c in cities],
        "message": message
    }

    return JsonResponse(response, json_dumps_params={"indent": 2})


def home(request):
    """Render the home page.
    """
    return HttpResponse(render(request, 'city/index.html', {}))
