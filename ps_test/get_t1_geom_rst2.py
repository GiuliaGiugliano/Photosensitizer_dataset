#!/usr/bin/env python3
import os

def extract_last_coordinates_block(log_path):
    """Estrae l'ultimo blocco 'CARTESIAN COORDINATES (ANGSTROEM)' dopo 'FINAL ENERGY EVALUATION'."""
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"⚠️ Impossibile leggere {log_path}: {e}")
        return None

    if not any("ORCA TERMINATED NORMALLY" in line for line in lines):
        return None

    final_energy_found = False
    current_block = []
    last_block = []

    for i, line in enumerate(lines):
        if "FINAL ENERGY EVALUATION" in line:
            final_energy_found = True

        if final_energy_found and "CARTESIAN COORDINATES (ANGSTROEM)" in line:
            current_block = []
            j = i + 2  # salta intestazione e linea ------
            while j < len(lines):
                l = lines[j].strip()
                if not l or not l[0].isalpha():  # riga vuota o non atomica
                    break
                current_block.append(l)
                j += 1
            last_block = current_block  # sovrascrive sempre con l’ultimo
    return last_block if last_block else None

def main():
    LIST_FILE = 'list_rst'
    if not os.path.isfile(LIST_FILE):
        print(f"❌ File di lista non trovato: {LIST_FILE}")
        return

    with open(LIST_FILE, 'r') as f:
        directories = [line.strip() for line in f if line.strip()]

    for directory in directories:
        if not os.path.isdir(directory):
            print(f"⚠️  Directory non trovata: {directory}")
            continue

        base_name = os.path.basename(directory)

        for subfolder in os.listdir(directory):
            if subfolder.startswith(f"{base_name}_protomer_"):
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

