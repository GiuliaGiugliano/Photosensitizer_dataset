import os
import re

def estrai_soc_valori(file_path):
    results = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # Trova inizio blocco SOCME
        start_idx = next((i for i, line in enumerate(lines)
                          if 'CALCULATED SOCME BETWEEN TRIPLETS AND SINGLETS' in line), None)
        if start_idx is None:
            return results

        block = lines[start_idx:start_idx+120]  # blocco abbastanza lungo

        for line in block:
            # Linee con numeri (tripletto, singoletto e 3 tuple)
            if re.match(r'\s*\d+\s+\d+\s+\(', line):
                try:
                    match = re.match(
                        r'\s*(\d+)\s+(\d+)\s+\(\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*\)\s+\(\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*\)\s+\(\s*([-+0-9.eE]+)\s*,\s*([-+0-9.eE]+)\s*\)',
                        line
                    )
                    if not match:
                        print("Regex non ha matchato:\n", line)
                        continue

                    T = int(match.group(1))
                    S = int(match.group(2))
                    ReZ, ImZ = float(match.group(3)), float(match.group(4))
                    ReX, ImX = float(match.group(5)), float(match.group(6))
                    ReY, ImY = float(match.group(7)), float(match.group(8))

                    X2 = ReX**2 + ImX**2
                    Y2 = ReY**2 + ImY**2
                    Z2 = ReZ**2 + ImZ**2

                    results.append((T, S, X2, Y2, Z2))

                except Exception as e:
                    print(f"Errore nel parsing della riga:\n{line}\n{e}")

    except FileNotFoundError:
        print(f"File non trovato: {file_path}")
    return results


# Legge la lista delle cartelle dal file 'prova'
with open('list_tot', 'r') as f:
    cartelle = [line.strip() for line in f if line.strip()]

# Scorre tutte le cartelle e sottocartelle
for cartella in cartelle:
    for i in range(1, 21):
        dir_path = os.path.join(cartella, f"{cartella}_protomer_{i}")
        log_path = os.path.join(dir_path, "orca_tddft.log")
        out_path = os.path.join(dir_path, "soc_calc.txt")

        if os.path.isdir(dir_path) and os.path.isfile(log_path):
            print(f"Processing {dir_path}")
            risultati = estrai_soc_valori(log_path)

            if risultati:
                with open(out_path, 'w') as out:
                    out.write("T S X² Y² Z²\n")
                    for T, S, X2, Y2, Z2 in risultati:
                        out.write(f"{T} {S} {X2:.5f} {Y2:.5f} {Z2:.5f}\n")
            else:
                print(f"Nessun SOCME trovato in {log_path}")
