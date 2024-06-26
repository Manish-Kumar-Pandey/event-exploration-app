from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
import requests

# Create your views here.
def home(request):
    return HttpResponse("Hello World!")

def events(request):
    query = request.GET.get('query')  # Get user query from URL parameter
    api_url="https://app.ticketmaster.com/discovery/v2/events.json"
    param1_name="apikey"
    param1_value= "rEAPENhGBiaW6jrS290UfWgSzKgk7zx9"
    param2_name="city" 
    param2_value="london"
    data=fetch_data(api_url, param1_name, param1_value, param2_name, param2_value)  # Fetch all events
    print(data['_embedded'])
    # if query:
    #     events = events.filter(title__icontains=query) | events.filter(description__icontains=query)
    # context = {'events': events, 'query': query}  # Pass events and query to template
    # return render(request, 'events.html', context)
    return JsonResponse(data['_embedded'])


def fetch_data(api_url, param1_name, param1_value, param2_name, param2_value):
    """Fetches data from a third-party API with two query string parameters.    
    Args:
      api_url: The base URL of the API endpoint.
      param1_name: The name of the first query string parameter.
      param1_value: The value of the first query string parameter.
      param2_name: The name of the second query string parameter.
      param2_value: The value of the second query string parameter. 
    Returns:
      A dictionary containing the API response data or None if an error occurs.
    """

#   params = {param1_name: param1_value, param2_name: param2_value}
    params = {param1_name: param1_value}
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return response.json()  # Assuming the API returns JSON data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None