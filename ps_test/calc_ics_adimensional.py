import os
import re
import math

def estrai_soc_valori(file_path):
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        start_idx = next((i for i, line in enumerate(lines)
                          if 'CALCULATED SOCME BETWEEN TRIPLETS AND SINGLETS' in line), None)
        if start_idx is None:
            return results

        block = lines[start_idx:start_idx+120]

        for line in block:
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
                    module = math.sqrt(X2 + Y2 + Z2)

                    results.append((T, S, X2, Y2, Z2, module))

                except Exception as e:
                    print(f"Errore nel parsing della riga:\n{line}\n{e}")

    except FileNotFoundError:
        print(f"File non trovato: {file_path}")

    return results

def parse__file(file_path):
    singlets = []
    triplets = []

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        if not lines:
            return singlets, triplets

        all_entries = []
        for line in lines[1:]:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) < 13:
                continue
            try:
                entry = {
                    'S0_min_energy(eV)': float(parts[11]),
                    'Excited_state_energy(eV)': float(parts[12])
                }
            except Exception as e:
                print(f"Errore nel parsing della riga dello spettro:\n{line}\n{e}")
                continue
            all_entries.append(entry)

        singlets = all_entries[:10]
        triplets = all_entries[10:20]

    except FileNotFoundError:
        print(f"File spettro non trovato: {file_path}")
    except Exception as e:
        print(f"Errore nella lettura del file spettro {file_path}: {e}")

    return singlets, triplets

# Legge la lista delle cartelle
with open('list_tot', 'r') as f:
    cartelle = [line.strip() for line in f if line.strip()]

# Processa tutte le cartelle e sottocartelle
for cartella in cartelle:
    for i in range(1, 21):
        dir_path = os.path.join(cartella, f"{cartella}_protomer_{i}")
        log_path = os.path.join(dir_path, "orca_tddft.log")
        soc_calc_path = os.path.join(dir_path, "soc_calc_complete.txt")
        ics_cost_path = os.path.join(dir_path, "ics_cost.txt")
        spectrum_path = os.path.join(dir_path, "spectrum_col.txt")

        if os.path.isdir(dir_path) and os.path.isfile(log_path) and os.path.isfile(spectrum_path):
            print(f"Processing {dir_path}")
            risultati = estrai_soc_valori(log_path)
            singlets, triplets = parse__file(spectrum_path)

            if risultati:
                with open(soc_calc_path, 'w') as out:
                    out.write("T S X\u00b2 Y\u00b2 Z\u00b2 module(cm-1)\n")
                    for T, S, X2, Y2, Z2, module_cm1 in risultati:
                        out.write(f"{T} {S} {X2:.5f} {Y2:.5f} {Z2:.5f} {module_cm1:.5f}\n")

                with open(ics_cost_path, 'w') as out:
                    out.write("T S X\u00b2 Y\u00b2 Z\u00b2 module(cm-1) module(eV) energy_Tn(eV) energy_Sn(eV) kisc\n")
                    for T, S, X2, Y2, Z2, module_cm1 in risultati:
                        if T > 0 and T <= len(triplets):
                            energy_T = triplets[T-1]['Excited_state_energy(eV)']
                        else:
                            energy_T = "NA"

                        if S == 0 and len(singlets) > 0:
                            energy_S = singlets[0]['S0_min_energy(eV)']
                        elif S > 0 and S <= len(singlets):
                            energy_S = singlets[S-1]['Excited_state_energy(eV)']
                        else:
                            energy_S = "NA"

                        module_eV = module_cm1 * 1.239841984e-4

                        if energy_T != "NA" and energy_S != "NA":
                            try:
                                diff = energy_S - energy_T
                                if diff != 0:
                                    kisc = (module_eV**2) / (diff**2)
                                else:
                                    kisc = "NA"
                            except Exception as e:
                                kisc = "NA"
                        else:
                            kisc = "NA"

                        out.write(f"{T} {S} {X2:.5f} {Y2:.5f} {Z2:.5f} {module_cm1:.5f} {module_eV:.7f} {energy_T} {energy_S} {kisc}\n")
            else:
                print(f"Nessun SOCME trovato in {log_path}")
        else:
            if not os.path.isdir(dir_path):
                print(f"Cartella {dir_path} non trovata")
            elif not os.path.isfile(log_path):
                print(f"File log {log_path} non trovato")
            elif not os.path.isfile(spectrum_path):
                print(f"File spectrum {spectrum_path} non trovato")

