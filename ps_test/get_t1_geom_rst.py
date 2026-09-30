#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estrae l’ultima geometria ottimizzata (opt_t1) dai log ORCA e la scrive in opt_t1.xyz.
Se il file esiste ed è non-vuoto viene lasciato stare.
Il file list_tot deve contenere il percorso delle cartelle “photo_X”.
"""

from pathlib import Path
import sys

LIST_FILE = "list_tot"
LOG_NAME = "opt_t1.log"
XYZ_NAME = "opt_t1.xyz"
ENERGY_FILE = "energy_t1_opt.txt"
HARTREE = 27.2114

# ---------------------------------------------------------------------------
def last_coord_block(log_path: Path) -> list[str] | None:
    """Estrae l'ultimo blocco 'CARTESIAN COORDINATES (ANGSTROEM)' in avanti."""
    try:
        lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception as err:
        print(f"⚠️  Impossibile leggere {log_path}: {err}")
        return None

    # verifica che il job sia terminato
    if not any("ORCA TERMINATED NORMALLY" in ln for ln in lines):
        return None

    blocks = []
    capturing = False
    current_block = []

    for ln in lines:
        if "CARTESIAN COORDINATES (ANGSTROEM)" in ln:
            if current_block:
                blocks.append(current_block)
                current_block = []
            capturing = True
            continue

        if capturing:
            stripped = ln.strip()
            if not stripped or not stripped[0].isalpha():
                capturing = False
                if current_block:
                    blocks.append(current_block)
                    current_block = []
            else:
                current_block.append(stripped)

    if current_block:
        blocks.append(current_block)

    if not blocks:
        return None

    return blocks[-1]

# ---------------------------------------------------------------------------
def read_energy(energy_file: Path, index: int) -> float | None:
    """Legge il file delle energie e restituisce l'energia in Hartree per la riga index (0-based)."""
    try:
        lines = energy_file.read_text().splitlines()
        value = float(lines[index].strip())
        return value / HARTREE
    except Exception as err:
        print(f"⚠️  Errore leggendo energia da {energy_file} (riga {index+1}): {err}")
        return None

# ---------------------------------------------------------------------------
def main() -> None:
    lf = Path(LIST_FILE)
    if not lf.is_file():
        sys.exit(f"❌  File {LIST_FILE} non trovato")

    roots = [Path(p.strip()) for p in lf.read_text().splitlines() if p.strip()]

    written, visited = 0, 0
    for root in roots:
        if not root.is_dir():
            print(f"⚠️  {root} non è una directory, salto.")
            continue

        energy_path = root / ENERGY_FILE
        if not energy_path.is_file():
            print(f"⚠️  {energy_path} mancante, salto {root}")
            continue

        for sub in sorted(root.iterdir()):
            if not (sub.is_dir() and sub.name.startswith(f"{root.name}_protomer_")):
                continue

            visited += 1
            xyz_path = sub / XYZ_NAME
            if xyz_path.exists() and xyz_path.stat().st_size > 0:
                continue

            log_path = sub / LOG_NAME
            if not log_path.is_file():
                continue

            coords = last_coord_block(log_path)
            if coords is None:
                continue

            # Numero atomi
            num_atoms = len(coords)

            # Riga nel file energia = indice del protomero (protomer_1 → indice 0)
            try:
                protomer_num = int(sub.name.split("_")[-1])
            except Exception:
                print(f"⚠️  Nome sottocartella non valido: {sub.name}")
                continue

            energy = read_energy(energy_path, protomer_num - 1)
            if energy is None:
                continue

            header = f"{num_atoms}\nCoordinates from ORCA-job opt_t1 E {energy:.8f}"
            content = "\n".join(coords)
            full_xyz = f"{header}\n{content}\n"

            try:
                xyz_path.write_text(full_xyz)
                written += 1
            except Exception as err:
                print(f"❌  Errore scrivendo {xyz_path}: {err}")

            if visited % 100 == 0:
                print(f"...{visited} cartelle visitate • XYZ creati: {written}")

    print(f"✅  Finito! XYZ totali creati: {written}")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()

