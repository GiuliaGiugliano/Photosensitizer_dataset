#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Per ogni cartella elencata in list_ps_completi_nodopp e per ogni sottocartella
<root>_protomer_*:
1. copia il template opt_cat.inp (presente nella directory in cui lanci lo script)
2. legge la carica da total_charge.txt, la incrementa di 1
3. inserisce alla riga 3 la linea:
   * xyzfile   <carica>  2 opt_t1.xyz
   (dove 2 è la molteplicità fissa e <carica> è (valore_txt + 1) )
"""

import os
import shutil

LIST_FILE   = "list_tot"
SOURCE_INP  = "opt_cat.inp"      # template da copiare
DEST_INP    = "opt_cat.inp"      # nome nella sottocartella
CHARGE_FILE = "total_charge.txt"

# --------------------------------------------------------------------------- #
def read_charge(txt_path: str) -> int | None:
    """Legge il primo intero nel file total_charge.txt; None se errore."""
    try:
        with open(txt_path) as f:
            return int(f.readline().split()[0])
    except Exception as err:
        print(f"⚠️  Impossibile leggere la carica da {txt_path}: {err}")
        return None

def patch_inp(inp_path: str, charge: int) -> None:
    """
    Inserisce (o sostituisce) la riga 3 con:
        * xyzfile   <charge>  2 opt_t1.xyz
    """
    with open(inp_path) as f:
        lines = f.readlines()

    insert = f"* xyzfile   {charge}  2 opt_t1.xyz\n"

    if len(lines) >= 3 and lines[2].lstrip().startswith("* xyzfile"):
        lines[2] = insert                        # sostituisci riga 3 esistente
    elif len(lines) >= 2:
        lines.insert(2, insert)                  # inserisci dopo le prime 2 righe
    else:                                        # file troncato: pad prima di inserire
        while len(lines) < 2:
            lines.append("\n")
        lines.append(insert)

    with open(inp_path, "w") as f:
        f.writelines(lines)

# --------------------------------------------------------------------------- #
def main() -> None:
    if not os.path.isfile(LIST_FILE):
        print(f"❌ File di lista non trovato: {LIST_FILE}")
        return
    if not os.path.isfile(SOURCE_INP):
        print(f"❌ Template {SOURCE_INP} mancante nella directory di lavoro")
        return

    with open(LIST_FILE) as f:
        roots = [ln.strip() for ln in f if ln.strip()]

    for root in roots:
        if not os.path.isdir(root):
            print(f"⚠️  Directory non trovata: {root}")
            continue

        for sub in os.listdir(root):
            if not sub.startswith(f"{os.path.basename(root)}_protomer_"):
                continue
            subdir = os.path.join(root, sub)

            dest_inp = os.path.join(subdir, DEST_INP)
            try:
                shutil.copy(SOURCE_INP, dest_inp)
            except Exception as err:
                print(f"❌ Errore copiando {SOURCE_INP} in {subdir}: {err}")
                continue

            charge_txt = os.path.join(subdir, CHARGE_FILE)
            base_charge = read_charge(charge_txt)
            if base_charge is None:
                print(f"⚠️  Carica non trovata in {charge_txt}, salto modifica.")
                continue

            try:
                patch_inp(dest_inp, base_charge + 1)
                print(f"✅ Aggiornato {dest_inp} con charge={base_charge + 1}, mult=2")
            except Exception as err:
                print(f"❌ Errore modificando {dest_inp}: {err}")

# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()
