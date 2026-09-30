#!/usr/bin/env python3
# full_system_photo.py
import os
import json
import numpy as np
import pandas as pd
import ase.io

# ——————————————————————————————————————————————————————————
def convert_info_dict(info_dict):
    """Converte mol.info in stringhe compatibili EXTXYZ."""
    new_info = {}
    for k, v in info_dict.items():
        if isinstance(v, np.ndarray):
            if v.ndim == 1:                                   # 1-D
                new_info[k] = ' '.join(f"{x:.25f}" for x in v.tolist())
            else:                                             # 2-D
                rows = [[float(f"{x:.25f}") for x in row] for row in v.tolist()]
                new_info[k] = '_JSON ' + json.dumps(rows)
        elif isinstance(v, (float, int)):
            new_info[k] = f"{float(v):.25f}"
        else:
            new_info[k] = str(v)
    return new_info
# ——————————————————————————————————————————————————————————
def extract_kisc_vector(ics_path):
    """(1 × 30) valori SOC² per T 1-5 × S 0-5 dal file kISC (ics_cost.txt)."""
    df = pd.read_csv(ics_path, sep=r'\s+', header=None,
                     skiprows=1, engine='python', dtype=float, on_bad_lines='skip')
    df_filt = df[
        df.iloc[:, 0].between(1, 5, inclusive='both') &  # T 1..5
        df.iloc[:, 1].between(0, 5, inclusive='both')    # S 0..5
    ]
    if df_filt.shape[0] != 30:
        raise ValueError(f"Attesi 30 kISC, trovati {df_filt.shape[0]}")
    mod_eV = df_filt.iloc[:, 6].to_numpy(dtype=float)
    return (mod_eV ** 2).reshape(1, -1)
# ——————————————————————————————————————————————————————————
def first5(df, sufx):
    """Prime 5 righe con end_state che termina per sufx (‘-1A’ o ‘-3A’)."""
    return df[df['end_state'].str.endswith(sufx)].head(5)
# ——————————————————————————————————————————————————————————
def process_dir(subdir, db):
    try:
        # — file paths
        paths = {
            'energy':   "energy_s0_opt.txt",
            'spectrum': "spectrum_col.txt",
            's0_dip':   "s0_dipole_components.txt",
            'charge':   "total_charge.txt",
            'hlgap':    "homo_lumo_gap_col.txt",
            'ics':      "ics_cost.txt",
            'xyz':      "xtbopt.xyz"
        }
        for k, fname in paths.items():
            paths[k] = os.path.join(subdir, fname)

        s0_energy = float(open(paths['energy']).read().strip())

        spec_df  = pd.read_csv(paths['spectrum'], delim_whitespace=True, engine='python')
        sing5, trip5 = first5(spec_df, '-1A'), first5(spec_df, '-3A')
        spec10   = pd.concat([sing5, trip5], ignore_index=True)

        # —— REF_energy (S0 + 10 eccitati)
        ref_energy = np.concatenate(
            ([s0_energy],
             spec10['Excited_state_energy(eV)'].to_numpy())
        ).reshape(1, -1)

        # —— REF_dipoles (moduli)
        # S0
        s0_vec = pd.read_csv(paths['s0_dip'], delim_whitespace=True,
                             header=None).iloc[0, [4, 5, 6]].to_numpy(dtype=float)
        mod_s0 = float(np.linalg.norm(s0_vec))
        # 10 eccitati
        mods_exc = spec10['Transition_dipole_module'].to_numpy(dtype=float)
        ref_dipoles = np.concatenate(([mod_s0], mods_exc)).reshape(1, -1)

        # —— REF_wavelen & oscillator
        ref_wavelen = spec10['excitation_energy(eV)'].to_numpy().reshape(1, -1)
        ref_osc     = spec10['fosc'].to_numpy().reshape(1, -1)

        # —— REF_scalar per atomo
        total_charge = float(open(paths['charge']).read().strip())

        # —— REF_hlgap duplicato
        hl = pd.read_csv(paths['hlgap'], delim_whitespace=True, header=None).iloc[2, 2]
        ref_hlgap = np.array([[hl, hl]], dtype=float)

        # —— REF_kisc (30 valori)
        ref_kisc = extract_kisc_vector(paths['ics'])

        # —— carica molecola
        mol = ase.io.read(paths['xyz'])
        n_atoms = len(mol)
        ref_scalar = np.full((n_atoms, 1), total_charge, dtype=float)

        mol.info = {
            "REF_energy":     ref_energy,
            "REF_wavelen":    ref_wavelen,
            "REF_oscillator": ref_osc,
            "REF_dipoles":    ref_dipoles,
            "REF_scalar":     ref_scalar,
            "REF_hlgap":      ref_hlgap,
            "REF_kisc":       ref_kisc,
        }

        db.append(mol)
        print(f"✅ Completato: {subdir}")

    except Exception as e:
        print(f"❌ Errore in {subdir}: {e}")
# ——————————————————————————————————————————————————————————
def main():
    list_file = "list_tot"
    if not os.path.isfile(list_file):
        print(f"File {list_file} non trovato.")
        return

    with open(list_file) as f:
        folders = [ln.strip() for ln in f if ln.strip()]

    db = []
    for fold in folders:
        for i in range(1, 21):
            subdir = os.path.join(fold, f"{fold}_protomer_{i}")
            if os.path.isdir(subdir):
                print(f"[FULL SYSTEM] Processing {subdir}")
                process_dir(subdir, db)

    if not db:
        print("Nessuna molecola processata.")
        return

    out_xyz = "full_system_ps_5stati.xyz"
    with open(out_xyz, "w") as fh:
        for mol in db:
            mol.info = convert_info_dict(mol.info)
            ase.io.write(fh, mol, format='extxyz')
    print(f"✔️ Salvato {out_xyz} ({len(db)} molecole).")
# ——————————————————————————————————————————————————————————
if __name__ == "__main__":
    main()
