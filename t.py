import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import urllib3

# Désactiver les avertissements SSL (pour verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/115.0.0.0 Safari/537.36")
}

def parse_game_details(soup):
    details = {
        "Développeur": "",
        "Éditeur": "",
        "Genres": "",
        "Mode de jeu": "",
        "Franchise": "",
        "Date de sortie": ""
    }
    game_details_div = soup.find("div", class_="game-details")
    if game_details_div:
        lines = game_details_div.find_all(["p", "li"])
        for line in lines:
            text = line.get_text(" ", strip=True)
            if ":" in text:
                label, value = text.split(":", 1)
                label = label.strip().lower()
                value = value.strip()
                if label.startswith("developer") or label.startswith("développeur"):
                    details["Développeur"] = value
                elif label.startswith("publisher") or label.startswith("éditeur"):
                    details["Éditeur"] = value
                elif label.startswith("genre"):
                    details["Genres"] = value
                elif label.startswith("mode"):
                    details["Mode de jeu"] = value
                elif label.startswith("franchise"):
                    details["Franchise"] = value
                elif label.startswith("release date") or label.startswith("date de sortie"):
                    details["Date de sortie"] = value
    return details

def get_game_blocks(page_number):
    url = f"https://www.grouvee.com/games/?dateFrom=2024-01-01&dateTo=2024-12-31&page={page_number}"
    print("Fetching:", url)
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de la page {page_number} : {e}")
        return []
    if response.status_code != 200:
        print(f"Erreur HTTP pour la page {page_number} : {response.status_code}")
        return []
    soup = BeautifulSoup(response.text, "html.parser")
    blocks = soup.find_all("div", class_="bottomed clearfix")
    print(f"Page {page_number}: {len(blocks)} blocs trouvés")
    return blocks

def extract_game_info(block):
    game = {}
    base_url = "https://www.grouvee.com"
    box_art = block.find("div", class_="box-art")
    if box_art:
        img_tag = box_art.find("img")
        game["Image URL"] = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""
    else:
        game["Image URL"] = ""
    details = block.find("div", class_="details-section")
    if details:
        title_tag = details.find("a", class_="game-title")
        if title_tag:
            game["Titre"] = title_tag.get_text(strip=True)
            href = title_tag.get("href", "")
            game["URL du jeu"] = base_url + href if href.startswith("/") else href
            game["Identifiant unique"] = game["URL du jeu"]
        else:
            game["Titre"] = ""
            game["URL du jeu"] = ""
            game["Identifiant unique"] = ""
        h4 = details.find("h4", class_="media-heading")
        if h4:
            h4_text = h4.get_text(" ", strip=True)
            match = re.search(r'\((\d{4})\)', h4_text)
            game["Année"] = match.group(1) if match else "Inconnu"
            rating_span = h4.find("span", class_="date")
            game["Note Moyenne"] = rating_span.get_text(strip=True) if rating_span else ""
        else:
            game["Année"] = ""
            game["Note Moyenne"] = ""
        platform_tags = details.find_all("a", class_="badge badge-info")
        if platform_tags:
            platforms = [pt.get_text(strip=True) for pt in platform_tags]
            game["Plateformes"] = ", ".join(platforms)
        else:
            game["Plateformes"] = ""
        wrapper_divs = details.find_all("div", class_="wrapper", recursive=False)
        if wrapper_divs:
            game["Résumé"] = wrapper_divs[0].get_text(" ", strip=True)
        else:
            game["Résumé"] = ""
    return game

def get_additional_game_info(game_url):
    time.sleep(0.1)
    try:
        response = requests.get(game_url, headers=headers, timeout=10, verify=False)
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des détails pour {game_url} : {e}")
        return {}
    if response.status_code != 200:
        print(f"Erreur HTTP pour {game_url} : {response.status_code}")
        return {}
    soup = BeautifulSoup(response.text, "html.parser")
    additional = {}
    details_from_block = parse_game_details(soup)
    additional.update(details_from_block)
    release_div = soup.find("div", class_="release-date")
    additional["Date de sortie"] = release_div.get_text(strip=True) if release_div else ""
    popularity_div = soup.find("div", class_="game-popularity")
    additional["Popularité"] = popularity_div.get_text(strip=True) if popularity_div else ""
    return additional

def main():
    max_page = 38
    all_games = []
    page_number = 1
    while page_number <= max_page:
        blocks = get_game_blocks(page_number)
        if not blocks:
            print(f"Aucun bloc trouvé à la page {page_number}.")
            break
        page_games = 0
        for block in blocks:
            game = extract_game_info(block)
            if game.get("Année") != "2024":
                continue
            page_games += 1
            if game.get("URL du jeu"):
                additional = get_additional_game_info(game["URL du jeu"])
                game.update(additional)
            all_games.append(game)
        print(f"Page {page_number}: {page_games} jeux de 2024 ajoutés.")
        if page_games == 0:
            print(f"Aucun jeu de 2024 trouvé à la page {page_number}, arrêt.")
            break
        page_number += 1

    print(f"Nombre total de jeux 2024 récupérés : {len(all_games)}")

    fieldnames = [
        "Titre", "Identifiant unique", "Date de sortie", "Plateformes", 
        "Genres", "Mode de jeu", "Développeur", "Éditeur", "Franchise",
        "Note Moyenne", "Résumé", "Popularité"
    ]
    
    for game in all_games:
        if not game.get("Date de sortie"):
            game["Date de sortie"] = game.get("Année", "")
        for key in ["URL du jeu", "Image URL", "Année"]:
            if key in game:
                del game[key]
    
    csv_filename = "grouvee_2024_games_complete.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for game in all_games:
            writer.writerow(game)

    print(f"Données extraites et enregistrées dans '{csv_filename}'.")

if __name__ == "__main__":
    main()
