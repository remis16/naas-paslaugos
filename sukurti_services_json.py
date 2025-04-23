import json

duomenys = {
    "restoranai": [
        {
            "pavadinimas": "Neighbourhood",
            "aprasymas": "Modernus airiškas restoranas, siūlantis kūrybingus patiekalus iš vietinių produktų.",
            "adresas": "Main Street 12, Naas",
            "telefonas": "+353 85 111 1111",
            "darbo_laikas": "12:00 - 22:00",
            "maps": "https://www.google.com/maps?q=Neighbourhood,+Naas"
        }
    ],
    "grozio_paslaugos": [
        {
            "pavadinimas": "The Hair Boutique",
            "aprasymas": "Modernus kirpyklos salonas moterims ir vyrams.",
            "adresas": "Abbey Street, Naas",
            "telefonas": "+353 85 101 1010",
            "darbo_laikas": "09:00 - 18:00",
            "maps": "https://www.google.com/maps?q=The+Hair+Boutique,+Naas"
        }
    ]
}

with open("services.json", "w", encoding="utf-8") as f:
    json.dump(duomenys, f, indent=4, ensure_ascii=False)

print("✅ services.json sukurtas!")
