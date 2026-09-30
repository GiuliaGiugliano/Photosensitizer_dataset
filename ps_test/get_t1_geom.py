#!/usr/bin/env python3
import os
import re

def extract_last_coordinates_block(log_path):
    with open(log_path, 'r') as f:
        content = f.read()

    # Verifica che ORCA sia terminato normalmente
    if "ORCA TERMINATED NORMALLY" not in content:
        return None

    # Trova tutti i blocchi di coordinate dopo la sezione FINAL ENERGY EVALUATION
    blocks = []
    pattern = re.compile(
        r"\*{10,}.*?FINAL ENERGY EVALUATION.*?\*{10,}.*?"
        r"CARTESIAN COORDINATES \(ANGSTROEM\)\s*-+\s*(.*?)\n\n",
        re.DOTALL
    )
    blocks = pattern.findall(content)

    if not blocks:
        return None

    # Prende l'ultimo blocco
    last_block = blocks[-1]

    # Pulisce righe vuote o spazi
    lines = [line.strip() for line in last_block.strip().splitlines() if line.strip()]
    return lines

def main():
    LIST_FILE = 'list_to_rstt'
    if not os.path.isfile(LIST_FILE):
        print(f"❌ File di lista non trovato: {LIST_FILE}")
        return

    with open(LIST_FILE, 'r') as f:
        directories = [line.strip() for line in f if line.strip()]

    for directory in directories:
        if not os.path.isdir(directory):
            print(f"⚠️  Directory non trovata: {directory}")
            continue

        for subfolder in os.listdir(directory):
            if subfolder.startswith(f"{os.path.basename(directory)}_protomer_"):
                subpath = os.path.join(directory, subfolder)
                log_path = os.path.join(subpath, 'opt_t1.log')

                if not os.path.isfile(log_path):
                    continue

                coords = extract_last_coordinates_block(log_path)
                if coords is None:
                    print(f"❌ Coordinate non trovate in {log_path}")
                    continue

                output_file = os.path.join(subpath, 'opt_t1.xyz')
                try:
                    with open(output_file, 'w') as out:
                        out.write("\n".join(coords) + "\n")
                    print(f"✅ Coordinate salvate in {output_file}")
                except Exception as e:
                    print(f"❌ Errore scrivendo {output_file}: {e}")

if __name__ == "__main__":
    main()

