import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import urllib3

# Désactiver les avertissements SSL (à utiliser en dev uniquement)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# En-tête pour simuler un navigateur
headers = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/115.0.0.0 Safari/537.36")
}

def parse_game_details(soup):
    """
    Extrait depuis la page détail les informations sous forme de lignes 
    comme "Developer: ...", "Publisher: ...", "Genre: ...", "Mode: ...", 
    "Franchise: ..." et "Release Date: ...".  
    Les clés retournées sont en français pour le CSV.
    """
    details = {
        "Développeur": "",
        "Éditeur": "",
        "Genres": "",
        "Mode de jeu": "",
        "Franchise": "",
        "Date de sortie": ""
    }
    # On cherche le bloc qui contient les détails du jeu.
    # Selon la page, cela pourrait être dans <div class="game-details">.
    container = soup.find("div", class_="game-details")
    if container:
        # On cherche les lignes dans des <p> ou <li>
        lines = container.find_all(["p", "li"])
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
    """
    Récupère la liste des blocs de jeux sur la page filtrée pour 2024.
    """
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
    Titre, URL (pour Identifiant unique), année, note, plateformes et résumé.
    """
    game = {}
    base_url = "https://www.grouvee.com"
    
    # Image URL (non exportée)
    box_art = block.find("div", class_="box-art")
    if box_art:
        img_tag = box_art.find("img")
        game["Image URL"] = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""
    else:
        game["Image URL"] = ""
    
    # Détails du jeu
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
        
        # Extraction de l'année et note depuis <h4 class="media-heading">
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
        
        # Plateformes
        platform_tags = details.find_all("a", class_="badge badge-info")
        if platform_tags:
            platforms = [pt.get_text(strip=True) for pt in platform_tags]
            game["Plateformes"] = ", ".join(platforms)
        else:
            game["Plateformes"] = ""
        
        # Résumé / Description (premier div.wrapper)
        wrapper_divs = details.find_all("div", class_="wrapper", recursive=False)
        if wrapper_divs:
            game["Résumé"] = wrapper_divs[0].get_text(" ", strip=True)
        else:
            game["Résumé"] = ""
    return game

def get_additional_game_info(game_url):
    """
    Récupère depuis la page détail les informations complémentaires :
    Date de sortie complète, Genres, Mode de jeu, Développeur, Éditeur, Franchise, Popularité.
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
    additional = {}
    
    # Utiliser le parseur de détails pour récupérer Développeur, Éditeur, Genres, Mode et Franchise, et éventuellement la date
    details_from_block = parse_game_details(soup)
    additional.update(details_from_block)
    
    # Si la date de sortie n'a pas été trouvée dans le bloc, on la cherche dans un autre bloc
    release_div = soup.find("div", class_="release-date")
    if release_div:
        # Par exemple, le texte "Sep 9, 2024" est attendu
        additional["Date de sortie"] = release_div.get_text(strip=True)
    else:
        additional["Date de sortie"] = ""
    
    # Popularité (exemple)
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
            # Ne conserver que les jeux dont l'année extraite est exactement "2024"
            if game.get("Année") != "2024":
                continue
            page_games += 1
            if game.get("URL du jeu"):
                additional = get_additional_game_info(game["URL du jeu"])
                game.update(additional)
            all_games.append(game)
        print(f"Page {page_number}: {page_games} jeux de 2024 ajoutés.")
        if page_games == 0:
            print(f"Aucun jeu de 2024 trouvé à la page {page_number}, arrêt de la boucle.")
            break
        page_number += 1

    print(f"Nombre total de jeux 2024 récupérés : {len(all_games)}")

    # Préparation du CSV avec séparateur point-virgule
    fieldnames = [
        "Titre", "Identifiant unique", "Date de sortie", "Plateformes", 
        "Genres", "Mode de jeu", "Développeur", "Éditeur", "Franchise",
        "Note Moyenne", "Résumé", "Popularité"
    ]
    
    # Pour chaque jeu, si "Date de sortie" est vide, utiliser l'année extraite (bien que normalement, la date complète soit présente)
    for game in all_games:
        if not game.get("Date de sortie"):
            game["Date de sortie"] = game.get("Année", "")
        # Supprimer les clés non souhaitées
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
