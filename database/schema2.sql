CREATE TABLE agency (
    agency_id           VARCHAR(63) PRIMARY KEY,
    agency_name         VARCHAR(127) NOT NULL,
    agency_url          VARCHAR(255) NOT NULL,
    agency_timezone     VARCHAR(31) NOT NULL,
    agency_lang         VARCHAR(31),
    agency_phone        VARCHAR(31)
);

CREATE TABLE calendar (
    service_id          VARCHAR(63) PRIMARY KEY,
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
    service_id          ARCHAR(63) PRIMARY KEY REFERENCES calendar(service_id),
    date                DATE NOT NULL,
    exception_type      SMALLINT NOT NULL CHECK (exception_type IN (1,2)),
);

CREATE TABLE feed_info (
    feed_info_id        SERIAL PRIMARY KEY,
    feed_publisher_name VARCHAR(127) NOT NULL,
    feed_publisher_url  VARCHAR(255) NOT NULL,
    feed_lang           VARCHAR(31) NOT NULL,
    feed_start_date     DATE,
    feed_end_date       DATE,
    feed_contact_email  VARCHAR(255)
);

CREATE TABLE levels (
    level_id            VARCHAR(63) PRIMARY KEY,
    level_index         INTEGER NOT NULL,
    level_name          VARCHAR(63)
);

CREATE TABLE stops (
    stop_id             VARCHAR(63) PRIMARY KEY,
    stop_name           VARCHAR(127) NOT NULL,
    stop_lat            DOUBLE PRECISION NOT NULL,
    stop_lon            DOUBLE PRECISION NOT NULL,
    zone_id             VARCHAR(31),
    stop_url            VARCHAR(255),
    location_type       SMALLINT,
    parent_station      VARCHAR(63) REFERENCES stops(stop_id) ON DELETE SET NULL,
    wheelchair_boarding SMALLINT,
    level_id            VARCHAR(63) REFERENCES levels(level_id) ON DELETE SET NULL,
    platform_code       VARCHAR(31),
    asw_node_id         VARCHAR(63),
    asw_stop_id         VARCHAR(63),
    zone_region_type    VARCHAR(31)
);

CREATE TABLE routes (
    route_id            VARCHAR(63) PRIMARY KEY,
    agency_id           VARCHAR(63) REFERENCES agency(agency_id) ON DELETE SET NULL,
    route_short_name    VARCHAR(31),
    route_long_name     VARCHAR(127),
    route_type          SMALLINT NOT NULL,
    route_url           VARCHAR(255),
    route_color         CHAR(31),     -- hex without '#'
    route_text_color    CHAR(31),
    is_night            BOOLEAN DEFAULT FALSE,
    is_regional         BOOLEAN DEFAULT FALSE,
    is_substitute_transport BOOLEAN DEFAULT FALSE
);

-- Sub-agency as an entity (so same sub_agency can be associated to many routes)
CREATE TABLE sub_agencies (
    sub_agency_id       VARCHAR(63) PRIMARY KEY,
    sub_agency_name     VARCHAR(127),
    notes               VARCHAR(255)
);

-- join table for routes <-> sub_agencies, with licence per route-sub
CREATE TABLE route_sub_agencies (
    id                  SERIAL PRIMARY KEY,
    route_id            VARCHAR(63) REFERENCES routes(route_id) ON DELETE CASCADE,
    sub_agency_id       VARCHAR(63) REFERENCES sub_agencies(sub_agency_id) ON DELETE CASCADE,
    route_licence_number VARCHAR(63),
    UNIQUE(route_id, sub_agency_id)
);

-- route stops: sequence per route + direction
CREATE TABLE route_stops (
    route_id            VARCHAR(63) REFERENCES routes(route_id) ON DELETE CASCADE,
    direction_id        SMALLINT DEFAULT 0,
    stop_id             VARCHAR(63) REFERENCES stops(stop_id) ON DELETE CASCADE,
    stop_sequence       INTEGER NOT NULL,
    PRIMARY KEY (route_id, direction_id, stop_sequence)
);

CREATE TABLE shapes (
    shape_id            VARCHAR(63) PRIMARY KEY
);

CREATE TABLE shape_points (
    shape_id            VARCHAR(63) REFERENCES shapes(shape_id) ON DELETE CASCADE,
    shape_pt_sequence   INTEGER NOT NULL,
    shape_pt_lat        DOUBLE PRECISION NOT NULL,
    shape_pt_lon        DOUBLE PRECISION NOT NULL,
    shape_dist_traveled DOUBLE PRECISION,
    PRIMARY KEY (shape_id, shape_pt_sequence)
);

