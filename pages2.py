import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import urllib3

# Désactiver les avertissements SSL (à utiliser uniquement en dev)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}

def get_game_blocks(page_number):
    """Récupère les blocs de jeu de la page liste filtrée pour 2024."""
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
    """
    Extrait depuis la page liste les informations de base :
      - Titre
      - Identifiant unique (basé sur l’URL du jeu)
      - Année (pour filtrer uniquement 2024)
      - Note Moyenne
      - Plateformes
    """
    game = {}
    base_url = "https://www.grouvee.com"
    details = block.find("div", class_="details-section")
    if details:
        title_tag = details.find("a", class_="game-title")
        if title_tag:
            game["Titre"] = title_tag.get_text(strip=True)
            href = title_tag.get("href", "")
            full_url = base_url + href if href.startswith("/") else href
            game["Identifiant unique"] = full_url
        else:
            game["Titre"] = ""
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
    return game

def get_game_detail_info(game_url):
    """
    Récupère depuis la page détail les informations du bloc "Game Details" :
      - Date de sortie, Développeur, Éditeur, Genres, Franchise et Mode de jeu (si présent)
    """
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
    details = {
        "Date de sortie": "",
        "Développeur": "",
        "Éditeur": "",
        "Genres": "",
        "Mode de jeu": "",
        "Franchise": "",
        "Popularité": ""
    }
    # On cherche le tableau dans le bloc "Game Details"
    stats_boxes = soup.find_all("div", class_="stats-box")
    table = None
    for box in stats_boxes:
        h3 = box.find("h3")
        if h3 and "game details" in h3.get_text(strip=True).lower():
            table = box.find("table")
            break
    if table:
        rows = table.find_all("tr")
        for row in rows:
            tds = row.find_all("td")
            if len(tds) < 2:
                continue
            label = tds[0].get_text(strip=True).lower()
            value = tds[1].get_text(" ", strip=True)
            if "release date" in label:
                details["Date de sortie"] = value
            elif "developer" in label or "développeur" in label:
                details["Développeur"] = value
            elif "publisher" in label or "éditeur" in label:
                details["Éditeur"] = value
            elif "genre" in label:
                details["Genres"] = value
            elif "franchise" in label:
                details["Franchise"] = value
            elif "mode" in label:
                details["Mode de jeu"] = value
    else:
        print("Table 'Game Details' non trouvée pour", game_url)
    # Extraction de la popularité si présente (dans un bloc séparé)
    popularity_div = soup.find("div", class_="game-popularity")
    details["Popularité"] = popularity_div.get_text(strip=True) if popularity_div else ""
    return details

def main():
    max_page = 2  # Pour tester avec 2 pages
    all_games = []
    for page_number in range(1, max_page + 1):
        blocks = get_game_blocks(page_number)
        if not blocks:
            print(f"Aucun bloc trouvé à la page {page_number}.")
            continue
        page_count = 0
        for block in blocks:
            game = extract_game_info(block)
            # On ne traite que les jeux dont l'année est exactement "2024"
            if game.get("Année") != "2024":
                continue
            page_count += 1
            if game.get("Identifiant unique"):
                details = get_game_detail_info(game["Identifiant unique"])
                game.update(details)
            all_games.append(game)
        print(f"Page {page_number}: {page_count} jeux de 2024 ajoutés.")

    print(f"Nombre total de jeux 2024 récupérés : {len(all_games)}")

    # Champs souhaités pour le CSV
    fieldnames = [
        "Titre", "Identifiant unique", "Date de sortie", "Développeur",
        "Éditeur", "Genres", "Mode de jeu", "Franchise", "Note Moyenne",
        "Plateformes", "Popularité"
    ]
    # Si la date de sortie n'est pas trouvée, on peut utiliser l'année (même si cela n'inclut pas le jour et le mois)
    for game in all_games:
        if not game.get("Date de sortie"):
            game["Date de sortie"] = game.get("Année", "")
        # On peut supprimer les clés inutiles
        for key in ["Année", "Image URL"]:
            if key in game:
                del game[key]

    csv_filename = "grouvee_2024_games_details_test.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for game in all_games:
            writer.writerow(game)

    print(f"Données extraites et enregistrées dans '{csv_filename}'.")

if __name__ == "__main__":
    main()
