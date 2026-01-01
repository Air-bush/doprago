POSSIBLE = 1
NOT_POSSIBLE = 0
UNDEFINED = -1


class Stop:
    def __init__(self, parent, gtfs_ids, node_id, alt_name, lat, lon, zones, platform, main_traffic):
        self.location_type: int = 0
        self.parent: Station = parent
        self.gtfs_ids: list[str] = gtfs_ids
        self.id: str = node_id
        self.alternative_name: str = alt_name
        self.latitude: str = lat
        self.longitude: str = lon
        self.zones: list[str] = zones
        self.wheelchair_boarding: int = UNDEFINED
        self.platform_code: str = platform
        self.main_traffic_type: str = main_traffic
        self.lines: dict  # key: Line, val: Line direction indexes stopping at this stations

    def to_string(self) -> str:
        return f"{self.id} ({self.alternative_name}) - {self.platform_code} -> {self.main_traffic_type} ({",".join(self.zones)})"

class Line:
    TRAM = 0
    METRO = 1
    RAIL = 2
    BUS = 3
    FERRY = 4
    FUNICULAR = 7
    TROLLEYBUS = 11

    def __init__(self, gtfs_id, s_name, l_name, traffic_type, color, text_color, is_night, is_reg, is_sub):
        self.id: str = gtfs_id
        self.short_name: str = s_name
        self.long_name: str = l_name
        self.type: int = traffic_type
        self.color: str = color
        self.text_color: str = text_color
        self.is_night: bool = is_night
        self.is_regional: bool = is_reg
        self.is_substitute: bool = is_sub
        self.directions: dict  # key: direction_id, val: head_sign/last_stop
        self.stops: dict = {}  # key: direction_id, val: list of stops per direction
        self.trips: dict  # key: direction_id, val: list of trips per direction


class Station:
    def __init__(self, gtfs_id, node_id, cis, name, lat, lon, main_traffic):
        self.location_type: int = 1
        self.gtfs_id: str = gtfs_id
        self.id: int = node_id
        self.cis: int = cis
        self.name: str = name
        self.latitude: str = lat
        self.longitude: str = lon
        self.main_traffic_type: str = main_traffic
        self.zones: list = []
        self.lines: list
        self.stops: list = []
        self.transfers: dict  # Key: (fromStop, toStop) Value: minTransferTime

    def to_string(self) -> str:
        station_string = f"{self.id} ({self.name}) -> {self.main_traffic_type}; Zones: {",".join(self.zones)}\n"
        stops_string = ""
        for stop in self.stops:
            stops_string += f"\t{stop.to_string()}\n"
        return station_string + stops_string


class Trip:
    def __init__(self):
        self.id: str
        self.service_id: str
        self.route_id: str
        self.direction_id: int
        self.headsign: str
        self.wheelchair_accessible: int = UNDEFINED
        self.bikes_allowed: int = UNDEFINED
        self.exceptional: bool
        self.stop_times: dict  # Key: stopId/stopSequence Value: (ArrivalTime, DepartureTime, X for the not key)
