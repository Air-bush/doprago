from structs import *
import requests

GTFS_LOCATION = "tempFiles/"


def init_stations() -> dict:  # node:object / list
    all_stations = {}  # key: node_id, value: Station
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


def init_lines() -> list:  # TODO: Temporary return type
    all_routes = []
    with open(GTFS_LOCATION + "routes.txt", encoding="UTF-8") as file:
        file.readline()
        routes_data = file.read().split("\n")
    for route_data in routes_data:
        route_data = route_data.split(",")
        route_id = route_data[0]
        short_name = route_data[2] if route_data[2] else None
        long_name = route_data[3] if route_data[3] else None
        route_type = int(routes_data[4])
        color = route_data[6]
        text_color = route_data[7]
        is_night = bool(int(route_data[8]))
        is_regional = bool(int(route_data[9]))
        is_substitute = bool(int(route_data[10]))
        route = Line(route_id, short_name, long_name, route_type, color,
                     text_color, is_night, is_regional, is_substitute)
        directions: dict  # key: direction_id, val: head_sign/last_stop  # TODO: Implement
        stops: dict  # key: direction_id, val: list of stops per direction  # TODO: Implement
        trips: dict  # key: direction_id, val: list of trips per direction  # TODO: Implement
        all_routes.append(route)


if __name__ == "__main__":
    # stations = init_stations()
    pass
