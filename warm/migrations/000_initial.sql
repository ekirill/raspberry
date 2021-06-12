CREATE schema IF NOT EXISTS warm;

CREATE TABLE IF NOT EXISTS warm.level (
    dt TIMESTAMP WITH TIME ZONE PRIMARY KEY NOT NULL DEFAULT NOW(),
    level INT NOT NULL,
    changed_by VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS warm.temperature (
    dt TIMESTAMP WITH TIME ZONE PRIMARY KEY NOT NULL DEFAULT NOW(),
    t1 INT,
    t2 INT,
    t3 INT,
    t4 INT
);