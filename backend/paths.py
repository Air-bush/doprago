import requests

from structs import *
from init import init_structures

GOLEMIO_APIKEY = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzQ1OCwiaWF0IjoxNzQzMDA5NT"
                  "I0LCJleHAiOjExNzQzMDA5NTI0LCJpc3MiOiJnb2xlbWlvIiwianRpIjoiOTNiOTY0OTEtM"
                  "jY0Yy00M2JkLWEwNTgtMDA0YWQ0ZTMzOGIzIn0.VQ40lUdu09Pfgug8EmkaDkYgNDAlKR21-anL9PJJUmw")


def get_departure_board(request_params):
    request_headers = {
        "X-Access-Token": GOLEMIO_APIKEY
    }
    data = requests.get("https://api.golemio.cz/v2/pid/departureboards", headers=request_headers, params=request_params).json()
    return data


def get_station_departures(node_id):
    request_params = {
        "aswIds": node_id
    }


if __name__ == "__main__":
    params = {
        "aswIds": "1040"
    }
    print(get_departure_board(params))