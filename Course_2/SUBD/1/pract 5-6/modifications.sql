-- Изменение структуры таблиц
ALTER TABLE Users
ADD gender CHAR(1) CHECK (gender IN ('M', 'F', 'O')) DEFAULT 'O';

ALTER TABLE Artists
ALTER COLUMN artist_name TYPE VARCHAR(150);

ALTER TABLE Songs
ALTER COLUMN duration DROP NOT NULL;

-- Создание таблицы Concerts
CREATE TABLE Concerts (
    concert_id SERIAL PRIMARY KEY,
    concert_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    concert_date DATE NOT NULL,
    artist_email VARCHAR(50) NOT NULL,
    ticket_price DECIMAL(10, 2) CHECK (ticket_price >= 0)
);

-- Добавление столбца в Concerts
ALTER TABLE Concerts
ADD available_tickets INT DEFAULT 100 CHECK (available_tickets >= 0);

-- Создание внешнего ключа для Concerts
ALTER TABLE Concerts
ADD CONSTRAINT fk_artist_email
FOREIGN KEY (artist_email) REFERENCES Artists(artist_email)
    ON DELETE CASCADE
    ON UPDATE CASCADE;

-- Модификация типа столбца в Songs
ALTER TABLE Songs
ALTER COLUMN plays_count TYPE BIGINT;

-- Удаление столбца в Artists
ALTER TABLE Artists
DROP COLUMN birth_date;

-- Удаление таблицы Playlist_Songs
DROP TABLE IF EXISTS Playlist_Songs;
