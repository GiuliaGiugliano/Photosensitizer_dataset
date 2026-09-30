import os
import numpy as np
import pandas as pd
import ase.io
from ase import Atoms

def convert_info_dict(info_dict):
    new_info = {}
    for key, value in info_dict.items():
        if isinstance(value, np.ndarray):
            if value.ndim == 1:
                new_info[key] = ' '.join(format(v, '.25f') for v in value)
            elif value.ndim == 2:
                new_info[key] = '_JSON ' + str([[format(v, '.25f') for v in row] for row in value])
        elif isinstance(value, (float, int)):
            new_info[key] = format(value, '.25f')
        else:
            new_info[key] = str(value)
    return new_info

def process_dir(subdir, db):
    try:
        energy_path = os.path.join(subdir, "energy_s0_opt.txt")
        spectrum_path = os.path.join(subdir, "spectrum_col.txt")
        s0_dipole_file = os.path.join(subdir, "s0_dipole_components.txt")
        total_charge_path = os.path.join(subdir, "total_charge.txt")
        homo_lumo_path = os.path.join(subdir, "homo_lumo_gap_col.txt")
        ics_path = os.path.join(subdir, "ics_cost.txt")
        xtb_path = os.path.join(subdir, "xtbopt.xyz")

        with open(energy_path, 'r') as f:
            s0_energy = float(f.readline().strip())

        spectrum_df = pd.read_csv(spectrum_path, sep='\s+')
        excited_energies = spectrum_df['Excited_state_energy(eV)'].to_numpy()[:20]
        ref_energy = np.concatenate((np.array([s0_energy]), excited_energies))

        s0_df = pd.read_csv(s0_dipole_file, sep='\s+', header=None)
        dipole_s0 = s0_df.iloc[0, [4, 5, 6]].to_numpy()

        dx = spectrum_df['DX'].to_numpy()[:20]
        dy = spectrum_df['DY'].to_numpy()[:20]
        dz = spectrum_df['DZ'].to_numpy()[:20]
        transition_dipoles = np.stack([dx, dy, dz], axis=1)
        ref_dipoles = np.vstack((dipole_s0, transition_dipoles))

        ref_oscillator = spectrum_df['fosc'].to_numpy()[:20]

        with open(total_charge_path, 'r') as f:
            total_charge = float(f.readline().strip())
        ref_scalar = np.array([total_charge])

        ref_wavelen = spectrum_df['excitation_energy(eV)'].to_numpy()[:20]

        homo_lumo_df = pd.read_csv(homo_lumo_path, sep='\s+', header=None)
        ref_hlgap = homo_lumo_df.iloc[2, 2]

        ics_df = pd.read_csv(ics_path, sep='\s+')
        ref_kisc = ics_df['kisc'].to_numpy()

        mol = ase.io.read(xtb_path)

        mol.info = {
            "REF_energy": ref_energy,
            "REF_oscillator": ref_oscillator,
            "REF_dipoles": ref_dipoles,
            "REF_scalar": ref_scalar,
            "REF_wavelen": ref_wavelen,
            "REF_hlgap": ref_hlgap,
            "REF_kisc": ref_kisc
        }

        db.append(mol)
        print(f"✅ Completato: {subdir}")

    except Exception as e:
        print(f"❌ Errore in {subdir}: {e}")

def main():
    db = []
    list_file = "list_ps_completi_nodopp"
    if not os.path.exists(list_file):
        print(f"File {list_file} non trovato.")
        return

    with open(list_file, 'r') as f:
        cartelle = [line.strip() for line in f if line.strip()]

    for cartella in cartelle:
        for i in range(1, 21):
            subdir = os.path.join(cartella, f"{cartella}_protomer_{i}")
            if os.path.isdir(subdir):
                print(f"[FULL SYSTEM] Processing {subdir}")
                process_dir(subdir, db)

    if db:
        output_file = "full_system_photo.xyz"
        with open(output_file, "w") as f:
            for mol in db:
                mol.info = convert_info_dict(mol.info)
                ase.io.write(f, mol, format='extxyz')
        print(f"Salvataggio completato in {output_file}")
    else:
        print("Nessuna molecola processata.")

if __name__ == "__main__":
    main()
