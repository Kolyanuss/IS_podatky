PRAGMA foreign_keys = ON;

CREATE TABLE general_info (
    year INTEGER PRIMARY KEY,
    min_salary INTEGER NOT NULL
);

CREATE TABLE real_estate_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE real_estate_type_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tax_year INTEGER NOT NULL,
    real_estate_type_id INTEGER NOT NULL,
    tax_area_limit REAL NOT NULL,
    tax_rate REAL NOT NULL CHECK (tax_rate >= 0),
    FOREIGN KEY (real_estate_type_id) REFERENCES real_estate_type(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT unique_type_year UNIQUE(real_estate_type_id, tax_year)
);

CREATE TABLE land_parcel_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE land_parcel_type_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tax_year INTEGER NOT NULL,
    land_parcel_type_id INTEGER NOT NULL,
    tax_rate REAL NOT NULL CHECK (tax_rate >= 0),
    FOREIGN KEY (land_parcel_type_id) REFERENCES land_parcel_type(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT unique_type_year UNIQUE(land_parcel_type_id, tax_year)
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_name TEXT NOT NULL,
    name TEXT NOT NULL,
    middle_name TEXT NOT NULL,
    rnokpp TEXT NOT NULL UNIQUE,
    address TEXT NOT NULL,
    email TEXT,
    phone TEXT
);

CREATE TABLE real_estate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    area REAL NOT NULL CHECK (area > 0),
    notes TEXT,
    user_id INTEGER NOT NULL,
    real_estate_type_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (real_estate_type_id) REFERENCES real_estate_type(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE land_parcel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    land_parcel_type_id INTEGER NOT NULL,
    address TEXT NOT NULL,
    area REAL NOT NULL,
    privileged INTEGER NOT NULL CHECK (privileged IN (0, 1)),
    notes TEXT,

    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    FOREIGN KEY (land_parcel_type_id) REFERENCES land_parcel_type(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE TABLE normative_monetary_values (
    land_id	INTEGER NOT NULL,
	year	INTEGER NOT NULL,
	value	REAL NOT NULL CHECK("value" >= 0),
	FOREIGN KEY (land_id) REFERENCES land_parcel(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	PRIMARY KEY("land_id","year")
);

CREATE TABLE real_estate_taxes (
    real_estate_id INTEGER NOT NULL,
    tax_year INTEGER NOT NULL,
    tax REAL NOT NULL,
    paid INTEGER NOT NULL CHECK (paid IN (0, 1)),
    sum_paid REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (real_estate_id) REFERENCES real_estate(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (real_estate_id, tax_year)
);

CREATE TABLE land_parcel_taxes (
    land_parcel_id INTEGER NOT NULL,
    tax_year INTEGER NOT NULL,
    tax REAL NOT NULL,
    paid INTEGER NOT NULL CHECK (paid IN (0, 1)),
    sum_paid REAL NOT NULL DEFAULT 0,
    FOREIGN KEY (land_parcel_id) REFERENCES land_parcel(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (land_parcel_id, tax_year)
);