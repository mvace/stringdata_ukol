import json
import csv
from datetime import datetime


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

    if item.get("dph_sazba") and item.get("dph_sazba") not in [
        "zakladni",
        "prvni_snizena",
        "druha_snizena",
    ]:
        errors.append(f"Incorect tax rate. Rate {item['dph_sazba']} does not exist.")

    return errors


def process_data(data, tax_rates):
    grocery_dict = {"items": {}, "errors": []}
    required_dict = {"nazev": str, "dph_sazba": str, "cena": float, "mnozstvi": int}

    for item in data:

        errors = validate_data(item)

        nazev = item.get("nazev")
        mnozstvi = item.get("mnozstvi")
        dph_sazba = item.get("dph_sazba")
        cena_kus_bez_dph = item.get("cena")
        if errors:
            status = "ERROR"
            err_list = [nazev, mnozstvi, dph_sazba, cena_kus_bez_dph, status, errors]
            grocery_dict["errors"].append(err_list)
        else:
            cena_kus_bez_dph = item.get("cena")
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
                    "cena_kus_bez_dph": round(cena_kus_bez_dph, 1),
                    "cena_kus_s_dph": round(cena_kus_s_dph, 1),
                    "cena_celkem_bez_dph": round(cena_celkem_bez_dph, 1),
                    "cena_celkem_s_dph": round(cena_celkem_s_dph, 1),
                    "status": "OK",
                    "error": "",
                }
    return grocery_dict


def export_to_csv(items_dict):
    current_date = datetime.now().strftime("%Y-%m-%d")
    with open(f"{current_date}.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "nazev",
                "mnozstvi",
                "cena za kus bez DPH",
                "cena celkem bez DPH",
                "cena za kus s DPH",
                "cena celkem s DPH",
                "status",
                "error",
            ]
        )

        for item in items_dict["items"]:
            writer.writerow(
                [
                    item,
                    items_dict["items"][item]["mnozstvi"],
                    items_dict["items"][item]["cena_kus_bez_dph"],
                    items_dict["items"][item]["cena_celkem_bez_dph"],
                    items_dict["items"][item]["cena_kus_s_dph"],
                    items_dict["items"][item]["cena_celkem_s_dph"],
                    items_dict["items"][item]["status"],
                    items_dict["items"][item]["error"],
                ]
            )
        for error in items_dict["errors"]:
            writer.writerow(
                [
                    error[0],
                    error[1],
                    error[3],
                    None,
                    None,
                    None,
                    "ERROR",
                    " ".join(error[5]),
                ]
            )


def main():
    file_path = "nakup.json"
    sazby_dph = {"zakladni": 1.21, "prvni_snizena": 1.15, "druha_snizena": 1.1}
    data = load_data(file_path)
    items_dict = process_data(data, sazby_dph)
    export_to_csv(items_dict)

    print(items_dict)


if __name__ == "__main__":
    main()
