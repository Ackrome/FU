-- а

-- Добавление нового столбца "gender" в таблицу Users
ALTER TABLE Users
ADD gender CHAR(1) CHECK (gender IN ('M', 'F', 'O')) DEFAULT 'O';

-- Модификация столбца "artist_name" в таблице Artists, изменяем его длину до 150 символов
ALTER TABLE Artists
ALTER COLUMN artist_name TYPE VARCHAR(150);

-- Удаление ограничения NOT NULL у столбца "duration" в таблице Songs
ALTER TABLE Songs
ALTER COLUMN duration DROP NOT NULL;


-- б

-- Создадим новую таблицу "Concerts" для хранения информации о концертах
CREATE TABLE Concerts (
    concert_id SERIAL PRIMARY KEY,
    concert_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    concert_date DATE NOT NULL,
    artist_email VARCHAR(50) NOT NULL,
    ticket_price DECIMAL(10, 2) CHECK (ticket_price >= 0)
);


-- в

-- Добавление столбца "available_tickets" в таблицу Concerts
ALTER TABLE Concerts
ADD available_tickets INT DEFAULT 100 CHECK (available_tickets >= 0);


-- г

-- Связываем "Concerts" с таблицей "Artists" через "artist_email"
ALTER TABLE Concerts
ADD CONSTRAINT fk_artist_email
FOREIGN KEY (artist_email) REFERENCES Artists(artist_email)
    ON DELETE CASCADE
    ON UPDATE CASCADE;


-- д

-- Изменение типа данных столбца "plays_count" в таблице Songs на BIGINT для увеличения диапазона
ALTER TABLE Songs
ALTER COLUMN plays_count TYPE BIGINT;


-- e

-- Удаление столбца "birth_date" из таблицы Artists
ALTER TABLE Artists
DROP COLUMN birth_date;


-- ж

-- Удаление таблицы Playlist_Songs
DROP TABLE IF EXISTS Playlist_Songs;
