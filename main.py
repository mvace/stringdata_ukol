import json
import csv
from datetime import datetime


def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)["data"]


def validate_data(item, dph_sazby):
    errors = []
    required_dict = {"nazev": str, "dph_sazba": str, "cena": float, "mnozstvi": int}

    if len(item) < len(required_dict):
        errors.append(
            f"Lower number of keys. Expected {len(required_dict)}, got {len(item)}"
        )

    for key, data_type in required_dict.items():
        if key not in item.keys():
            errors.append(f"Key missing: {key}")
            continue

        if not isinstance(item[key], data_type):
            errors.append(
                f"Incorrect type for {key}. Expected {data_type}, got {type(item[key])}."
            )

    if item.get("dph_sazba") and item.get("dph_sazba") not in dph_sazby:
        errors.append(f"Incorect tax rate. Rate {item['dph_sazba']} does not exist.")

    return errors


def calculate_prices(cena_kus_bez_dph, mnozstvi, dph_sazba, dph_sazby):
    cena_kus_s_dph = cena_kus_bez_dph * dph_sazby[dph_sazba]
    cena_celkem_bez_dph = cena_kus_bez_dph * mnozstvi
    cena_celkem_s_dph = cena_celkem_bez_dph * dph_sazby[dph_sazba]
    return cena_kus_s_dph, cena_celkem_bez_dph, cena_celkem_s_dph


def process_data(data, dph_sazby):
    grocery_dict = {"items": {}, "errors": []}
    required_dict = {"nazev": str, "dph_sazba": str, "cena": float, "mnozstvi": int}

    for item in data:
        errors = validate_data(item, dph_sazby)
        nazev = item.get("nazev")
        mnozstvi = item.get("mnozstvi")
        dph_sazba = item.get("dph_sazba")
        cena_kus_bez_dph = item.get("cena")
        if errors:
            err_list = [nazev, mnozstvi, dph_sazba, cena_kus_bez_dph, "ERROR", errors]
            grocery_dict["errors"].append(err_list)
        else:
            cena_kus_s_dph, cena_celkem_bez_dph, cena_celkem_s_dph = calculate_prices(
                cena_kus_bez_dph, mnozstvi, dph_sazba, dph_sazby
            )

            if nazev in grocery_dict["items"]:
                if (
                    dph_sazba == grocery_dict["items"][nazev]["dph_sazba"]
                    and cena_kus_bez_dph
                    == grocery_dict["items"][nazev]["cena_kus_bez_dph"]
                ):
                    grocery_dict["items"][nazev]["mnozstvi"] += mnozstvi
                    grocery_dict["items"][nazev]["cena_celkem_bez_dph"] = (
                        cena_kus_bez_dph * grocery_dict["items"][nazev]["mnozstvi"]
                    )
                    grocery_dict["items"][nazev]["cena_celkem_s_dph"] = (
                        cena_celkem_s_dph * grocery_dict["items"][nazev]["mnozstvi"]
                    )
                else:
                    errors = [
                        "Items with the same name have different prices or tax rates"
                    ]
                    err_list = [
                        nazev,
                        mnozstvi,
                        dph_sazba,
                        cena_kus_bez_dph,
                        "ERROR",
                        errors,
                    ]
                    grocery_dict["errors"].append(err_list)

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
    with open(f"{current_date}.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Název",
                "Množství",
                "Cena za kus bez DPH",
                "Cena celkem bez DPH",
                "Cena za kus s DPH",
                "Cena celkem s DPH",
                "Status",
                "Error",
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
    dph_sazby = {"zakladni": 1.21, "prvni_snizena": 1.15, "druha_snizena": 1.1}
    data = load_data(file_path)
    items_dict = process_data(data, dph_sazby)
    export_to_csv(items_dict)

    print(items_dict)


if __name__ == "__main__":
    main()
