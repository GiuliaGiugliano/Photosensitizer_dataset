#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix header of every opt_t1.xyz inside protomer sub-folders.

• first line  : number of atoms
• second line : "Coordinates from ORCA-job opt_t1 E <energy_Ha>"
                where energy_Ha = value(found in energy_t1_opt.txt) / 27.211386
• remove blank lines (begin, middle, end)

Author: chatGPT
"""

from pathlib import Path

LIST_FILE = "list_tot"          # elenco delle cartelle «photo_X»
XYZ_NAME   = "opt_t1.xyz"
ENERGY_TXT = "energy_t1_opt.txt"
FMT        = "{:.6f}"                          # cifre decimali per l’energia

def read_energy(folder: Path) -> float | None:
    """Ritorna l'energia (Hartree) o None se non trovata/parsabile."""
    try:
        with open(folder/ENERGY_TXT) as f:
            first_token = f.readline().split()[0]
            ev = float(first_token)
            return ev / 27.211386
    except Exception as err:
        print(f"   ⚠️  energia mancante o non leggibile in {folder}/{ENERGY_TXT}: {err}")
        return None

def clean_xyz(xyz_path: Path, energy_ha: float) -> None:
    """Riscrive il file XYZ con header corretto e righe pulite."""
    with open(xyz_path) as f:
        # tutte le righe non-vuote (strip preserva spazi interni)
        coords = [ln.rstrip() for ln in f if ln.strip()]

    if not coords:
        print(f"   ⚠️  {xyz_path} è vuoto, salto.")
        return

    n_atoms = len(coords)
    header1 = f"{n_atoms}\n"
    header2 = f"Coordinates from ORCA-job opt_t1 E {FMT.format(energy_ha)}\n"
    xyz_path.write_text(header1 + header2 + "\n".join(coords) + "\n")
    print(f"   ✅ aggiornato  {xyz_path}  (N={n_atoms},  E={FMT.format(energy_ha)} Ha)")

def main() -> None:
    root = Path.cwd()                                      # directory in cui lanciamo lo script
    if not (root/LIST_FILE).is_file():
        print(f"File lista '{LIST_FILE}' non trovato nella dir corrente.")
        return

    with open(LIST_FILE) as f:
        top_dirs = [Path(line.strip()) for line in f if line.strip()]

    for top in top_dirs:
        if not top.is_dir():
            print(f"⚠️  cartella '{top}' non trovata, salto.")
            continue

        for sub in top.iterdir():
            if not sub.is_dir() or "_protomer_" not in sub.name:
                continue

            xyz_path = sub/XYZ_NAME
            if not xyz_path.is_file():
                continue  # niente XYZ da sistemare

            energy = read_energy(sub)
            if energy is None:
                continue

            try:
                clean_xyz(xyz_path, energy)
            except Exception as err:
                print(f"   ❌  errore su {xyz_path}: {err}")

if __name__ == "__main__":
    main()
