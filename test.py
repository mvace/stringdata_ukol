required_dict = {"nazev": str, "dph_sazba": str, "cena": float, "mnozstvi": int}

errors = []
item = {"nazev": "rohlik", "dph_sazba": "zakladni", "cena": 3, "mnozstvi": 10.5}

for key, expected_type in required_dict.items():
    if not isinstance(item[key], expected_type):
        errors.append(
            f"Incorrect type for {key}. Expected {expected_type}, got {type(item[key])}."
        )
print(errors)
