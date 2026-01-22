# Részletes Projekt Leírás

**Projekt Neve:** MyWallet - Pénzügyi Kiadáskövető Alkalmazás
**Cél:** Egy felhasználóbarát webes alkalmazás, amely modern fejlesztési elveket (Clean Code) követve teszi lehetővé a személyes pénzügyek kezelését és vizualizációját.
**Technológiai Stack:** Python 3, Flask, SQLite + SQLAlchemy, Bootstrap 5, Chart.js, Pytest.

**Megvalósítási Lépések és Funkciók:**

1. **Backend és Adatbázis:**
* **Expense Modell:** `id`, `title` (max 50 kar.), `amount`, `category`, `date`.
* **Clean Code:** "Magic Number"-ek kerülése konstansok (`MAX_TITLE_LENGTH`, `MAX_AMOUNT_LIMIT`) használatával.
* **Validáció:** Szigorú bemeneti ellenőrzés (hossz, típus, érték), amely összhangban van az adatbázis korlátaival.
* **Flash Üzenetek:** Visszajelzések a felhasználónak (Siker, Hiba).
* **Aggregáció:** Összes költés és kategória-specifikus adatok számítása.


2. **Frontend (UX fókusszal):**
* **Dashboard:** Összesítő kártya és dinamikus kördiagram.
* **Biztonságos Törlés:** A törlés megerősítésekor a rendszer kiírja a törlendő tétel nevét, megelőzve a véletlen kattintásokat.
* **Reszponzív Design:** Bootstrap 5 alapú felület.


3. **Minőségbiztosítás (Testing):**
* **Pytest:** Kiterjedt tesztelés, beleértve a szerkesztés ellenőrzését (nemcsak a státuszkódot, hanem a tartalom frissülését is vizsgálva).



---

## A Fájllista


```text
MyWallet_Project/
│
├── app.py                # Backend logika + Validáció + Flash config
├── requirements.txt      # Flask, Flask-SQLAlchemy, pytest
├── README.md             # A fenti leírás (angolul vagy magyarul)
├── test_wallet.py        # Pytest tesztek (Edit és Validáció tesztekkel)
└── templates/
    ├── index.html        # Dashboard + Total Summary + Flash Messages + Chart
    └── edit.html         # Szerkesztő űrlap + Flash Messages

```