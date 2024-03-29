
# Automation team úkol

Chystáš se udělat první krok na cestě do Automation teamu ve Stringdata. Vypracuj následující zadání za použití programovacího jazyka Python 3 a výsledek včetně zpracovaného výstupu pošli v zipu zpět. V případě nejasností nás neváhej kontaktovat. Držíme ti palce a budeme se těšit na tvoje zpracování.

## Zadání

**Vstup:** *nakup.json*

**Výstup:** *RRRR-MM-DD.csv*

1. Načti vstupní data ze souboru *nakup.json*. V JSONu je seznam nákupu vygenerovaný pokladnou při markování, jedna položka má následující tvar:

    ```json
    {
        "nazev": <string>,
        "dph_sazba": <string>,
        "cena": <float>,
        "mnozstvi": <int>
    }
    ```
    Kde:

    - *nazev:* název zboží
    - *dph_sazba:* základní nebo snížená. Možné hodnoty: "zakladni", "prvni_snizena", "druha_snizena"
    - *cena:* cena za kus **bez DPH**
    - *mnozstvi:* počet kusů

2. U každého produktu vypočítej cenu s DPH dle sazby:

    - zakladni: 21%
    - prvni_snizena: 15%
    - druha_snizena: 10%

    Výslednou cenu zaokrouhli na desítky haléřů

3. Výsledek ulož do CSV souboru, který bude mít jako název aktuální datum ve formátu RRRR-MM-DD.csv. Ve výstupním CSV *jeden řádek = jeden produkt*. Pozor! Prodavačka markovala zboží, jak ji přišlo pod ruku. Někdy ručně zadala množství a namarkovala ho jednou, někdy markovala stejné produkty po jednom. Je tedy možné, že některý produkt se vyskytne ve vstupu vícekrát. Takové případy sluč do jednoho řádku.
Záznam ve výstupním CSV bude mít následující sloupce:

    - Název produktu
    - Zakoupené množství
    - Cena za kus bez DPH
    - Cena celkem bez DPH
    - Cena za kus s DPH
    - Cena celkem s DPH
    - Status

Sloupec Status může nabývat dvou hodnot: *OK* nebo *ERROR*. Pokladna občas udělá chybu a záznam o namarkované položce neuloží správně (udělá typo, splete si float s integerem, …). Záznamy, které nesplňují formát z bodu 1 nezpracovávej a do sloupce Status zapiš *ERROR*. V opačném případě zapiš *OK*. Přiložený JSON slouží pouze jako ukázka jednoho možného vstupu.

**Bonusy:**

- přidej do výstupu ještě jeden sloupec, ve kterém bude vysvětlení, proč je záznam označen jako ERROR

- uprav kód tak aby se dal i do budoucna snadno udržovat

- kód dodržuje PEP8



