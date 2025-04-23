import json
import os

failo_kelias = os.path.join(os.path.dirname(__file__), 'services.json')

with open(failo_kelias, 'r', encoding='utf-8') as f:
    duomenys = json.load(f)

id_counter = 1
for kategorija in duomenys:
    for paslauga in duomenys[kategorija]:
        paslauga['id'] = id_counter
        id_counter += 1

with open(failo_kelias, 'w', encoding='utf-8') as f:
    json.dump(duomenys, f, indent=4, ensure_ascii=False)

print("✅ ID sėkmingai pridėti visoms paslaugoms!")
