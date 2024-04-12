CREATE TABLE IF NOT EXISTS users(
    userid SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    created timestamp with time zone default current_timestamp
);

CREATE TABLE IF NOT EXISTS flags(
    flagid SERIAL PRIMARY KEY,
    userid SERIAL REFERENCES users ON DELETE CASCADE,
    todo BOOLEAN NOT NULL DEFAULT FALSE,
    hoursrange numrange NOT NULL DEFAULT numrange('[14, 22]'),
    instaling_user TEXT NOT NULL DEFAULT '',
    instaling_pass TEXT NOT NULL DEFAULT '',
    error_level INT NOT NULL DEFAULT 5
);

CREATE TABLE IF NOT EXISTS words(
    flagid SERIAL PRIMARY KEY REFERENCES flags ON DELETE CASCADE,
    userid SERIAL KEY REFERENCES users ON DELETE CASCADE,
    list JSON NOT NULL DEFAULT '[]'
);