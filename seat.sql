CREATE TABLE seats (
    seat_number VARCHAR(10) PRIMARY KEY,
    on_break BOOLEAN DEFAULT FALSE,
    is_flagged BOOLEAN DEFAULT FALSE
);
