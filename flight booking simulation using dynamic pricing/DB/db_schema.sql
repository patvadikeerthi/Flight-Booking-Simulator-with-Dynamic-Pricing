CREATE TABLE Aircraft (
    aircraft_id SERIAL PRIMARY KEY,-- PRIMARY KEY, SERIAL
    model VARCHAR(100) NOT NULL,-- NOT NULL
    total_capacity INTEGER NOT NULL CHECK (total_capacity > 0)-- NOT NULL, CHECK
);

CREATE TABLE Route (
    route_id SERIAL PRIMARY KEY,-- PRIMARY KEY, SERIAL
    origin_airport_code CHAR(3) NOT NULL,
    destination_airport_code CHAR(3) NOT NULL,
    base_duration_minutes INTEGER NOT NULL,
    UNIQUE (origin_airport_code, destination_airport_code)-- UNIQUE
);

CREATE TABLE Flight (
    flight_id SERIAL PRIMARY KEY,-- PRIMARY KEY, SERIAL
    flight_number VARCHAR(10) NOT NULL UNIQUE,
    route_id INTEGER REFERENCES Route(route_id),-- FOREIGN KEY
    aircraft_id INTEGER REFERENCES Aircraft(aircraft_id),-- FOREIGN KEY
    departure_time TIMESTAMP WITH TIME ZONE NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL CHECK (base_price >= 0)
);

CREATE TABLE Seat (
    seat_id SERIAL PRIMARY KEY,-- PRIMARY KEY, SERIAL
    flight_id INTEGER REFERENCES Flight(flight_id),-- FOREIGN KEY
    seat_number VARCHAR(5) NOT NULL,
    class VARCHAR(20) NOT NULL,
    is_booked BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (flight_id, seat_number)
);

