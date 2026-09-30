import os
from rdkit import Chem

def pdb_to_xyz_no_mod(pdb_path, xyz_path):
    # Carica il PDB senza rimuovere H o sanificare
    mol = Chem.MolFromPDBFile(pdb_path, removeHs=False, sanitize=False)

    if mol is None:
        print(f"[ERRORE] Impossibile caricare: {pdb_path}")
        return

    conf = mol.GetConformer()

    with open(xyz_path, 'w') as f:
        f.write(f"{mol.GetNumAtoms()}\n")
        f.write(f"{os.path.basename(pdb_path)}\n")
        for atom in mol.GetAtoms():
            idx = atom.GetIdx()
            pos = conf.GetAtomPosition(idx)
            symbol = atom.GetSymbol()
            f.write(f"{symbol} {pos.x:.6f} {pos.y:.6f} {pos.z:.6f}\n")

    print(f"[OK] XYZ creato: {xyz_path}")

# 📄 Legge la lista delle cartelle da name_tot.txt
with open("list2", "r") as f:
    name_tot = [line.strip() for line in f if line.strip()]

for name in name_tot:
    folder = os.path.join(name, f"{name}_protomer_1")
    pdb_file = os.path.join(folder, f"{name}_protomer_1.pdb")
    xyz_file = os.path.join(folder, f"{name}_protomer_1.xyz")

    if os.path.exists(pdb_file):
        pdb_to_xyz_no_mod(pdb_file, xyz_file)
    else:
        print(f"[ERRORE] File PDB non trovato: {pdb_file}")

