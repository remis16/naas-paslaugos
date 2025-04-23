import json

# Teisinga struktūra su restoranais ir grožio paslaugomis
duomenys = {
    "restoranai": [
        {
            "pavadinimas": "Neighbourhood",
            "aprasymas": "Modernus airiškas restoranas, siūlantis kūrybingus patiekalus iš vietinių produktų.",
            "adresas": "Main Street 12, Naas",
            "telefonas": "+353 85 111 1111",
            "darbo_laikas": "12:00 - 22:00",
            "meniu": [
                {"patiekalas": "Grilled Chicken", "kaina": "€18.00"},
                {"patiekalas": "Prawn Linguine", "kaina": "€20.50"},
                {"patiekalas": "Chocolate Fondant", "kaina": "€7.00"}
            ],
            "maps": "https://www.google.com/maps?q=Neighbourhood,+Naas"
        },
        {
            "pavadinimas": "Vie de Châteaux",
            "aprasymas": "Prancūziškos virtuvės restoranas prie senojo uosto – rafinuoti skoniai ir vyno pasirinkimas.",
            "adresas": "Harbour Street, Naas",
            "telefonas": "+353 85 222 2222",
            "darbo_laikas": "13:00 - 22:30",
            "meniu": [
                {"patiekalas": "French Onion Soup", "kaina": "€8.50"},
                {"patiekalas": "Duck à l’Orange", "kaina": "€26.00"},
                {"patiekalas": "Crème Brûlée", "kaina": "€7.50"}
            ],
            "maps": "https://www.google.com/maps?q=Vie+de+Châteaux,+Naas"
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
        },
        {
            "pavadinimas": "Glam Nails Studio",
            "aprasymas": "Profesionalus nagų salonas su SPA paslaugomis.",
            "adresas": "South Main Street, Naas",
            "telefonas": "+353 85 202 2020",
            "darbo_laikas": "10:00 - 19:00",
            "maps": "https://www.google.com/maps?q=Glam+Nails+Studio,+Naas"
        }
    ]
}

# Įrašom į failą
kelias = "/mnt/data/services_fixed.json"
with open("services_fixed.json", "r", encoding="utf-8") as f:
    duomenys = json.load(f)

kelias
