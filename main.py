from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path
import json
import os
import time
from urllib.parse import quote

# Approximate location and area to search. Keep exact personal locations in a
# local .env file, not in a public repository.
latitude = float(os.getenv("FLIGHT_LATITUDE", "38.995165"))
longitude = float(os.getenv("FLIGHT_LONGITUDE", "-76.932392"))
search_radius = float(os.getenv("FLIGHT_RADIUS_NM", "10"))
url = f"https://api.adsb.lol/v2/point/{latitude}/{longitude}/{search_radius}" # url for api

# save files in the same folder as this python script
flight_file = Path(__file__).parent / "flight.json"

# keep checking for nearby aircraft
while True:
    # call api and convert json response into a python dictionary
    try:
        with urlopen(url, timeout=15) as response:
            data = json.load(response)
        # with closes the response automatically
    except (URLError, TimeoutError) as error:
        print("Could not fetch aircraft. Retrying in 30 seconds:", error)
        time.sleep(30)
        continue # skip the rest and try again

    # get aircraft list and reset values for this update
    aircraft = data.get("ac", [])
    num_of_aircraft = len(aircraft)
    airborne = 0
    closest_plane = None # no plane selected yet
    closest_distance = float("inf") # start with infinity so any known distance is closer

    if num_of_aircraft > 0:
        # check each aircraft's altitude and distance
        for plane in aircraft:
            altitude = plane.get("alt_baro", "unknown")
            distance = plane.get("dst", float("inf"))

            # skip aircraft marked as ground or with unknown altitude
            if altitude != "ground" and altitude != "unknown":
                airborne += 1 # increment airborne count

                # save this plane if it is closer than the previous closest
                if distance < closest_distance:
                    closest_distance = distance
                    closest_plane = plane

        # aircraft were found but none passed the airborne check
        if airborne == 0:
            print("No airborne aircraft nearby.")
    else:
        print("No aircraft nearby.")

    # start with no flight so old data doesn't stay on the screen
    flight_data = {"available": False}

    # get details from the closest plane after checking all aircraft
    if closest_plane is not None:
        callsign = closest_plane.get("flight", "unknown").strip() # remove extra spaces
        aircraft_type = closest_plane.get("t", "unknown")
        altitude = closest_plane.get("alt_baro", "unknown")

        print("Flight:", callsign)
        print("Aircraft:", aircraft_type)
        print("Altitude:", altitude, "feet")
        print("Distance:", closest_distance, "nautical miles")

        # default values in case the route lookup fails
        airline = "Unknown airline"
        departure = "?"
        arrival = "?"

        # use callsign to look up airline and route from a separate api
        route_url = f"https://api.adsbdb.com/v0/callsign/{quote(callsign, safe='')}"
        try:
            route_response = urlopen(route_url, timeout=15)
            route_data = json.load(route_response)
            route_response.close()

            # get route details from the nested dictionaries
            route = route_data["response"]["flightroute"]
            airline_data = route.get("airline") or {} # use empty dictionary if airline is missing
            airline = airline_data.get("name", "unknown airline")
            departure = route["origin"]["iata_code"] # departure airport code
            arrival = route["destination"]["iata_code"] # arrival airport code

            print("Airline:", airline)
            print("Route:", departure, "→", arrival)

        # handle an error response from the route api
        except HTTPError as error:
            print("Route unavailable. HTTP status:", error.code)

        # handle connection errors or the request taking too long
        except (URLError, TimeoutError) as error:
            print("Could not fetch route:", error)

        # collect the details for the webpage
        flight_data = {
            "available": True,
            "callsign": callsign,
            "aircraft": aircraft_type,
            "altitude": altitude,
            "distance": closest_distance,
            "airline": airline,
            "departure": departure,
            "arrival": arrival
        }

    # record when this update was saved
    flight_data["updated_at"] = time.time()
    # write a temporary file, then replace the old file
    # this keeps the webpage from reading a half-written file
    temp_file = flight_file.with_suffix(".tmp")
    with temp_file.open("w") as file:
        json.dump(flight_data, file)
    temp_file.replace(flight_file)

    print() # blank line between updates
    time.sleep(30) # wait 30 seconds before checking again
