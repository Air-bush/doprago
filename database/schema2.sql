CREATE TABLE agency (
    agency_id           VARCHAR(255) PRIMARY KEY,
    agency_name         VARCHAR(255) NOT NULL,
    agency_url          VARCHAR(255) NOT NULL,
    agency_timezone     VARCHAR(255) NOT NULL,
    agency_lang         VARCHAR(255),
    agency_phone        VARCHAR(255)
);

CREATE TABLE calendar (
    service_id          VARCHAR(255) PRIMARY KEY,
    monday              BOOLEAN NOT NULL,
    tuesday             BOOLEAN NOT NULL,
    wednesday           BOOLEAN NOT NULL,
    thursday            BOOLEAN NOT NULL,
    friday              BOOLEAN NOT NULL,
    saturday            BOOLEAN NOT NULL,
    sunday              BOOLEAN NOT NULL,
    start_date          DATE NOT NULL,
    end_date            DATE NOT NULL
);

CREATE TABLE calendar_dates (
    service_id          VARCHAR(255) PRIMARY KEY REFERENCES calendar(service_id),
    date                DATE NOT NULL,
    exception_type      SMALLINT NOT NULL CHECK (exception_type IN (1,2)),
);

CREATE TABLE feed_info (
    feed_publisher_name VARCHAR(255) NOT NULL,
    feed_publisher_url  VARCHAR(255) NOT NULL,
    feed_lang           VARCHAR(255) NOT NULL,
    feed_start_date     DATE,
    feed_end_date       DATE,
    feed_contact_email  VARCHAR(255)
);

CREATE TABLE levels (
    level_id            VARCHAR(255) PRIMARY KEY,
    level_index         DOUBLE PRECISION NOT NULL,
    level_name          VARCHAR(255)
);

CREATE TABLE stops (
    stop_id             VARCHAR(255) PRIMARY KEY,
    stop_name           VARCHAR(255),
    stop_lat            DOUBLE PRECISION NOT NULL,
    stop_lon            DOUBLE PRECISION NOT NULL,
    zone_id             VARCHAR(255),
    stop_url            VARCHAR(255),
    location_type       SMALLINT CHECK (location_type IN (0,1,2,3,4)),
    parent_station      VARCHAR(255) REFERENCES stops(stop_id),
    wheelchair_boarding SMALLINT CHECK (wheelchair_boarding IN (0,1,2)),
    level_id            VARCHAR(255) REFERENCES levels(level_id),
    platform_code       VARCHAR(255),
    asw_node_id         VARCHAR(255),
    asw_stop_id         VARCHAR(255),
    zone_region_type    VARCHAR(255)
);

CREATE TABLE routes (
    route_id            VARCHAR(255) PRIMARY KEY,
    agency_id           VARCHAR(255) REFERENCES agency(agency_id),
    route_short_name    VARCHAR(255),
    route_long_name     VARCHAR(255),
    route_type          SMALLINT NOT NULL CHECK (route_type IN (0,1,2,3,4,5,6,7,11,12)),
    route_url           VARCHAR(255),
    route_color         CHAR(6),
    route_text_color    CHAR(6),
    is_night            BOOLEAN DEFAULT FALSE,
    is_regional         BOOLEAN DEFAULT FALSE,
    is_substitute_transport BOOLEAN DEFAULT FALSE
);

-- Possiblility of merging sub_agencies into route_sub_agencies
CREATE TABLE sub_agencies (
    sub_agency_id       VARCHAR(255) PRIMARY KEY,
    sub_agency_name     VARCHAR(255),
);

CREATE TABLE route_sub_agencies (
    route_id            VARCHAR(255) REFERENCES routes(route_id),
    route_licence_number SMALLINT,
    sub_agency_id       VARCHAR(255) REFERENCES sub_agencies(sub_agency_id),
);

CREATE TABLE route_stops (
    route_id            VARCHAR(255) REFERENCES routes(route_id),
    direction_id        SMALLINT NOT NULL,
    stop_id             VARCHAR(63) REFERENCES stops(stop_id),
    stop_sequence       SMALLINT NOT NULL,
);

CREATE TABLE shapes (
    shape_id            VARCHAR(255) PRIMARY KEY,
    shape_pt_lat        DOUBLE PRECISION NOT NULL,
    shape_pt_lon        DOUBLE PRECISION NOT NULL,
    shape_pt_sequence   SMALLINT NOT NULL CHECK (shape_pt_sequence >= 0),
    shape_dist_traveled DOUBLE PRECISION CHECK (shape_dist_traveled >= 0)
);

