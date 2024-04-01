import json
import csv
from datetime import datetime

DPH_SAZBY = {"zakladni": 0.21, "prvni_snizena": 0.15, "druha_snizena": 0.1}
FILE_PATH = "nakup.json"


def load_data(file_path):
    """
    Načte data ve formátu JSON ze zadaného souboru.

    Parametry:
        file_path (str): Cesta k souboru, ze kterého budou data načtena.

    Vrátí:
        list: Seznam dat načtených z JSON souboru.
    """
    with open(file_path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)["data"]


def validate_data(item, dph_sazby):
    """
    Ověří, zda položka splňuje očekávané formáty a hodnoty.

    Parametry:
        item (dict): Položka k validaci.
        dph_sazby (dict): Slovník s hodnotami sazeb DPH.

    Vrátí:
        list: Seznam chybových zpráv.
        Pokud nejsou žádné chyby, vrátí prázdný seznam.
    """
    errors = []
    required_dict = {"nazev": str, "dph_sazba": str, "cena": float, "mnozstvi": int}

    for key, data_type in required_dict.items():
        if key not in item.keys():
            errors.append(f"Key missing: {key}")
            continue

        if not isinstance(item[key], data_type):
            errors.append(
                f"Incorrect data type for {key}. Expected {data_type}, got {type(item[key])}."
            )

    dph_sazba = item.get("dph_sazba")
    if dph_sazba and dph_sazba not in dph_sazby:
        errors.append(f"Incorect tax rate. Rate {item['dph_sazba']} does not exist.")

    mnozstvi = item.get("mnozstvi")
    if mnozstvi and isinstance(mnozstvi, int) and mnozstvi <= 0:
        errors.append(
            f"Quantity is {mnozstvi}. Quantity cannot be lower or equal to zero."
        )

    cena = item.get("cena")
    if cena and isinstance(cena, float) and cena <= 0:
        errors.append(f"Price is {cena}. Price cannot be lower or equal to zero.")

    return errors


def calculate_prices(cena_kus_bez_dph, mnozstvi, dph_sazba, dph_sazby):
    """
    Vypočítá ceny s DPH a bez DPH pro jednotku a celkově a zaokrouhlí
    na desítky haléřů.

    Parametry:
        cena_kus_bez_dph (float): Cena za kus bez DPH.
        mnozstvi (int): Počet kusů.
        dph_sazba (str): Název sazby DPH.
        dph_sazby (dict): Slovník s hodnotami sazeb DPH.

    Vrátí:
        tuple: Cena za kus s DPH, celková cena bez DPH, celková cena s DPH.
    """
    cena_kus_s_dph = cena_kus_bez_dph * (1 + dph_sazby[dph_sazba])
    cena_celkem_bez_dph = cena_kus_bez_dph * mnozstvi
    cena_celkem_s_dph = round(cena_celkem_bez_dph * (1 + dph_sazby[dph_sazba]), 1)
    return cena_kus_s_dph, cena_celkem_bez_dph, cena_celkem_s_dph


def process_data(data, dph_sazby):
    """
    Zpracuje vstupní data: validuje a vypočítá ceny s DPH a bez DPH.

    Parametry:
        data (list): Seznam položek k zpracování.
        dph_sazby (dict): Slovník s hodnotami sazeb DPH.

    Vrátí:
        dict: Slovník obsahující zpracované položky a chyby.
    """
    grocery_dict = {"items": {}, "errors": []}
    required_dict = {"nazev": str, "dph_sazba": str, "cena": float, "mnozstvi": int}

    for item in data:
        errors = validate_data(item, dph_sazby)
        nazev = item.get("nazev")
        mnozstvi = item.get("mnozstvi")
        dph_sazba = item.get("dph_sazba")
        cena_kus_bez_dph = item.get("cena")
        if errors:
            err_list = [nazev, mnozstvi, cena_kus_bez_dph, errors]
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
                        cena_kus_s_dph * grocery_dict["items"][nazev]["mnozstvi"]
                    )
                else:
                    err_list = [
                        nazev,
                        mnozstvi,
                        cena_kus_bez_dph,
                        ["Items with the same name have different prices or tax rates"],
                    ]
                    grocery_dict["errors"].append(err_list)
                    print(err_list)

            else:

                grocery_dict["items"][nazev] = {
                    "mnozstvi": mnozstvi,
                    "dph_sazba": dph_sazba,
                    "cena_kus_bez_dph": cena_kus_bez_dph,
                    "cena_kus_s_dph": cena_kus_s_dph,
                    "cena_celkem_bez_dph": cena_celkem_bez_dph,
                    "cena_celkem_s_dph": cena_celkem_s_dph,
                    "status": "OK",
                    "error": "",
                }
    return grocery_dict


def export_to_csv(items_dict):
    """
    Exportuje zpracované položky a chyby do souboru CSV.

    Parametry:
        items_dict (dict): Slovník obsahující zpracované položky a chyby.
    """
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
                    error[2],
                    None,
                    None,
                    None,
                    "ERROR",
                    " ".join(error[3]),
                ]
            )


def main():
    """
    Hlavní funkce pro načtení dat, jejich zpracování a export do CSV.
    """
    data = load_data(FILE_PATH)
    items_dict = process_data(data, DPH_SAZBY)
    export_to_csv(items_dict)


if __name__ == "__main__":
    main()
