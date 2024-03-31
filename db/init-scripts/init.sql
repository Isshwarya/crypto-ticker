-- DDL for `crypto_price` table
CREATE TABLE crypto_price (
    id SERIAL,
    symbol VARCHAR(20),
    price FLOAT,
    datetime TIMESTAMP,
    PRIMARY KEY (id, datetime),
    CONSTRAINT unique_symbol_datetime UNIQUE (symbol, datetime)
) PARTITION BY RANGE (datetime);

-- DDL for `latest_crypto_price` table
CREATE TABLE latest_crypto_price (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE,
    price FLOAT,
    datetime TIMESTAMP
);

CREATE OR REPLACE FUNCTION generate_partition_name(start_date TIMESTAMP, end_date TIMESTAMP)
RETURNS TEXT AS $$
DECLARE
    partition_name TEXT;
BEGIN
    partition_name := 'crypto_price_' || to_char(start_date, 'YYYY_MM_DD') || '_' || to_char(end_date, 'YYYY_MM_DD');
    RETURN partition_name;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION create_partitions(start_date TIMESTAMP, end_date TIMESTAMP)
RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
BEGIN
    partition_name := generate_partition_name(start_date, end_date);
    EXECUTE FORMAT('CREATE TABLE %I PARTITION OF crypto_price FOR VALUES FROM (%L) TO (%L)', partition_name, start_date, end_date);
END;
$$ LANGUAGE plpgsql;

-- Creating weekly partitions manually for April month. This is just a quickfix solution -- 
SELECT create_partitions('2024-03-24 00:00:00', '2024-03-30 23:59:59');
SELECT create_partitions('2024-03-31 00:00:00', '2024-04-06 23:59:59');
SELECT create_partitions('2024-04-07 00:00:00', '2024-04-13 23:59:59');
SELECT create_partitions('2024-04-14 00:00:00', '2024-04-20 23:59:59');
SELECT create_partitions('2024-04-21 00:00:00', '2024-04-27 23:59:59');
SELECT create_partitions('2024-04-28 00:00:00', '2024-05-04 23:59:59');