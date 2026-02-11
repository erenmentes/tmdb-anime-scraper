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

cur.close()
conn.close()
