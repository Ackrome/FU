SELECT user_phone AS "Phone", username AS "User Name" FROM Users;

SELECT artist_email AS "Email", country AS "Country" FROM Artists;

SELECT album_name AS "Album Name", release_date AS "Release Date" FROM Albums;

SELECT song_name AS "Song Name", duration AS "Duration" FROM Songs;

SELECT playlist_name AS "Playlist Name", is_public AS "Is Public" FROM Playlists;

SELECT username AS "User Name", registration_date AS "Registration Date"
FROM Users
WHERE registration_date = '2024-01-01';

SELECT Artists.artist_name AS "Artist", Albums.album_name AS "Album"
FROM Artists
JOIN Albums ON Artists.artist_email = Albums.artist_email
WHERE Artists.genre = 'Rock';

SELECT song_name AS "Song Name", plays_count AS "Plays Count"
FROM Songs
WHERE plays_count > 100;

SELECT Users.username AS "User Name", COUNT(Playlists.playlist_id) AS "Playlists Count"
FROM Users
LEFT JOIN Playlists ON Users.user_phone = Playlists.user_phone
GROUP BY Users.username;

SELECT username AS "User Name", email AS "Email"
FROM Users
WHERE username LIKE 'A%';