PRAGMA foreign_keys = ON;

CREATE TABLE general_info (
    year INTEGER PRIMARY KEY,
    min_salary INTEGER NOT NULL,
    tax_rate REAL NOT NULL,
    normative_monetary_value REAL NOT NULL
);

CREATE TABLE real_estate_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    middle_name TEXT NOT NULL,
    rnokpp INTEGER NOT NULL UNIQUE,
    address TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT CHECK (Phone GLOB '[0-9]*')
);

CREATE TABLE real_estate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    area REAL NOT NULL,
    area_taxable REAL NOT NULL,
    tax REAL NOT NULL,
    notes TEXT,
    user_id INTEGER,
    real_estate_type_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (real_estate_type_id) REFERENCES real_estate_type(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);