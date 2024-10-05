-- DO $$ 
-- BEGIN 
--    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'my_database') THEN
--       EXECUTE 'CREATE DATABASE my_database';
--    END IF;
-- END $$;

-- \c my_database;

CREATE TABLE IF NOT EXISTS appeal (
    id SERIAL PRIMARY KEY,
    lastname VARCHAR(50),
    firstname VARCHAR(50),
    middlename VARCHAR(50),
    phone VARCHAR(15),
    message TEXT
);
