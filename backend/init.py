from structs import *
import requests
import json

def init_stations(lines) -> list:
    stations = []
    response = requests.get("https://data.pid.cz/stops/json/stops.json")
    raw_stations = response.json()["stopGroups"]
    for raw_station in raw_stations:
        node_id = raw_station["node"]
        gtfs_id = f"U{node_id}"
        cis = int(raw_station["cis"])
        name = raw_station["name"]
        latitude = raw_station["avgLat"]
        longitude = raw_station["avgLon"]
        main_traffic_type = raw_station["mainTrafficType"]
        station = Station(gtfs_id, node_id, cis, name, latitude, longitude, main_traffic_type)
        station_zones: list
        station_lines: list
        stops: list
        transfers: dict  # Key: (fromStop, toStop) Value: minTransferTime
    return stations

def init_stops(station: Station, station_data: dict):
    pass


if __name__ == "__main__":
    init_stations()