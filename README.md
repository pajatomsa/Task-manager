# Terminálový monitor systému (TUI)

Jednoduchý a přehledný správce procesů pro terminál v jazyce **Python** (knihovny `Textual` a `psutil`).

## 📌 Stav milníků (k 11. 11. 2026)
- **14. 10. 2026:** Založení repozitáře a nastavení projektu.
- **21. 10. 2026:** Analýza požadavků a návrh architektury ([`docs/ANALYZA_A_ARCHITEKTURA.md`](docs/ANALYZA_A_ARCHITEKTURA.md)).
- **11. 11. 2026:** Implementace základního TUI (dashboard, tabulka procesů, řazení, vyhledávání, kill dialog).

## 🚀 Spuštění

```bash
# Instalace závislostí
pip install -r requirements.txt

# Spuštění aplikace
python main.py
```

## 🎮 Klávesové zkratky

| Klávesa | Akce |
|---|---|
| `↑` / `↓` | Pohyb a výběr procesu |
| `/` | Vyhledávání / filtr podle jména nebo PID |
| `ESC` / `Enter` | Návrat do tabulky procesů |
| `c` | Řazení podle CPU % |
| `m` | Řazení podle RAM % |
| `p` | Řazení podle PID |
| `k` | Ukončit proces (s potvrzovacím oknem) |
| `r` | Ruční obnova dat |
| `q` | Ukončení aplikace |

## 🧪 Testy

```bash
python -m unittest discover -s tests -v
```