CREATE TABLE Booking (
    booking_id SERIAL PRIMARY KEY,-- PRIMARY KEY, SERIAL
    pnr_code CHAR(6) NOT NULL UNIQUE,
    flight_id INTEGER REFERENCES Flight(flight_id),-- FOREIGN KEY
    seat_id INTEGER REFERENCES Seat(seat_id) UNIQUE,-- FOREIGN KEY, UNIQUE
    total_fare_paid DECIMAL(10, 2) NOT NULL CHECK (total_fare_paid >= 0),
    passenger_name VARCHAR(100) NOT NULL,
    booking_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE PriceFactor (
    factor_id SERIAL PRIMARY KEY,-- PRIMARY KEY, SERIAL
    flight_id INTEGER REFERENCES Flight(flight_id),-- FOREIGN KEY
    seats_booked_percent DECIMAL(5, 2) NOT NULL,
    fare_multiplier DECIMAL(5, 2) NOT NULL,
    UNIQUE (flight_id, seats_booked_percent)
);

-- ALTER TABLE EXAMPLE

ALTER TABLE Flight
ADD COLUMN current_occupancy DECIMAL(5, 2) NOT NULL DEFAULT 0.00;

-- SAMPLE DATA POPULATION 

--- 1. Aircraft (20 Entries)
INSERT INTO Aircraft (model, total_capacity) VALUES
('Airbus A320-200', 180), ('Boeing 737-800', 189), ('Airbus A321neo', 220), ('Boeing 787-9 Dreamliner', 290),
('Airbus A350-900', 325), ('Boeing 777-300ER', 396), ('ATR 72-600', 78), ('Bombardier Q400', 76),
('Embraer 175', 88), ('Airbus A380', 550), ('Boeing 747-8', 467), ('Airbus A319', 156),
('Boeing 737 MAX 8', 178), ('Airbus A330-300', 277), ('Boeing 767-300', 218), ('Airbus A340-600', 320),
('Embraer 190', 114), ('Cessna Caravan 208', 9), ('Airbus A320neo', 186), ('Boeing 737-900ER', 215);

--- 2. Route (20 Entries)
INSERT INTO Route (origin_airport_code, destination_airport_code, base_duration_minutes) VALUES
('DEL', 'BOM', 120), ('BOM', 'BLR', 95), ('BLR', 'MAA', 60), ('MAA', 'HYD', 75),
('HYD', 'CCU', 150), ('CCU', 'DEL', 180), ('DEL', 'GOI', 135), ('BOM', 'COK', 150),
('BLR', 'PNQ', 70), ('MAA', 'AMD', 180), ('HYD', 'LKO', 140), ('CCU', 'PAT', 60),
('JAI', 'BOM', 105), ('IXR', 'DEL', 130), ('DEL', 'DOH', 240), ('BOM', 'DXB', 180),
('BLR', 'SIN', 300), ('MAA', 'KUL', 245), ('HYD', 'CMB', 120), ('CCU', 'DMK', 180);

--- 3. Flight (20 Entries)
INSERT INTO Flight (flight_number, route_id, aircraft_id, departure_time, base_price) VALUES
('AI101', 1, 3, '2025-11-10 06:00:00+05:30', 4500.00), ('6E202', 2, 2, '2025-11-10 09:30:00+05:30', 3800.00),
('UK303', 3, 1, '2025-11-11 12:45:00+05:30', 3200.00), ('SG404', 4, 4, '2025-11-11 16:00:00+05:30', 4100.00),
('AI505', 5, 5, '2025-11-12 10:15:00+05:30', 5500.00), ('6E606', 6, 6, '2025-11-12 20:30:00+05:30', 6000.00),
('UK707', 7, 7, '2025-11-13 08:00:00+05:30', 4200.00), ('SG808', 8, 8, '2025-11-13 14:00:00+05:30', 4900.00),
('AI909', 9, 9, '2025-11-14 11:00:00+05:30', 3000.00), ('6E100', 10, 10, '2025-11-14 19:00:00+05:30', 6500.00),
('UK111', 11, 11, '2025-11-15 07:30:00+05:30', 5100.00), ('SG122', 12, 12, '2025-11-15 15:00:00+05:30', 2500.00),
('AI133', 13, 13, '2025-11-16 10:45:00+05:30', 3900.00), ('6E144', 14, 14, '2025-11-16 22:00:00+05:30', 4700.00),
('UK155', 15, 15, '2025-11-17 06:30:00+05:30', 18000.00), ('SG166', 16, 16, '2025-11-17 13:00:00+05:30', 16500.00),
('AI177', 17, 17, '2025-11-18 09:45:00+05:30', 22000.00), ('6E188', 18, 18, '2025-11-18 17:15:00+05:30', 19000.00),
('UK199', 19, 19, '2025-11-19 11:30:00+05:30', 15500.00), ('SG200', 20, 20, '2025-11-19 20:00:00+05:30', 17000.00);

--- 4. PriceFactor (20 Entries)
INSERT INTO PriceFactor (flight_id, seats_booked_percent, fare_multiplier) VALUES
(1, 0, 1.00), (1, 50, 1.25), (1, 75, 1.70), (1, 90, 2.20),
(2, 0, 1.00), (2, 50, 1.20), (2, 70, 1.60), (2, 85, 2.00),
(3, 0, 1.00), (3, 60, 1.30), (3, 80, 1.80), (3, 95, 2.50),
(4, 0, 1.00), (4, 40, 1.15), (4, 65, 1.50), (4, 80, 1.90),
(5, 0, 1.00), (5, 55, 1.28), (5, 78, 1.75), (5, 92, 2.30);

--- 5. Seat (20 Entries)
INSERT INTO Seat (flight_id, seat_number, class, is_booked) VALUES
(1, '1A', 'First', FALSE), (1, '1B', 'First', TRUE), (1, '10C', 'Business', FALSE), (1, '10D', 'Business', TRUE),
(1, '25F', 'Economy', FALSE), (1, '30A', 'Economy', TRUE), (1, '30B', 'Economy', FALSE), (1, '30C', 'Economy', TRUE),
(2, '5A', 'Economy', FALSE), (2, '5B', 'Economy', FALSE), (2, '10F', 'Economy', TRUE), (2, '15C', 'Economy', FALSE),
(3, '1A', 'Business', TRUE), (3, '1B', 'Business', FALSE), (3, '5A', 'Business', FALSE), (3, '10A', 'Economy', FALSE),
(3, '15F', 'Economy', TRUE), (4, '2A', 'Economy', FALSE), (4, '2B', 'Economy', TRUE), (5, '10C', 'Economy', FALSE);

--- 6. Booking (20 Entries)
INSERT INTO Booking (pnr_code, flight_id, seat_id, total_fare_paid, passenger_name, booking_time) VALUES
('A1B2C3', 1, 2, 4500.00, 'Ravi Kumar', '2025-10-01 10:00:00+05:30'),
('D4E5F6', 1, 4, 5625.00, 'Priya Sharma', '2025-10-01 11:30:00+05:30'),
('G7H8I9', 1, 6, 7650.00, 'Amit Singh', '2025-10-02 09:00:00+05:30'),
('J0K1L2', 1, 8, 9900.00, 'Neha Patel', '2025-10-03 14:00:00+05:30'),
('M3N4O5', 2, 11, 3800.00, 'Vikas Gupta', '2025-10-03 16:30:00+05:30'),
('P6Q7R8', 3, 13, 3960.00, 'Sneha Jain', '2025-10-04 10:00:00+05:30'),
('S9T0U1', 3, 17, 5760.00, 'Gaurav Das', '2025-10-04 17:00:00+05:30'),
('V2W3X4', 4, 19, 4715.00, 'Anjali Verma', '2025-10-05 08:30:00+05:30'),
('Y5Z6A7', 6, NULL, 7800.00, 'Rahul Khanna', '2025-10-05 13:00:00+05:30'),
('B8C9D0', 7, NULL, 5040.00, 'Deepak Yadav', '2025-10-06 10:00:00+05:30'),
('E1F2G3', 8, NULL, 6125.00, 'Kirti Reddy', '2025-10-06 14:30:00+05:30'),
('H4I5J6', 9, NULL, 3750.00, 'Manoj Soni', '2025-10-07 09:00:00+05:30'),
('K7L8M9', 10, NULL, 7800.00, 'Divya Nair', '2025-10-07 18:00:00+05:30'),
('N0O1P2', 11, NULL, 6375.00, 'Rajesh Menon', '2025-10-08 07:00:00+05:30'),
('Q3R4S5', 12, NULL, 3000.00, 'Karan Taneja', '2025-10-08 11:45:00+05:30'),
('T6U7V8', 13, NULL, 4875.00, 'Sonia Bhati', '2025-10-09 10:00:00+05:30'),
('W9X0Y1', 14, NULL, 5875.00, 'Harish Joshi', '2025-10-09 15:30:00+05:30'),
('Z2A3B4', 15, NULL, 22500.00, 'John Smith', '2025-10-10 09:00:00+05:30'),
('C5D6E7', 16, NULL, 20625.00, 'Liu Wei', '2025-10-10 13:00:00+05:30'),
('F8G9H0', 17, NULL, 27500.00, 'Ahmed Khan', '2025-10-11 08:00:00+05:30');

-- JOIN EXAMPLE

SELECT
    B.pnr_code,
    S.seat_number,
    S.class,
    F.flight_number,
    A.model AS aircraft_model
FROM
    Booking B
INNER JOIN
    Seat S ON B.seat_id = S.seat_id
INNER JOIN
    Flight F ON B.flight_id = F.flight_id
INNER JOIN
    Aircraft A ON F.aircraft_id = A.aircraft_id
WHERE
    F.flight_number = 'AI101';

-- TRANSACTION EXAMPLE 

BEGIN;

UPDATE Seat
SET is_booked = TRUE
WHERE seat_id = 1 AND is_booked = FALSE;

INSERT INTO Booking (pnr_code, flight_id, seat_id, total_fare_paid, passenger_name)
VALUES ('T9R8S7', 1, 1, 5625.00, 'Suresh Reddy');

COMMIT;