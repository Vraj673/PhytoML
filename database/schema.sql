-- =====================================================================
-- schema.sql
-- ----------
-- Reference SQL schema for the AI-Based Plant Disease Detection and
-- Recommendation System (SQLite).
--
-- NOTE: In normal operation the Flask app creates these tables
-- automatically via SQLAlchemy (db.create_all() in app.py). This file
-- is provided as human-readable documentation of the schema and can
-- also be run manually against an empty plant_disease.db file with:
--     sqlite3 database/plant_disease.db < database/schema.sql
-- =====================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- users: registered end users (farmers / gardeners / students, etc.)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name       VARCHAR(120)  NOT NULL,
    username        VARCHAR(80)   NOT NULL UNIQUE,
    email           VARCHAR(120)  NOT NULL UNIQUE,
    password_hash   VARCHAR(255)  NOT NULL,   -- werkzeug PBKDF2 hash, never plain text
    phone           VARCHAR(20),
    address         VARCHAR(255),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- admins: administrator accounts (kept separate from `users`)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS admins (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        VARCHAR(80)   NOT NULL UNIQUE,
    password_hash   VARCHAR(255)  NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- diseases: knowledge base used to power the Recommendation Module
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS diseases (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    class_label     VARCHAR(120)  NOT NULL UNIQUE,  -- matches the ML model's output class
    crop_name       VARCHAR(80)   NOT NULL,
    disease_name    VARCHAR(120)  NOT NULL,
    symptoms        TEXT          NOT NULL,
    causes          TEXT          NOT NULL,
    treatment       TEXT          NOT NULL,
    is_healthy      BOOLEAN       DEFAULT 0
);

-- ---------------------------------------------------------------------
-- predictions: history of every AI prediction made, tied to a user
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS predictions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER       NOT NULL,
    image_path          VARCHAR(255)  NOT NULL,   -- relative path under /static
    predicted_class     VARCHAR(120)  NOT NULL,   -- matches diseases.class_label
    confidence          FLOAT         NOT NULL,   -- percentage 0-100
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_predictions_user_id ON predictions (user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions (created_at);
