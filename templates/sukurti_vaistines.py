import json
import os

failo_kelias = "services.json"

# Įkeliam esamus duomenis
if os.path.exists(failo_kelias):
    with open(failo_kelias, "r", encoding="utf-8") as f:
        duomenys = json.load(f)
else:
    duomenys = {}

# Pridedam vaistines
duomenys["vaistines"] = [
    {
        "pavadinimas": "Vista Primary Care Centre",
        "aprasymas": "Vaistinė, teikianti platų vaistų ir sveikatos prekių pasirinkimą.",
        "adresas": "Ballymore Eustace Road, Naas",
        "telefonas": "+353 45 881146",
        "svetaine": "vista@allcarepharmacy.ie",
        "maps": "https://www.google.com/maps?q=Vista+Primary+Care+Centre,+Naas"
    }
]

# Išsaugom
with open(failo_kelias, "w", encoding="utf-8") as f:
    json.dump(duomenys, f, indent=4, ensure_ascii=False)

print("✅ Vaistinės sėkmingai pridėtos į services.json")
