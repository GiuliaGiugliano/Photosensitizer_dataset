import os

# Legge la lista delle cartelle da un file di input
input_file = "list_tot"
with open(input_file, "r") as f:
    list_ps_completi_nodopp = [line.strip() for line in f.readlines()]

# Nome del file di output
output_file = "s0_andati.txt"

with open(output_file, "w") as out_file:
    for cartella in list_ps_completi_nodopp:
        for numero in range(1, 21):  # Da 1 a 20
            sottocartella = os.path.join(cartella, f"{cartella}_protomer_{numero}")
            log_file = os.path.join(sottocartella, "opt_s0_orca_single_point.log")

            if not os.path.exists(sottocartella):
                continue  # Salta se la sottocartella non esiste

            if not os.path.exists(log_file):
                out_file.write(f"{sottocartella} NO (file non trovato)\n")
            else:
                if os.path.getsize(log_file) == 0:
                    out_file.write(f"{sottocartella} MISSING\n")
                else:
                    with open(log_file, "r") as log:
                        contenuto = log.read()
                        if "****ORCA TERMINATED NORMALLY****" in contenuto:
                            out_file.write(f"{sottocartella} OK\n")
                        else:
                            out_file.write(f"{sottocartella} NO\n")

print(f"Risultati salvati in {output_file}")
