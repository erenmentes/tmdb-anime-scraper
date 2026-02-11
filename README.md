# TMDB Anime Scraper

A Python script that fetches anime data from TMDB API and stores it in a PostgreSQL database.

## Requirements
- Python 3.x
- PostgreSQL
- `requests` and `psycopg2` libraries

## Installation
1. Install required packages:
   ```bash
   pip install requests psycopg2-binary
   ```

2. Add your TMDB API key to the `API_KEY` variable in `main.py`

3. Configure PostgreSQL database settings

## Usage
```bash
python main.py
```

The script fetches anime data from TMDB and saves it to the `Anime` table in the `AniNext` database.

---

# TMDB Anime Scraper

TMDB API'den anime verilerini çekip PostgreSQL veritabanına kaydeden Python scripti.

## Gereksinimler
- Python 3.x
- PostgreSQL
- `requests` ve `psycopg2` kütüphaneleri

## Kurulum
1. Gerekli paketleri yükle:
   ```bash
   pip install requests psycopg2-binary
   ```

2. `main.py` içindeki `API_KEY` değişkenine TMDB API anahtarını ekle

3. PostgreSQL veritabanı ayarlarını kontrol et

## Kullanım
```bash
python main.py
```

Script, TMDB'den anime verilerini çeker ve `AniNext` veritabanındaki `Anime` tablosuna kaydeder.
