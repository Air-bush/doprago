from structs import *
import requests


def init_stations() -> dict:  # node:object / list
    all_stations = {}
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
        station_lines: list  # TODO: Implement
        stops: list[Stop] = []
        for stop in raw_station["stops"]:
            stops.append(init_stop(stop, station))
        station.stops = stops
        station_zones = []
        for stop in stops:
            for zone in stop.zones:
                if zone not in station_zones:
                    station_zones.append(zone)
        station.zones = station_zones
        transfers: dict  # Key: (fromStop, toStop) Value: minTransferTime TODO: Implement
        all_stations[node_id] = station
    return all_stations


def init_stop(stop_data: dict, parent_station: Station) -> Stop:
    parent = parent_station
    gtfs_ids = stop_data["gtfsIds"]
    node_id = stop_data["id"]
    name = stop_data["altIdosName"]
    latitude = stop_data["lat"]
    longitude = stop_data["lon"]
    zones = stop_data["zone"].split(",")
    platform_code = stop_data.get("platform", UNDEFINED)
    main_traffic_type = stop_data["mainTrafficType"]
    stop = Stop(parent, gtfs_ids, node_id, name, latitude, longitude, zones, platform_code, main_traffic_type)
    wheelchair = stop_data["wheelchairAccess"]
    if wheelchair == "possible":
        stop.wheelchair_boarding = POSSIBLE
    elif wheelchair == "notPossible":
        stop.wheelchair_boarding = NOT_POSSIBLE
    lines: dict  # key: Line, val: Line direction indexes stopping at this stations TODO: implement
    return stop


if __name__ == "__main__":
    stations = init_stations()
