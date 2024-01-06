CREATE TABLE IF NOT EXISTS users(
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    userId SERIAL PRIMARY KEY,
    email TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS flags(
    userId INT PRIMARY KEY,
    todo BOOLEAN DEFAULT FALSE,
    hoursRange numrange DEFAULT numrange('[14, 22]'),
    FOREIGN KEY (userId) REFERENCES users(userId)
);

CREATE TABLE IF NOT EXISTS words(
    userId INT PRIMARY KEY,
    list JSON NOT NULL,
    FOREIGN KEY (userId) REFERENCES users(userId)
);