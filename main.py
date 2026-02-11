import requests
import time
import psycopg2
import json

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.themoviedb.org/3/discover/tv"

conn = psycopg2.connect(
    dbname="AniNext",
    user="macbook",
    host="localhost",
    port=5432
)
cur = conn.cursor()

def fetchAnimes():
    for page in range(1, 214):
        try:
            response = requests.get(
                BASE_URL,
                params={
                    "api_key": API_KEY,
                    "with_keywords": 210024,
                    "language": "tr-TR",
                    "page": page,
                    "sort_by": "popularity.desc",
                    "include_adult": "false"
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])

            for anime in results:
                genres_list = anime.get("genre_ids") or []
                origin_country_json = json.dumps(anime.get("origin_country") or [])

                cur.execute("""
                    INSERT INTO "Anime" (
                        adult, "backdropPath", genres, "tmdbId", "originCountry",
                        "originalLanguage", "originalName", overview, popularity,
                        "posterPath", "firstAirDate", name, "voteAverage", "voteCount",
                        "numberOfSeasons", "numberOfEpisodes", status, title
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT ("tmdbId") DO NOTHING
                """, (
                    str(anime.get("adult")),
                    anime.get("backdrop_path"),
                    genres_list,
                    anime.get("id"),
                    origin_country_json,
                    anime.get("original_language"),
                    anime.get("original_name"),
                    anime.get("overview"),
                    anime.get("popularity"),
                    anime.get("poster_path"),
                    anime.get("first_air_date"),
                    anime.get("name"),
                    anime.get("vote_average"),
                    anime.get("vote_count"),
                    anime.get("number_of_seasons"),
                    anime.get("number_of_episodes"),
                    anime.get("status"),
                    anime.get("name")
                ))
                print(f"Inserted or skipped: {anime.get('name')} (page {page})")

            conn.commit()

        except requests.exceptions.RequestException as e:
            print(f"Request error on page {page}: {e}")
        except psycopg2.Error as e:
            print(f"DB error on page {page}: {e}")
            conn.rollback()

        time.sleep(0.3)
def getAnimeSeasons(tmdb_id):
    cur.execute('SELECT id FROM "Anime" WHERE "tmdbId" = %s', (tmdb_id,))
    result = cur.fetchone()
    
    if not result:
        print(f"Couldn't find {tmdb_id} in Anime table.")
        return
    
    anime_db_id = result[0]
    print(f"TMDB {tmdb_id} → Prisma ID: {anime_db_id}")

    seasons = []
    
    series_url = f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key={API_KEY}&language=tr-TR"
    series_res = requests.get(series_url)
    if series_res.status_code == 200:
        season_count = series_res.json().get("number_of_seasons", 0)
        print(f"Anime has : {season_count} season.")
    else:
        season_count = 20
    
    for season_num in range(1, season_count + 1):
        url = f"https://api.themoviedb.org/3/tv/{tmdb_id}/season/{season_num}?api_key={API_KEY}&language=tr-TR"
        response = requests.get(url)
        if response.status_code != 200:
            break
        seasons.append(response.json())
    
    print(f"{len(seasons)} sezon fetched.")

    inserted = 0
    for season_data in seasons:
        episodes = season_data.get("episodes", [])
        for ep in episodes:
            cur.execute("""
                INSERT INTO "Episode" (
                    "animeId",
                    "airDate",
                    "episodeNumber",
                    "episode_type",
                    "tmdbId",
                    overview,
                    runtime,
                    "seasonNumber",
                    "stillPath",
                    "voteAverage",
                    "voteCount"
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT ("tmdbId") DO NOTHING
            """, (
                anime_db_id,
                ep.get("air_date"),
                ep.get("episode_number"),
                ep.get("episode_type"),
                ep.get("id"),
                ep.get("overview"),
                ep.get("runtime"),
                ep.get("season_number"),
                ep.get("still_path"),
                ep.get("vote_average"),
                ep.get("vote_count")
            ))
            inserted += 1
        conn.commit()
        time.sleep(0.3)

    print(f"{inserted} episode saved.")

getAnimeSeasons(95479)
cur.close()
conn.close()