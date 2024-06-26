from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from datetime import datetime
import requests

# Create your views here.
def home(request):
    return HttpResponse("Hello World!")

def events(request):
    country = request.GET.get('country')  # Get user query from URL parameter
    genre = request.GET.get('genre')
    startDate = request.GET.get('startDate')
    endDate = request.GET.get('endDate')
    print("query and request is", request.GET.get('country'), genre, startDate, endDate)
    api_url="https://app.ticketmaster.com/discovery/v2/events.json"
    param1_name="apikey"
    param1_value= "rEAPENhGBiaW6jrS290UfWgSzKgk7zx9"
    param2_name="city" 
    param2_value="london"
    data=fetch_data(api_url, param1_name, param1_value, param2_name, param2_value)  # Fetch all events
    # print(data['_embedded'])
    # if query:
    #     events = events.filter(title__icontains=query) | events.filter(description__icontains=query)
    # context = {'events': events, 'query': query}  # Pass events and query to template
    # return render(request, 'events.html', context)
    if(country):
        filtered_objects_by_country = []
        for item in data['_embedded'].get('events'):
            # print("************************************")
            for venue in item['_embedded'].get('venues'):
                print(venue['country'].get('name'))
                if(country.lower() in venue['country'].get('name').lower()):
                    filtered_objects_by_country.append(item)
        print("************************************", len(filtered_objects_by_country))
    
    if(genre):
        filtered_objects_by_genre = []
        for item in data['_embedded'].get('events'):
            # print("************************************")
            for genr in item['classifications']:
                print(genr['genre'].get('name'))
                if(genre.lower() in genr['genre'].get('name').lower()):
                    filtered_objects_by_genre.append(item)
        print("************************************", len(filtered_objects_by_genre))

    if(startDate and endDate):
        filtered_objects_by_date = []
        for item in data['_embedded'].get('events'):
            print("************************************")
            is_after = compare_dates(item['sales']['public']['startDateTime'], startDate)
            if is_after:
                print("The start date in 'date_str' is after 'date_to_compare'.")
                print("Let's check for end date!")
                is_endDate_after = compare_dates(item['sales']['public']['endDateTime'], endDate)
                if is_endDate_after:
                    print("The end date in 'date_str' is after 'date_to_compare'.")
                else:
                    print("The end date in 'date_str' is not after 'date_to_compare'.")
                    filtered_objects_by_date.append(item)
            else:
                print("The start date in 'date_str' is not after 'date_to_compare'.")
        print("************************************", len(filtered_objects_by_date))

    common_objects = find_common_objects(filtered_objects_by_country, filtered_objects_by_genre, filtered_objects_by_date)
    print("########################################", len(common_objects))
    if(len(common_objects)>=1):
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        return JsonResponse({'events':common_objects})
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

    # params = {param1_name: param1_value, param2_name: param2_value}
    params = {param1_name: param1_value}
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return response.json()  # Assuming the API returns JSON data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None


def compare_dates(date_str, date_to_compare):
  """
  Compares a date in format "YYYY-MM-DDTHH:MM:SSZ" with another date.

  Args:
    date_str: The date string in ISO 8601 format (e.g., "2023-12-11T16:00:00Z").
    date_to_compare: The date object or string to compare with (e.g., "2023-12-09").

  Returns:
    True if the date in 'date_str' is after 'date_to_compare', False otherwise.
  """

  # Parse the date string
  date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")

  # Handle potential exceptions during parsing (optional)
  try:
    # Convert date_to_compare to datetime if it's a string
    if isinstance(date_to_compare, str):
      date_to_compare = datetime.strptime(date_to_compare, "%Y-%m-%d")
  except ValueError:
    print("Invalid date format for date_to_compare.")
    return False

  # Compare the dates
  return date_obj >= date_to_compare

def find_common_objects(array1, array2, array3):
    """
      Finds the common objects present in all three input arrays based on unique identifiers.

      Args:
        array1: A list of dictionaries (assumed to have a unique 'id' key).
        array2: A list of dictionaries (assumed to have a unique 'id' key).
        array3: A list of dictionaries (assumed to have a unique 'id' key).

      Returns:
        A list containing the common objects found in all three arrays based on their unique identifiers.
    """
    common_ids = set(obj['id'] for obj in array1)  # Extract unique IDs from array1
    # Iterate through remaining arrays and keep only objects with IDs in common_ids
    for arr in (array2, array3):
      common_ids = common_ids.intersection(set(obj['id'] for obj in arr))
    # Recreate the common objects list based on IDs (optional)
    common_objects = [obj for obj in array1 if obj['id'] in common_ids]
    return common_objects