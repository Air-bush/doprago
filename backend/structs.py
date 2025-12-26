TRUE = 1
FALSE = 0
UNDEFINED = -1

class Stop:
    def __init__(self):
        self.location_type: int = 0
        self.parent: Station
        self.gtfs_id: str
        self.id: str
        self.name: str
        self.latitude: str
        self.longitude: str
        self.zones: list[str]
        self.wheelchair_boarding: int = UNDEFINED
        self.platform_code: str
        self.main_traffic_type: str
        self.lines: dict # key: Line, val: Line direction indexes stopping at this stations

class Line:
    def __init__(self):
        self.id: str
        self.short_name: str
        self.long_name: str
        self.type: str
        self.color: str
        self.text_color: str
        self.is_night: bool
        self.is_regional: bool
        self.is_substitute: bool
        self.directions: dict # key: direction_id, val: head_sign/last_stop
        self.stops: dict # key: direction_id, val: list of stops per direction
        self.trips: list

class Station:
    def __init__(self, gtfs_id, node_id, cis, name, lat, lon, main_traffic):
        self.location_type: int = 1
        self.gtfs_id: str = gtfs_id
        self.id: str = node_id
        self.cis: int = cis
        self.name: str = name
        self.latitude: str = lat
        self.longitude: str = lon
        self.main_traffic_type: str = main_traffic
        self.zones: list
        self.lines: list
        self.stops: list
        self.transfers: dict # Key: (fromStop, toStop) Value: minTransferTime

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
        self.stop_times: dict # Key: stopId/stopSequence Value: (ArrivalTime, DepartureTime, X for the not key)
