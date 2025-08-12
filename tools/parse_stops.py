import sys, json, os
from app.services.ztm import find_brama_wyzynna_from_stopsfile

if len(sys.argv) < 2:
    print("Użycie: python tools/parse_stops.py path/to/stops.json")
    sys.exit(1)

path = sys.argv[1]
if not os.path.exists(path):
    print("Plik nie istnieje:", path)
    sys.exit(1)

res = find_brama_wyzynna_from_stopsfile(path)
print("Znalezione stopId:", res)
# zapis do config/stops.json
os.makedirs("config", exist_ok=True)
with open("config/stops.json", "w", encoding="utf-8") as f:
    json.dump({"api_base": "https://ckan.multimediagdansk.pl", **res}, f, indent=2)
print("Zapisano config/stops.json")
# uruchom ten skrypt raz, podając ścieżkę do lokalnego stops.json (pobrane z CKAN)
