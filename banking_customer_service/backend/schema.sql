CREATE TABLE IF NOT EXISTS customers(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    dob TEXT,
    created_at TEXT
);


CREATE TABLE IF NOT EXISTS accounts(
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    account_type TEXT,
    balance FLOAT,
    opened_at TEXT

);


CREATE TABLE IF NOT EXISTS tickets(
    id INTEGER PRIMARY KEY,
    ticket_number TEXT UNIQUE,
    customer_id INTEGER,
    message TEXT,
    status TEXT,
    created_at TEXT
);