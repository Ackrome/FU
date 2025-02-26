-- Создание таблицы пользователей
CREATE TABLE Users (
    user_phone VARCHAR(11) PRIMARY KEY NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    registration_date DATE DEFAULT CURRENT_DATE
);

-- Создание таблицы исполнителей
CREATE TABLE Artists (
    artist_email VARCHAR(50) PRIMARY KEY UNIQUE NOT NULL ,
    artist_name VARCHAR(100) UNIQUE NOT NULL,
    country VARCHAR(50) NOT NULL,
    birth_date DATE,
    genre VARCHAR(50) CHECK (genre IN ('Pop', 'Rock', 'Jazz', 'Classical', 'Electronic', 'Hip-Hop'))
);

-- Создание таблицы альбомов
CREATE TABLE Albums (
    album_id SERIAL PRIMARY KEY,
    album_name VARCHAR(100) NOT NULL,
    release_date DATE NOT NULL,
    artist_email VARCHAR(50) UNIQUE NOT NULL ,
    total_tracks INT CHECK (total_tracks > 0) NOT NULL,
    FOREIGN KEY (artist_email) REFERENCES Artists(artist_email)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Создание таблицы песен
CREATE TABLE Songs (
    song_id SERIAL PRIMARY KEY,
    song_name VARCHAR(100) NOT NULL,
    album_id INT NOT NULL,
    duration INTERVAL NOT NULL,
    plays_count INT CHECK (plays_count >= 0),
    FOREIGN KEY (album_id) REFERENCES Albums(album_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Создание таблицы плейлистов
CREATE TABLE Playlists (
    playlist_id SERIAL PRIMARY KEY,
    playlist_name VARCHAR(100) NOT NULL,
	user_phone VARCHAR(11) NOT NULL,
    created_date DATE DEFAULT CURRENT_DATE,
    is_public BOOLEAN DEFAULT FALSE NOT NULL,
    FOREIGN KEY (user_phone) REFERENCES Users(user_phone)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Создание таблицы для связи песен и плейлистов
CREATE TABLE Playlist_Songs (
    playlist_id INT NOT NULL,
    song_id INT NOT NULL,
    FOREIGN KEY (playlist_id) REFERENCES Playlists(playlist_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (song_id) REFERENCES Songs(song_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (playlist_id, song_id)
);

-- Добавление индексов для оптимизации поиска
CREATE INDEX idx_artist_name ON Artists(artist_name);
CREATE INDEX idx_album_name ON Albums(album_name);
CREATE INDEX idx_song_name ON Songs(song_name);
CREATE INDEX idx_playlist_name ON Playlists(playlist_name);