#!/usr/bin/env python3
import os
import shutil

###############################################################################
# Funzioni di utilità
###############################################################################

def get_charge_from_txt(file_path: str) -> int | None:
    """
    Legge la carica (un intero) dalla prima riga del file total_charge.txt.
    """
    try:
        with open(file_path, "r") as f:
            # ci basta la prima colonna della prima riga
            first_token = f.readline().strip().split()[0]
            return int(first_token)
    except Exception as e:
        print(f"⚠️  Errore nella lettura della carica da {file_path}: {e}")
        return None


def update_orca_file(file_path: str, charge: int) -> None:
    """
    • Cambia la prima riga aggiungendo 'OPT'
    • Inserisce – o sostituisce – la seconda riga con '%PAL NPROCS 16 END'
    • Imposta la terza riga in formato '* xyzfile   <charge>  1 xtbopt.xyz'
    Elimina eventuali altre righe '* xyzfile …' successive per evitare duplicati.
    """
    with open(file_path, "r") as f:
        lines = f.readlines()

    # 1) Prima riga
    lines[0] = "! b3lyp_g  def2-tzvp  CPCM(water) OPT\n"

    # 2) Seconda riga – %PAL
    pal_line = "%PAL NPROCS 16 END\n"
    if len(lines) > 1 and lines[1].strip().startswith("%PAL"):
        lines[1] = pal_line
    else:
        lines.insert(1, pal_line)

    # 3) Terza riga – xyzfile con carica
    xyz_line = f"* xyzfile   {charge}  1 xtbopt.xyz\n"
    if len(lines) > 2 and lines[2].strip().startswith("* xyzfile"):
        lines[2] = xyz_line
    else:
        lines.insert(2, xyz_line)

    # 4) Rimuovi eventuali duplicati successivi di '* xyzfile'
    cleaned = [lines[0], lines[1], lines[2]] + [
        ln for ln in lines[3:] if not ln.strip().startswith("* xyzfile")
    ]

    with open(file_path, "w") as f:
        f.writelines(cleaned)


###############################################################################
# Main
###############################################################################

def main() -> None:
    LIST_FILE = "list_tot"
    if not os.path.isfile(LIST_FILE):
        print(f"❌ File di lista non trovato: {LIST_FILE}")
        return

    with open(LIST_FILE, "r") as f:
        directories = [line.strip() for line in f if line.strip()]

    for directory in directories:
        if not os.path.isdir(directory):
            print(f"❌ Directory non trovata: {directory}")
            continue

        for subfolder in os.listdir(directory):
            if subfolder.startswith(f"{os.path.basename(directory)}_protomer_"):
                subpath = os.path.join(directory, subfolder)
                if not os.path.isdir(subpath):
                    continue

                # 1) Copia del file sorgente → destinazione
                source_file = "opt_s0_orca_singlepoint.inp"
                dest_file = os.path.join(subpath, "opt_s0_dft.inp")

                try:
                    shutil.copy(source_file, dest_file)
                except Exception as e:
                    print(f"❌ Errore copiando {source_file} in {subpath}: {e}")
                    continue

                # 2) Leggi la carica
                charge_file = os.path.join(subpath, "total_charge.txt")
                charge = get_charge_from_txt(charge_file)
                if charge is None:
                    print(f"⚠️  Carica non trovata in {charge_file}, salto modifica.")
                    continue

                # 3) Aggiorna il file ORCA
                try:
                    update_orca_file(dest_file, charge)
                    print(
                        f"✅ Aggiornato {dest_file}: prima riga con 'OPT', "
                        f"%PAL, e carica={charge}"
                    )
                except Exception as e:
                    print(f"❌ Errore modificando {dest_file}: {e}")


if __name__ == "__main__":
    main()
