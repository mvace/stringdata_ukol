import json
import csv
from datetime import datetime

current_date = datetime.now().strftime("%Y-%m-%d")

nakup_dict = {"items": {}, "errors": {}}


def load_data(file_path):
    with open(file_path, "r") as json_file:
        return json.load(json_file)["data"]


def validate_data(item):
    errors = []
    required_dict = {"nazev": str, "dph_sazba": str, "cena": float, "mnozstvi": int}

    if len(item) != len(required_dict):
        errors.append(
            f"Incorrect number of keys. Expected {len(required_dict)}, got {len(item)}"
        )

    for key, expected_type in required_dict.items():
        if key not in item.keys():
            errors.append(f"Key missing: {key}")
            continue

        if not isinstance(item[key], expected_type):
            errors.append(
                f"Incorrect type for {key}. Expected {expected_type}, got {type(item[key])}."
            )
    if item["dph_sazba"] not in ["zakladni", "prvni_snizena", "druha_snizena"]:
        errors.append(f"Incorect tax rate. Rate {item['dph_sazba']} does not exist.")

    return errors


def process_data(data, tax_rates):
    grocery_dict = {"items": {}, "errors": []}
    required_dict = {"nazev": str, "dph_sazba": str, "cena": float, "mnozstvi": int}

    for item in data:
        nazev = item["nazev"]
        mnozstvi = item["mnozstvi"]
        dph_sazba = item["dph_sazba"]
        cena_kus_bez_dph = item["cena"]

        errors = validate_data(item)
        if errors:
            status = "ERROR"
            err_list = [nazev, mnozstvi, dph_sazba, cena_kus_bez_dph, status, errors]
            grocery_dict["errors"].append(err_list)
        else:
            cena_kus_bez_dph = item["cena"]
            cena_kus_s_dph = cena_kus_bez_dph * tax_rates[dph_sazba]
            cena_celkem_bez_dph = cena_kus_bez_dph * mnozstvi
            cena_celkem_s_dph = cena_celkem_bez_dph * tax_rates[dph_sazba]

            if nazev in grocery_dict["items"]:
                grocery_dict["items"][nazev]["mnozstvi"] += mnozstvi
                grocery_dict["items"][nazev]["cena_celkem_bez_dph"] = (
                    cena_kus_bez_dph * grocery_dict["items"][nazev]["mnozstvi"]
                )
                grocery_dict["items"][nazev]["cena_celkem_s_dph"] = (
                    cena_celkem_s_dph * grocery_dict["items"][nazev]["mnozstvi"]
                )

            else:

                grocery_dict["items"][nazev] = {
                    "mnozstvi": mnozstvi,
                    "dph_sazba": dph_sazba,
                    "cena_kus_bez_dph": cena_kus_bez_dph,
                    "cena_kus_s_dph": cena_kus_s_dph,
                    "cena_celkem_bez_dph": cena_celkem_bez_dph,
                    "cena_celkem_s_dph": cena_celkem_s_dph,
                }
        print(grocery_dict)
    return grocery_dict


# after validation


def main():
    file_path = "nakup.json"
    sazby_dph = {"zakladni": 1.21, "prvni_snizena": 1.15, "druha_snizena": 1.1}
    data = load_data(file_path)
    items_dict = process_data(data, sazby_dph)


if __name__ == "__main__":
    main()
