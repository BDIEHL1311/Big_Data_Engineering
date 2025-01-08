-- Datenbank erstellen
CREATE DATABASE IF NOT EXISTS honeypot;
USE honeypot;

-- Statistiken pro Land und Zeitfenster
CREATE TABLE country_stats (
    window_start TIMESTAMP,
    country VARCHAR(50),
    count BIGINT,
    PRIMARY KEY (window_start, country)
);

-- Erfolgreiche Login-Versuche pro IP
CREATE TABLE login_stats (
    ip VARCHAR(45),
    successful_attempts BIGINT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (ip)
);

-- Häufigste Passwörter
CREATE TABLE password_stats (
    password VARCHAR(100),
    attempts BIGINT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (password)
);