CREATE TABLE trips (
    trip_id             VARCHAR(63) PRIMARY KEY,
    route_id            VARCHAR(63) REFERENCES routes(route_id) ON DELETE SET NULL,
    service_id          VARCHAR(63) REFERENCES services(service_id) ON DELETE SET NULL,
    trip_headsign       VARCHAR(127),
    trip_short_name     VARCHAR(31),
    direction_id        SMALLINT,
    block_id            VARCHAR(63),
    shape_id            VARCHAR(63) REFERENCES shapes(shape_id) ON DELETE SET NULL,
    wheelchair_accessible SMALLINT,
    bikes_allowed       SMALLINT,
    exceptional         BOOLEAN DEFAULT FALSE,
    sub_agency_id       VARCHAR(63) REFERENCES sub_agencies(sub_agency_id) ON DELETE SET NULL
);

-- stop_times: arrival/departure in seconds from midnight (allows >24:00)
CREATE TABLE stop_times (
    trip_id             VARCHAR(63) REFERENCES trips(trip_id) ON DELETE CASCADE,
    stop_sequence       INTEGER NOT NULL,
    stop_id             VARCHAR(63) REFERENCES stops(stop_id) ON DELETE CASCADE,
    arrival_time_secs   INTEGER CHECK (arrival_time_secs >= 0),
    departure_time_secs INTEGER CHECK (departure_time_secs >= 0),
    stop_headsign       VARCHAR(127),
    pickup_type         SMALLINT,
    drop_off_type       SMALLINT,
    shape_dist_traveled DOUBLE PRECISION,
    trip_operation_type SMALLINT,
    bikes_allowed       SMALLINT,
    PRIMARY KEY (trip_id, stop_sequence)
);

CREATE TABLE pathways (
    pathway_id          VARCHAR(63) PRIMARY KEY,
    from_stop_id        VARCHAR(63) REFERENCES stops(stop_id) ON DELETE CASCADE,
    to_stop_id          VARCHAR(63) REFERENCES stops(stop_id) ON DELETE CASCADE,
    pathway_mode        SMALLINT NOT NULL,
    is_bidirectional    BOOLEAN DEFAULT FALSE,
    traversal_time      INTEGER,
    signposted_as       VARCHAR(63),
    reversed_signposted_as VARCHAR(63),
    bikes_prohibited    BOOLEAN DEFAULT FALSE
);

CREATE TABLE transfers (
    transfer_id         SERIAL PRIMARY KEY,
    from_stop_id        VARCHAR(63) REFERENCES stops(stop_id) ON DELETE CASCADE,
    to_stop_id          VARCHAR(63) REFERENCES stops(stop_id) ON DELETE CASCADE,
    transfer_type       SMALLINT NOT NULL,
    min_transfer_time   INTEGER,
    from_trip_id        VARCHAR(63) REFERENCES trips(trip_id) ON DELETE SET NULL,
    to_trip_id          VARCHAR(63) REFERENCES trips(trip_id) ON DELETE SET NULL,
    max_waiting_time    INTEGER,
    UNIQUE (from_stop_id, to_stop_id, from_trip_id, to_trip_id)
);

CREATE TABLE fare_attributes (
    fare_id             VARCHAR(63) PRIMARY KEY,
    price               SMALLINT NOT NULL,
    currency_type       VARCHAR(31) NOT NULL,
    payment_method      SMALLINT NOT NULL CHECK (payment_method IN (0,1)),
    transfers           SMALLINT,
    agency_id           VARCHAR(63) REFERENCES agency(agency_id) ON DELETE SET NULL,
    transfer_duration   INTEGER
);

CREATE TABLE fare_rules (
    fare_rule_id        SERIAL PRIMARY KEY,
    fare_id             VARCHAR(63) REFERENCES fare_attributes(fare_id) ON DELETE CASCADE,
    contains_id         VARCHAR(63),   -- zone or contains identifier
    route_id            VARCHAR(63) REFERENCES routes(route_id) ON DELETE SET NULL
);

CREATE TABLE vehicle_categories (
    vehicle_category_id VARCHAR(63) PRIMARY KEY
);

CREATE TABLE vehicle_allocations (
    id                  SERIAL PRIMARY KEY,
    route_id            VARCHAR(63) REFERENCES routes(route_id) ON DELETE CASCADE,
    vehicle_category_id VARCHAR(63) REFERENCES vehicle_categories(vehicle_category_id) ON DELETE CASCADE,
    UNIQUE (route_id, vehicle_category_id)
);

CREATE TABLE vehicle_boardings (
    id                  SERIAL PRIMARY KEY,
    vehicle_category_id VARCHAR(63) REFERENCES vehicle_categories(vehicle_category_id) ON DELETE CASCADE,
    child_sequence      INTEGER NOT NULL,
    boarding_area_id    VARCHAR(63),
    UNIQUE (vehicle_category_id, child_sequence)
);

CREATE TABLE vehicle_couplings (
    id                  SERIAL PRIMARY KEY,
    parent_id           VARCHAR(63) REFERENCES vehicle_categories(vehicle_category_id) ON DELETE CASCADE,
    child_id            VARCHAR(63) REFERENCES vehicle_categories(vehicle_category_id) ON DELETE CASCADE,
    child_sequence      INTEGER NOT NULL,
    UNIQUE (parent_id, child_id, child_sequence)
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
