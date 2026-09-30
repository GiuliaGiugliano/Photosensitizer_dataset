import os

# Nome del file che contiene la lista delle cartelle
input_file = "list_tot"

# File di output dove salvare le informazioni sull'atomo di iodio
output_file = "iodine_atom.txt"

# Funzione per leggere la lista di cartelle dal file
def read_folder_list(input_file):
    with open(input_file, 'r') as f:
        # Legge tutte le righe e rimuove gli eventuali spazi o newline
        return [line.strip() for line in f.readlines()]

# Funzione per verificare la presenza di iodio nel file xtbopt.xyz
def check_iodine_in_file(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            if "I" in content:  # Verifica se c'è l'atomo di iodio (I)
                return True
    except FileNotFoundError:
        return False
    return False

# Funzione principale
def process_folders(list_tot):
    with open(output_file, 'w') as output:  # Apri il file per scrivere i risultati
        for cartella in list_tot:
            for numero in range(1, 21):  # Prova numeri da 1 a 20
                subfolder = f"{cartella}/{cartella}_protomer_{numero}"
                xtbopt_path = os.path.join(subfolder, "xtbopt.xyz")

                if os.path.exists(subfolder) and check_iodine_in_file(xtbopt_path):
                    # Se il file xtbopt.xyz contiene iodio, scrivi nel file di output
                    output.write(f"{subfolder}\tiodio\n")
                    print(f"Trovato iodio in {subfolder}")  # Messaggio di log

# Leggi la lista delle cartelle dal file
list_tot = read_folder_list(input_file)

# Esegui lo script
process_folders(list_tot)
