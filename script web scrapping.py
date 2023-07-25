# Importer les modules nécessaires
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from geopy.geocoders import Nominatim
from datetime import datetime

# URL de la page d'événements
url = "https://ladecadanse.darksite.ch/evenement-agenda.php"

# Obtenir la réponse HTTP de la page
response = requests.get(url)

# Analyser le HTML de la page avec BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Initialiser une liste vide pour stocker les données des événements
data = []

# Initialiser le géocodeur Nominatim pour convertir les adresses en coordonnées géographiques
geolocator = Nominatim(user_agent="event_scraper")

# Trouver toutes les balises HTML qui contiennent des informations sur les événements
events = soup.find_all("div", class_="evenement vevent")

# Parcourir chaque balise HTML d'événement et extraire ses informations
for event in events:
    
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

    # Extraire la date de l'événement et la convertir en objet datetime
    event_date_raw = event.find("h2", class_="small")
    event_date = datetime.strptime(event_date_raw.get_text(strip=True), "%d.%m.%Y") if event_date_raw else None
    
    # Ajouter les informations de l'événement à la liste des données
    data.append([event_title, event_date, event_location, event_lat, event_lon, event_description])
        
    # Afficher un message de confirmation pour chaque événement ajouté à la liste des données
    print(f"Added event {event_title} to data: {data[-1]}")

# Attendre 1 seconde avant de récupérer la page suivante pour éviter de surcharger le serveur
time.sleep(1)

# Convertir la liste des données en un DataFrame pandas et l'écrire dans un fichier Excel
df = pd.DataFrame(data, columns=["event_title", "event_date", "event_location", "event_lat", "event_lon", "event_description"])

# Enregistrer le DataFrame dans un fichier Excel
df.to_excel("events.xlsx", index=False)

# Afficher un message de confirmation que le fichier Excel a été enregistré avec succès
print("Saved Excel file to events.xlsx")