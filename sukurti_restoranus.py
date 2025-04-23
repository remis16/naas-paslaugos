import json

# 10 restoranų su svetaine vietoj meniu
restoranai = [
    {
        "pavadinimas": "Neighbourhood",
        "aprasymas": "Modernus airiškas restoranas, siūlantis kūrybingus patiekalus iš vietinių produktų.",
        "adresas": "Main Street 12, Naas",
        "telefonas": "+353 85 111 1111",
        "darbo_laikas": "12:00 - 22:00",
        "svetaine": "https://neighbourhoodnaas.ie",
        "maps": "https://www.google.com/maps?q=Neighbourhood,+Naas"
    },
    {
        "pavadinimas": "Vie de Châteaux",
        "aprasymas": "Prancūziškos virtuvės restoranas prie senojo uosto – rafinuoti skoniai ir vyno pasirinkimas.",
        "adresas": "Harbour Street, Naas",
        "telefonas": "+353 85 222 2222",
        "darbo_laikas": "13:00 - 22:30",
        "svetaine": "https://viedechateaux.ie",
        "maps": "https://www.google.com/maps?q=Vie+de+Châteaux,+Naas"
    },
    {
        "pavadinimas": "Lemongrass Fusion",
        "aprasymas": "Azijietiškos virtuvės restoranas su šiuolaikiniu požiūriu ir gardžiais desertais.",
        "adresas": "South Main St, Naas",
        "telefonas": "+353 85 333 3333",
        "darbo_laikas": "12:00 - 23:00",
        "svetaine": "https://lemongrass.ie",
        "maps": "https://www.google.com/maps?q=Lemongrass+Fusion,+Naas"
    },
    {
        "pavadinimas": "Cooke's of Caragh",
        "aprasymas": "Tradicinis airiškas maistas jaukioje aplinkoje, puikus šeimoms.",
        "adresas": "Caragh Village, Naas",
        "telefonas": "+353 85 444 4444",
        "darbo_laikas": "12:00 - 21:00",
        "svetaine": "https://cookesofcaragh.ie",
        "maps": "https://www.google.com/maps?q=Cooke's+of+Caragh,+Naas"
    },
    {
        "pavadinimas": "Butt Mullins Restaurant",
        "aprasymas": "Klasikinė europietiška virtuvė, draugiškas personalas ir jauki atmosfera.",
        "adresas": "Poplar Square, Naas",
        "telefonas": "+353 85 555 5555",
        "darbo_laikas": "12:30 - 22:00",
        "svetaine": "https://buttmullins.ie",
        "maps": "https://www.google.com/maps?q=Butt+Mullins+Restaurant,+Naas"
    },
    {
        "pavadinimas": "Bouchon",
        "aprasymas": "Moderni europietiška virtuvė su sezoniniais ingredientais ir kūrybingais patiekalais.",
        "adresas": "North Main Street, Naas",
        "telefonas": "+353 85 666 6666",
        "darbo_laikas": "17:00 - 22:00",
        "svetaine": "https://bouchonnaas.ie",
        "maps": "https://www.google.com/maps?q=Bouchon,+Naas"
    },
    {
        "pavadinimas": "Vi's Restaurant",
        "aprasymas": "Elegantiškas restoranas Lawlor's viešbutyje, tinka verslo pietums ir vakarienėms.",
        "adresas": "Lawlor's Hotel, Naas",
        "telefonas": "+353 85 777 7777",
        "darbo_laikas": "12:00 - 22:30",
        "svetaine": "https://lawlors.ie/dining",
        "maps": "https://www.google.com/maps?q=Vi's+Restaurant,+Naas"
    },
    {
        "pavadinimas": "Lock13 Gastro Pub",
        "aprasymas": "Gastro baras netoli Naas – puikus craft alus ir skanus maistas.",
        "adresas": "Sallins Rd, Naas",
        "telefonas": "+353 85 888 8888",
        "darbo_laikas": "12:00 - 23:00",
        "svetaine": "https://lock13.ie",
        "maps": "https://www.google.com/maps?q=Lock13+Gastro+Pub,+Sallins"
    },
    {
        "pavadinimas": "Rustic",
        "aprasymas": "Šiuolaikinė virtuvė ir šiltas interjeras – puikiai tinka jaukiems vakarams.",
        "adresas": "Friary Road, Naas",
        "telefonas": "+353 85 999 9999",
        "darbo_laikas": "13:00 - 22:00",
        "svetaine": "https://rusticnaas.ie",
        "maps": "https://www.google.com/maps?q=Rustic,+Naas"
    },
    {
        "pavadinimas": "Siblings",
        "aprasymas": "Šiuolaikiškas restoranas su draugišku aptarnavimu ir plačiu patiekalų pasirinkimu.",
        "adresas": "Main Street, Naas",
        "telefonas": "+353 85 000 0000",
        "darbo_laikas": "12:00 - 21:30",
        "svetaine": "https://siblings.ie",
        "maps": "https://www.google.com/maps?q=Siblings,+Naas"
    }
]

duomenys = {"restoranai": restoranai}

# Išsaugome kaip services.json
failo_kelias = "/mnt/data/services.json"
with open(failo_kelias, "w", encoding="utf-8") as f:
    json.dump(duomenys, f, indent=4, ensure_ascii=False)

failo_kelias
