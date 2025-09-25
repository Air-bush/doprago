DROP TABLE agency; -- IGNORE --
DROP TABLE feed_info; --- IGNORE ---
DROP TABLE stops;
DROP TABLE routes;
DROP TABLE calendar;
DROP TABLE calendar_dates;
DROP TABLE shapes;
DROP TABLE trips;
DROP TABLE stop_times;
DROP TABLE frequencies;
DROP TABLE transfers;

CREATE TABLE agency
(
  agency_id         VARCHAR(255) UNIQUE NULL,
  agency_name       VARCHAR(255) NOT NULL,
  agency_url        VARCHAR(255) NOT NULL,
  agency_timezone   VARCHAR(255) NOT NULL,
  agency_lang       VARCHAR(255) NULL,
  agency_phone      VARCHAR(255) NULL
);

CREATE TABLE feed_info (
  feed_publisher_name VARCHAR(255) NOT NULL,
  feed_publisher_url  VARCHAR(255) NOT NULL,
  feed_lang           VARCHAR(255) NOT NULL,
  feed_start_date     NUMERIC(8) NULL,
  feed_end_date       NUMERIC(8) NULL,
  feed_contact_email  VARCHAR(255) NULL
);

CREATE TABLE stops
(
  stop_id             VARCHAR(255) PRIMARY KEY,
  stop_code           VARCHAR(255) NULL,
  stop_name           VARCHAR(255) NOT NULL,
  stop_desc           VARCHAR(255) NULL,
  stop_lat            double precision NOT NULL,
  stop_lon            double precision NOT NULL,
  zone_id             VARCHAR(255) NULL,
  stop_url            VARCHAR(255) NULL,
  location_type       boolean NULL,
  parent_station      VARCHAR(255) NULL,
  wheelchair_boarding VARCHAR(255) NULL
);

CREATE TABLE routes
(
  route_id          VARCHAR(255) PRIMARY KEY,
  agency_id         VARCHAR(255) NULL,
  route_short_name  VARCHAR(255) NULL,
  route_long_name   VARCHAR(255) NULL,
  route_desc        VARCHAR(255) NULL,
  route_type        integer NULL,
  route_url         VARCHAR(255) NULL,
  route_color       VARCHAR(255) NULL,
  route_text_color  VARCHAR(255) NULL,
  route_sort_order  integer NULL
);

CREATE TABLE calendar
(
  service_id        VARCHAR(255) PRIMARY KEY,
  monday            boolean NOT NULL,
  tuesday           boolean NOT NULL,
  wednesday         boolean NOT NULL,
  thursday          boolean NOT NULL,
  friday            boolean NOT NULL,
  saturday          boolean NOT NULL,
  sunday            boolean NOT NULL,
  start_date        numeric(8) NOT NULL,
  end_date          numeric(8) NOT NULL
);

CREATE TABLE calendar_dates
(
  service_id VARCHAR(255) NOT NULL,
  date numeric(8) NOT NULL,
  exception_type integer NOT NULL
);

CREATE TABLE shapes
(
  shape_id          VARCHAR(255),
  shape_pt_lat      double precision NOT NULL,
  shape_pt_lon      double precision NOT NULL,
  shape_pt_sequence integer NOT NULL,
  shape_dist_traveled VARCHAR(255) NULL
);

CREATE TABLE trips
(
  route_id          VARCHAR(255) NOT NULL,
  service_id        VARCHAR(255) NOT NULL,
  trip_id           VARCHAR(255) NOT NULL PRIMARY KEY,
  trip_headsign     VARCHAR(255) NULL,
  trip_short_name   VARCHAR(255) NULL,
  direction_id      boolean NULL,
  block_id          VARCHAR(255) NULL,
  shape_id          VARCHAR(255) NULL,
  wheelchair_accessible VARCHAR(255) NULL
);

CREATE TABLE stop_times
(
  trip_id           VARCHAR(255) NOT NULL,
  arrival_time      interval NOT NULL,
  departure_time    interval NOT NULL,
  stop_id           VARCHAR(255) NOT NULL,
  stop_sequence     integer NOT NULL,
  stop_headsign     VARCHAR(255) NULL,
  pickup_type       integer NULL CHECK(pickup_type >= 0 and pickup_type <=3),
  drop_off_type     integer NULL CHECK(drop_off_type >= 0 and drop_off_type <=3)
);

CREATE TABLE frequencies
(
  trip_id           VARCHAR(255) NOT NULL,
  start_time        interval NOT NULL,
  end_time          interval NOT NULL,
  headway_secs      integer NOT NULL
);

CREATE TABLE transfers
(
  from_stop_id  VARCHAR(255) NOT NULL,
  to_stop_id    VARCHAR(255) NOT NULL,
    transfer_type   integer NOT NULL,
    min_transfer_time integer
);

--\copy agency from './gtfs/agency.txt' with csv header
--\copy feed_info from './gtfs/feed_info.txt' with csv header
--\copy stops from './gtfs/stops.txt' with csv header
--\copy routes from './gtfs/routes.txt' with csv header
--\copy calendar from './gtfs/calendar.txt' with csv header
--\copy calendar_dates from './gtfs/calendar_dates.txt' with csv header
--\copy shapes from './gtfs/shapes.txt' with csv header
--\copy trips from './gtfs/trips.txt' with csv header
--\copy stop_times from './gtfs/stop_times.txt' with csv header
--\copy frequencies from './gtfs/frequencies.txt' with csv header
--\copy transfers from './gtfs/transfers.txt' with csv header
