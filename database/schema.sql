CREATE TABLE containers (
    container_id VARCHAR(50) PRIMARY KEY,
    origin_port VARCHAR(20),
    current_milestone VARCHAR(50),
    total_units INTEGER,
    total_weight_kg NUMERIC(12,2),
    arrival_timestamp TIMESTAMP
);
