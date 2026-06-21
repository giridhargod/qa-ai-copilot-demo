# scripts/scraper.py
import requests
from bs4 import BeautifulSoup

def extract_fields_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        inputs = soup.find_all("input")

        fields = []

        for inp in inputs:
            fields.append({
                "name": inp.get("name"),
                "type": inp.get("type")
            })

        return fields

    except Exception as e:
        print("Error while scraping:", e)
        return []