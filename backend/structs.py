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
        self.lines: dict = {}  # key: Line, val: Line direction indexes stopping at this station/->list of terminus stations<-

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
        self.directions: list = []  # key: direction_id, val: head_sign/last_stop TODO: For now just list of terminus stations
        self.stops: dict = {}  # key: direction_id, val: list of stops per direction
        self.trips: dict = {}  # key: direction_id, val: list of trips per direction


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
        self.lines: list = []
        self.stops: dict = {}  # Key: /id Val: Stop
        self.transfers: dict  # Key: (fromStop, toStop) Value: minTransferTime

    def to_string(self) -> str:
        station_string = f"{self.id} ({self.name}) -> {self.main_traffic_type}; Zones: {",".join(self.zones)}\n"
        stops_string = ""
        for stop in self.stops.values():
            stops_string += f"\t{stop.to_string()}\n"
        return station_string + stops_string


class Trip:
    METRO_A = "Ma"
    METRO_B = "Mb"
    METRO_C = "Mc"
    METRO_D = "Md"
    TRAIN = "Ra"
    ESKO = "Sb"
    FUNICULAR = "Fu"
    BOAT = "Fe"
    AIRPLANE = "Ap"
    TRAM = "Tw"
    TROLLEY_BUS = "Tb"
    BUS = "Bu"

    def __init__(self, trip_id, service, parent_line, direction_id, head_sign, chairs = UNDEFINED, bikes = UNDEFINED, exceptional = False):
        self.id: str = trip_id
        self.service: ServiceSchedule = service
        self.parent_line: Line = parent_line
        self.direction_id: int = direction_id
        self.headsign: str = head_sign
        self.wheelchair_accessible: int = chairs
        self.bikes_allowed: int = bikes
        self.exceptional: bool = exceptional
        self.stops: list = []  # Value:{Stop, ArrivalTime, DepartureTime} TimeFormat: Hour:Min:Sec
        self.icons_stop: list[str]
        self.icons_line: list[str]


class ServiceSchedule:
    ADDED = 1
    REMOVED = 2
    def __init__(self, service_id, start, end):
        self.service_id: str = service_id  # 1st 7 digits => weekdays of operation
        self.mon: bool = True if self.service_id[0] == "1" else False
        self.tue: bool = True if self.service_id[1] == "1" else False
        self.wed: bool = True if self.service_id[2] == "1" else False
        self.thu: bool = True if self.service_id[3] == "1" else False
        self.fri: bool = True if self.service_id[4] == "1" else False
        self.sat: bool = True if self.service_id[5] == "1" else False
        self.sun: bool = True if self.service_id[6] == "1" else False
        self.start_date: str = start  # Year-4Dig Month-2Dig Day-2Dig
        self.end_date: str = end
        self.exceptions: dict[str, int] = {}  # Key: exception date, Val: 1/2 (service added/service removed)

# Trips -> sorted by direction ids and then by dates for easier access -> dict { direction_id: { mon:[], tue:[]}
# Implement searching algorithm of halfing previous list part for faster services_now finding -> LIST MUST BE SORTED BY DEPARTURE TIME