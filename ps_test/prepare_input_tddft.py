#!/usr/bin/env python3

import os
import shutil

# Funzione per ottenere la carica dal file charge.txt
def get_charge_from_txt(file_path):
    charge = None
    try:
        with open(file_path, 'r') as f:
            line = f.readline()
            charge = int(line.strip())
    except Exception as e:
        print(f"Errore nella lettura della carica da {file_path}: {e}")
        charge = None
    return charge

# Funzione per aggiornare il file orca_tddft.inp
def update_orca_file(file_path, charge):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Aggiungi la riga * xyzfile dopo la riga 9
    lines.insert(9, f"* xyzfile   {charge}  1 xtbopt.xyz\n")

    # Scrivi il file aggiornato
    with open(file_path, 'w') as f:
        f.writelines(lines)

# Percorso al file name_dir.txt che contiene la lista delle cartelle
name_dir_file = 'list_tot'

# Leggi le cartelle da name_dir.txt
with open(name_dir_file, 'r') as f:
    directories = f.readlines()

# Ciclo attraverso ogni cartella nella lista
for directory in directories:
    directory = directory.strip()  # Rimuovi eventuali spazi o newline

    # Verifica se la cartella principale esiste
    if os.path.isdir(directory):
        # Esamina le sottocartelle nella cartella principale
        for subfolder in os.listdir(directory):
            if subfolder.startswith(f"{directory}_protomer_") and os.path.isdir(os.path.join(directory, subfolder)):
                subfolder_path = os.path.join(directory, subfolder)

                # Copia il file orca_tddft.inp nella sottocartella
                source_file = 'orca_tddft.inp'  # Assumendo che il file si trovi nella directory corrente
                destination_file = os.path.join(subfolder_path, 'orca_tddft.inp')
                shutil.copy(source_file, destination_file)

                # Ottieni la carica dal file charge.txt nella sottocartella
                charge_file = os.path.join(subfolder_path, 'charge.txt')
                charge = get_charge_from_txt(charge_file)

                if charge is not None:
                    # Modifica il file orca_tddft.inp
                    update_orca_file(destination_file, charge)
                else:
                    print(f"Carica non trovata nel file {charge_file}")
    else:
        print(f"Directory {directory} non trovata.")

