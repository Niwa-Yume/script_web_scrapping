# Importer les modules nécessaires
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from geopy.geocoders import Nominatim
import json
import datetime

# URL de la page d'événements
url = "https://ladecadanse.darksite.ch/evenement-agenda.php"

# Obtenir la réponse HTTP de la page
response = requests.get(url)

# Analyser le HTML de la page avec BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Initialiser une liste vide pour stocker les données des événements
data = []

# Charger le nombre de fois que le script a été exécuté depuis un fichier
try:
    with open('execution_count.json', 'r') as file:
        execution_count = json.load(file)
except FileNotFoundError:
    execution_count = 0

# Récupérer la date et l'heure de l'exécution du script
current_datetime = datetime.datetime.now()

# Initialiser le géocodeur Nominatim pour convertir les adresses en coordonnées géographiques
geolocator = Nominatim(user_agent="event_scraper")

# Trouver toutes les balises HTML qui contiennent des informations sur les événements
events = soup.find_all("div", class_="evenement vevent")

# Parcourir chaque balise HTML d'événement et extraire ses informations
for event in events:
    # Incrémenter l'ID de l'événement
    execution_count += 1

    # Extraire le titre de l'événement
    event_title_tag = event.find("div", class_="titre") or event.find("span", class_="left")
    event_title = event_title_tag.get_text(strip=True) if event_title_tag else None
    
    # Extraire le lieu de l'événement et le convertir en coordonnées géographiques
    event_location_raw = event.find("span", class_="right location").get_text(strip=True)
    event_location = event_location_raw.split(" - ")[0]
    location = geolocator.geocode(event_location)
    event_lat = location.latitude if location else None
    event_lon = location.longitude if location else None

    # Extraire la description de l'événement
    event_description = event.find("div", class_="description").get_text(strip=True)

    # Extraire la date de l'événement
    event_date = soup.h3.text
    
    # Extraire le contenu du span.right de la balise div avec la classe "pratique"
    event_pratique_tag = event.find("div", class_="pratique")
    event_pratique_span = event_pratique_tag.find("span", class_="right") if event_pratique_tag else None
    event_pratique_text = event_pratique_span.get_text(strip=True) if event_pratique_span else None
    
    event_time = None
    
    if event_pratique_text:
        # Utiliser les 4 premiers chiffres de event_pratique_text comme heure de l'événement
        event_time = event_pratique_text.strip()[:4]

    # Ajouter les informations de l'événement à la liste des données
    data.append([execution_count, event_title, event_date, event_time, event_location, event_lat, event_lon, event_description, current_datetime])

# Créer un DataFrame pandas à partir des données
df = pd.DataFrame(data, columns=["event_id", "event_title", "event_date", "event_time","event_location", "event_lat", "event_lon", "event_description", "event_creation"])

# Ajouter une colonne "event_music" avec la valeur "2" pour chaque événement
df["event_music"] = 2

# Ajouter une colonne "event_type" avec la valeur "3" pour chaque événement
df["event_type"] = 3

# Ajouter une colonne "event_private" avec la valeur "0" pour chaque événement
df["event_private"] = 0

# Ajouter une colonne "event_user_type" avec la valeur "3" pour chaque événement
df["event_user_type"] = 3

# Ajouter une colonne "event_user_id" avec la valeur "10" pour chaque événement
df["event_user_id"] = 10

# Ajouter une colonne "event_imageevent_id" avec la valeur "1" pour chaque événement
df["event_imageevent_id"] = 1# Ajouter une colonne "event_creation" avec la date et l'heure de l'exécution du script

#heure et date d'exécution du script
df["event_creation"] = current_datetime

#réorganisation de l'ordre
df = df[["event_id", "event_title", "event_date", "event_time","event_location", "event_lat", "event_lon", "event_description", "event_music", "event_type", "event_private", "event_creation", "event_user_type", "event_user_id", "event_imageevent_id"]]


# Enregistrer le DataFrame dans un fichier Excel
df.to_excel("events.xlsx", index=False)

# Enregistrer le nombre d'exécutions dans un fichier
with open('execution_count.json', 'w') as file:
    json.dump(execution_count, file)

# Afficher un message de confirmation que le fichier Excel a été enregistré avec succès
print("Saved Excel file to events.xlsx")