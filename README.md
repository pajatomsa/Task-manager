# Terminálový monitor systému (TUI)

Interaktivní správce procesů a monitor systémových prostředků v jazyce **Python** (`Textual` a `psutil`).

## 🚀 Spuštění

```bash
# Instalace závislostí
pip install -r requirements.txt

# Spuštění aplikace
python main.py
```

## 🎮 Ovládání a klávesové zkratky

| Klávesa | Akce | Popis |
|---|---|---|
| `↑` / `↓` | **Pohyb v tabulce** | Výběr aktivního procesu v seznamu |
| `/` | **Hledat** | Aktivace vyhledávacího pole pro filtr procesů |
| `ESC` / `Enter` | **Zpět** | Návrat z vyhledávání do tabulky procesů |
| `c` | **Řadit dle CPU** | Seřadí procesy podle vytížení CPU |
| `m` | **Řadit dle RAM** | Seřadí procesy podle využití paměti RAM |
| `p` | **Řadit dle PID** | Seřadí procesy podle čísla PID |
| `k` | **Ukončit (Kill)** | Otevře potvrzovací okno pro ukončení vybraného procesu |
| `r` | **Obnovit** | Ruční obnova dat |
| `q` | **Konec** | Ukončení aplikace |