CREATE TABLE trips (
    trip_id             VARCHAR(255) PRIMARY KEY,
    route_id            VARCHAR(255) REFERENCES routes(route_id),
    service_id          VARCHAR(255) REFERENCES calendar(service_id),
    trip_headsign       VARCHAR(255),
    trip_short_name     VARCHAR(255),
    direction_id        SMALLINT CHECK (direction_id IN (0,1)),
    block_id            VARCHAR(255),
    shape_id            VARCHAR(255) REFERENCES shapes(shape_id),
    wheelchair_accessible SMALLINT CHECK (wheelchair_accessible IN (0,1,2)),
    bikes_allowed       SMALLINT CHECK (bikes_allowed IN (0,1,2)),
    exceptional         BOOLEAN DEFAULT FALSE,
    sub_agency_id       VARCHAR(255) REFERENCES sub_agencies(sub_agency_id)
);

CREATE TABLE stop_times (
    trip_id             VARCHAR(255) REFERENCES trips(trip_id),
    arrival_time        INTERVAL, -- stored as interval to allow times > 24:00:00
    departure_time      INTERVAL, -- stored as interval to allow times > 24:00:00
    stop_id             VARCHAR(255) REFERENCES stops(stop_id),
    stop_sequence       SMALLINT NOT NULL,
    stop_headsign       VARCHAR(255),
    pickup_type         SMALLINT CHECK (pickup_type IN (0,1,2,3)),
    drop_off_type       SMALLINT CHECK (drop_off_type IN (0,1,2,3)),
    shape_dist_traveled DOUBLE PRECISION CHECK (shape_dist_traveled >= 0),
    trip_operation_type SMALLINT CHECK (trip_operation_type IN (1,7,8,9,10)),
    bikes_allowed       SMALLINT CHECK (bikes_allowed IN (0,1,2,3,4,5)),
);

CREATE TABLE pathways (
    pathway_id          VARCHAR(255) PRIMARY KEY,
    from_stop_id        VARCHAR(255) REFERENCES stops(stop_id) NOT NULL,
    to_stop_id          VARCHAR(255) REFERENCES stops(stop_id) NOT NULL,
    pathway_mode        SMALLINT NOT NULL CHECK (pathway_mode IN (0,1,2,3,4,5,6)),
    is_bidirectional    BOOLEAN NOT NULL,
    traversal_time      INTEGER CHECK (traversal_time > 0),
    signposted_as       VARCHAR(255),
    reversed_signposted_as VARCHAR(255),
    bikes_prohibited    BOOLEAN DEFAULT FALSE
);

CREATE TABLE transfers (
    from_stop_id        VARCHAR(255) REFERENCES stops(stop_id),
    to_stop_id          VARCHAR(63) REFERENCES stops(stop_id),
    transfer_type       SMALLINT NOT NULL CHECK (transfer_type IN (0,1,2,3,4,5)),
    min_transfer_time   INTEGER,
    from_trip_id        VARCHAR(63) REFERENCES trips(trip_id),
    to_trip_id          VARCHAR(63) REFERENCES trips(trip_id),
    max_waiting_time    INTEGER,
);

CREATE TABLE fare_attributes (
    fare_id             VARCHAR(255) PRIMARY KEY,
    price               DOUBLE PRECISION NOT NULL,
    currency_type       VARCHAR(255) NOT NULL,
    payment_method      SMALLINT NOT NULL CHECK (payment_method IN (0,1)),
    transfers           SMALLINT CHECK (transfers IN (0,1,2)),
    agency_id           VARCHAR(255) REFERENCES agency(agency_id),
    transfer_duration   INTEGER CHECK (transfer_duration >= 0)
);

CREATE TABLE fare_rules (
    fare_id             VARCHAR(255) REFERENCES fare_attributes(fare_id),
    contains_id         VARCHAR(255) REFERENCES stops(zone_id),
    route_id            VARCHAR(63) REFERENCES routes(route_id)
);

CREATE TABLE vehicle_categories (
    vehicle_category_id VARCHAR(255) PRIMARY KEY
);

CREATE TABLE vehicle_allocations (
    route_id            VARCHAR(255) REFERENCES routes(route_id),
    vehicle_category_id VARCHAR(255) REFERENCES vehicle_categories(vehicle_category_id),
);

CREATE TABLE vehicle_boardings (
    vehicle_category_id VARCHAR(255) REFERENCES vehicle_categories(vehicle_category_id),
    child_sequence      INTEGER NOT NULL,
    boarding_area_id    VARCHAR(255),
);

CREATE TABLE vehicle_couplings (
    parent_id           VARCHAR(255) REFERENCES vehicle_categories(vehicle_category_id),
    child_id            VARCHAR(255) REFERENCES vehicle_categories(vehicle_category_id),
    child_sequence      SMALLINT NOT NULL,
);

-- ======================
--  INDEX SUGGESTIONS (common queries)
-- ======================
--CREATE INDEX idx_stop_times_trip ON stop_times(trip_id);
--CREATE INDEX idx_stop_times_stop ON stop_times(stop_id);
--CREATE INDEX idx_trips_route ON trips(route_id);
--CREATE INDEX idx_route_stops_stop ON route_stops(stop_id);
--CREATE INDEX idx_shapes_points_shape ON shape_points(shape_id);

-- End of schema
