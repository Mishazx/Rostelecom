CREATE TABLE IF NOT EXISTS requests (
    id SERIAL PRIMARY KEY,
    lastname VARCHAR(50),
    firstname VARCHAR(50),
    middlename VARCHAR(50),
    phone VARCHAR(15),
    message TEXT
);