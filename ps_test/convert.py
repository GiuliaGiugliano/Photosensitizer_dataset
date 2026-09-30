import ase.io
import numpy as np

# Legge il file XYZ contenente il training set
db = ase.io.read("full_system_ps_shape_moduli.xyz", ":")

# Stampa la forma iniziale del campo REF_energy della prima molecola
print("Forma iniziale REF_energy:", db[0].info["REF_energy"].shape)

correct_mols = []
for mol in db:
    # Per ogni molecola, replica il valore scalar per ogni atomo
    mol.info["REF_scalar"] = np.full((len(mol), 1), mol.info["REF_scalar"])
    # Rimodella REF_energy in modo da avere una forma (1, 21)
    mol.info["REF_energy"] = mol.info["REF_energy"].reshape(1, 21)
    correct_mols.append(mol)
    mol.info["REF_dipoles"] = mol.info["REF_dipoles"].reshape(1, 21)
    mol.info["REF_wavelen"] = mol.info["REF_wavelen"].reshape(1, 20)
    mol.info["REF_kisc"] = mol.info["REF_kisc"].reshape(1, 110)
    mol.info["REF_hlgap"] = mol.info["REF_hlgap"].reshape(1, 1)
    mol.info["REF_oscillator"] = mol.info["REF_oscillator"].reshape(1, 20)
    print(db[0].info["REF_energy"].shape)
    print(db[0].info["REF_oscillator"].shape)
    print(db[0].info["REF_dipoles"].shape)
    print(db[0].info["REF_wavelen"].shape)
    print(db[0].info["REF_hlgap"].shape)
    print(db[0].info["REF_kisc"].shape)
# Salva il training set modificato in un nuovo file XYZ
ase.io.write("full_system_ps_shape.xyz", correct_mols)
