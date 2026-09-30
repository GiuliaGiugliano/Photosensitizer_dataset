import os

# Leggi la lista delle cartelle dal file
input_file = "no"
with open(input_file, "r") as f:
    cartelle = [line.strip() for line in f.readlines()]

# Per ogni cartella, esegui il controllo e le azioni
for cartella in cartelle:
    log_file = os.path.join(cartella, "opt_s0_orca_single_point.log")

    if os.path.exists(log_file):
        with open(log_file, "r") as log:
            contenuto = log.read()

            if "The File: opt_s0_orca_singlepoint.gbw  exists" in contenuto:
                print(f"[{cartella}] Trovato 'opt_s0_orca_singlepoint.gbw exists'. Rimuovo .gbw e rilancio.")
                os.system(f"cd {cartella} && rm *.gbw && sbatch orca_single_point.slurm")

            elif "in GUESS" in contenuto:
                print(f"[{cartella}] Trovato 'in GUESS'. Rimuovo .ges e rilancio.")
                os.system(f"cd {cartella} && rm *.ges && sbatch orca_single_point.slurm")

            elif "ORCA finished by error termination in LEANSCF" in contenuto:
                print(f"[{cartella}] Trovato errore LEANSCF. Modifico input e rilancio.")

                inp_file = os.path.join(cartella, "opt_s0_orca_singlepoint.inp")
                if os.path.exists(inp_file):
                    with open(inp_file, "r") as inp:
                        lines = inp.readlines()

                    lines[0] = "! b3lyp_g  def2-tzvp  CPCM(water) Slowconv\n"
                    lines.insert(1, "%maxcore 8000\n\n%scf\n  maxiter 500\nend\n")

                    with open(inp_file, "w") as inp:
                        inp.writelines(lines)

                    os.system(f"cd {cartella} && sbatch orca_single_point.slurm")
                else:
                    print(f"[{cartella}] File input non trovato.")

            elif "Calling Command: orca_startup orca_singlepoint*.tmp" in contenuto:
                print(f"[{cartella}] Trovato orca_startup error. Pulizia e modifica input.")

                # Rimuovi i file .tmp
                os.system(f"cd {cartella} && rm *.tmp")

                inp_file = os.path.join(cartella, "opt_s0_orca_singlepoint.inp")
                if os.path.exists(inp_file):
                    with open(inp_file, "r") as inp:
                        lines = inp.readlines()

                    # Sovrascrivi prima riga e inserisci la seconda
                    lines[0] = "! b3lyp_g def2-tzvp SlowConv RIJCOSX TightSCF CPCM(water)\n"
                    lines.insert(1, "%maxcore 64000\n")

                    with open(inp_file, "w") as inp:
                        inp.writelines(lines)

                    # Lancia il job
                    os.system(f"cd {cartella} && sbatch orca_single_point.slurm")
                else:
                    print(f"[{cartella}] File opt_s0_orca_singlepoint.inp  non trovato.")
            else:
                print(f"[{cartella}] Nessuna delle condizioni trovata nel log.")
    else:
        print(f"[{cartella}] File log mancante.")
