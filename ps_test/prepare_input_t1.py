#!/usr/bin/env python3
import os
import shutil

# Funzione per ottenere la carica dal file charge.txt
def get_charge_from_txt(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read().strip()
            return int(content)
    except Exception as e:
        print(f"Errore nella lettura della carica da {file_path}: {e}")
        return None

# Funzione per aggiornare opt_t1.inp inserendo la riga "* xyzfile   charge 3 xtbopt.xyz"
def update_orca_file(file_path, charge):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Inserisci la linea con molteplicità 3 alla riga 10 (indice 9)
    insertion = f"* xyzfile   {charge}  3 xtbopt.xyz\n"
    lines.insert(9, insertion)

    with open(file_path, 'w') as f:
        f.writelines(lines)

def main():
    LIST_FILE = 'list_tot'
    if not os.path.isfile(LIST_FILE):
        print(f"File di lista non trovato: {LIST_FILE}")
        return

    with open(LIST_FILE, 'r') as f:
        directories = [line.strip() for line in f if line.strip()]

    for directory in directories:
        if not os.path.isdir(directory):
            print(f"Directory non trovata: {directory}")
            continue

        for subfolder in os.listdir(directory):
            if subfolder.startswith(f"{os.path.basename(directory)}_protomer_"):
                subpath = os.path.join(directory, subfolder)
                if not os.path.isdir(subpath):
                    continue

                # Copia opt_t1.inp nella sottocartella
                source_file = 'opt_t1.inp'
                dest_file = os.path.join(subpath, 'opt_t1.inp')
                try:
                    shutil.copy(source_file, dest_file)
                except Exception as e:
                    print(f"❌ Errore copiando {source_file} in {subpath}: {e}")
                    continue

                # Leggi la carica
                charge_file = os.path.join(subpath, 'charge.txt')
                charge = get_charge_from_txt(charge_file)
                if charge is None:
                    print(f"⚠️  Carica non trovata in {charge_file}, salto modifica.")
                    continue

                # Inserisci la riga con molteplicità 3
                try:
                    update_orca_file(dest_file, charge)
                    print(f"✅ Aggiornato {dest_file} con charge={charge}, multiplicity=3")
                except Exception as e:
                    print(f"❌ Errore modificando {dest_file}: {e}")

if __name__ == "__main__":
    main()
