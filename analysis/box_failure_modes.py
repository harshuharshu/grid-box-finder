"""
Quantify the multiple-copy box-definition failure mode.

For each PDB entry: identify the ligand Grid Box Finder would auto-select, then compare
the correct single-copy box centre against the centre obtained by pooling every copy of
that ligand (what a residue-name selection produces). Reports the displacement, whether a
conventionally sized cube at the pooled centre still contains the true ligand, and how
buried each centre looks.

Outputs: gridbox_pilot_benchmark.csv, fig_box_failure_modes.png

Usage:  python box_failure_modes.py
Requires: numpy, matplotlib (no internet cache needed; files are fetched from RCSB)
"""

import csv
import math
import os
import statistics
import urllib.request

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

PDB_IDS = [
    "5KIR", "1IEP", "3ERT", "2ITO", "4HJO", "1HVR", "3PP0", "4EY7", "6LU7", "1M17",
    "2HYY", "1STP", "3LN1", "4DJU", "5TBM", "1FKF", "2RGP", "3POZ", "1UYG", "4GBD",
    "1OYT", "2P2I", "3NY8", "1AQ1", "4LDE",
]

# Residue-code classes, mirroring the dictionary in grid-box-finder.html.
SETS = {
    "water": "HOH WAT DOD H2O",
    "ion": "NA CL K MG CA ZN MN FE FE2 CO NI CU CU1 CD HG IOD BR F LI RB CS SR BA AL "
           "NH4 NO3 SO4 PO4 PI SCN AZI CYN OH",
    # cryoprotectants, buffers, precipitants, polyamines and detergents
    "additive": "GOL EDO PEG PG4 PGE 1PE P6G MPD DMS DMSO ACT ACE FMT EPE MES TRS TAM "
                "BME CIT FLC ACY IMD MLI MLA TLA BU3 PE4 PE5 2PE 15P 7PE CXS HEZ IPA "
                "EOH MOH DIO SIN MRD BTB B3P POP 12P P33 PEU EDT TAR BU1 ACM URE SPM "
                "SPD UMQ LMT LDA BOG OTG HTG BNG DDQ C8E DMU LMN SOG BCD HP6 JEF",
    "sugar": "NAG NDG MAN BMA FUC GAL GLC BGC SIA GLA FUL XYS NGA A2G RAM",
    # sterols, fatty acids, phospholipids and LCP alkanes
    "lipid": "CLR Y01 CHD OLA OLB OLC PLM MYR STE PEE POV PC1 PCW PGV PGT LHG D10 D12 "
             "HEX HTO 1WV CPS CDL TGL RET",
    # nucleotide sugars, phosphosugars and metabolic intermediates
    "substrate": "UD1 UD2 UD4 UDM UPG UGA UFG U2F GDU GDD UMA UDP PEP PYR AKG OAA G6P "
                 "F6P GLP PRP ADN DUP G1P M6P S6P R5P E4P FBP 13P 3PG 2PG",
    "cofactor": "HEM HEC HEA COH FAD FMN NAD NAI NAP NDP NADP ATP ADP AMP ANP ACP GTP "
                "GDP GNP SAM SAH COA ACO PLP TPP BTN H4B CLA BCL UMP CTP UTP TTP MTX "
                "GCP APC CMP AGS ADX THG FOL",
    "modified": "MSE SEP TPO PTR CSO CSD KCX LLP MLY HYP OCS CME SCH",
}
TYPE = {code: cls for cls, codes in SETS.items() for code in codes.split()}
# Pre-selection tier: no class is excluded, so the molecule of interest is always
# reachable, but molecules that are structurally present rather than pharmacologically
# interesting rank below true ligands.
RANK = {"ligand": 0, "substrate": 1, "cofactor": 2, "lipid": 3, "sugar": 4,
        "additive": 5, "modified": 6, "ion": 7, "water": 8}

CORRECT_COLOUR = "#0f6b74"
ERROR_COLOUR = "#c9631a"
NEUTRAL_COLOUR = "#8a9aa0"
CUBE_EDGE = 25.0          # the conventional "25 A cube" shortcut
AUTO_MARGIN = 7.0         # tool default margin
BURIED_CUTOFF = 4.0       # "looks buried" threshold used for reporting


def fetch(pdb_id):
    path = f"{pdb_id}.pdb"
    if not os.path.exists(path):
        urllib.request.urlretrieve(
            f"https://files.rcsb.org/download/{pdb_id}.pdb", path)
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def parse_pdb(text):
    """Heavy atoms of model 1, altloc blank or A. Mirrors the tool's parser."""
    atoms, in_model = [], False
    for line in text.split("\n"):
        rec = line[:6]
        if rec == "MODEL ":
            if in_model:
                break
            in_model = True
            continue
        if rec == "ENDMDL":
            break
        if rec not in ("ATOM  ", "HETATM"):
            continue
        alt = line[16:17]
        if alt.strip() and alt != "A":
            continue
        name = line[12:16].strip()
        element = line[76:78].strip().upper() or name.strip("0123456789")[:1].upper()
        if element in ("H", "D"):
            continue
        try:
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
        except ValueError:
            continue
        atoms.append({
            "het": rec == "HETATM", "resn": line[17:20].strip(),
            "chain": line[21], "resi": int(line[22:26]),
            "xyz": (x, y, z),
        })
    return atoms


def het_groups(atoms):
    groups = {}
    for atom in atoms:
        if atom["het"]:
            key = (atom["resn"], atom["chain"], atom["resi"])
            groups.setdefault(key, []).append(atom)
    return groups


def kind(resn):
    return TYPE.get(resn, "ligand")


def auto_select(groups):
    """The molecule the tool would pre-select: by class tier, then by size."""
    candidates = [(key, atoms) for key, atoms in groups.items()
                  if kind(key[0]) != "water" and len(atoms) >= 6]
    if not candidates:
        candidates = [(key, atoms) for key, atoms in groups.items()
                      if kind(key[0]) != "water"]
    candidates.sort(key=lambda kv: (RANK[kind(kv[0][0])], -len(kv[1]), kv[0][1]))
    return candidates[0][0] if candidates else None


def centroid(atoms):
    n = len(atoms)
    return tuple(sum(a["xyz"][i] for a in atoms) / n for i in range(3))


def box(atoms, margin, cube=True):
    """Centre and per-axis edge, sized so the margin holds on every face."""
    centre = centroid(atoms)
    half = [max(abs(a["xyz"][i] - centre[i]) for a in atoms) for i in range(3)]
    size = [math.ceil(2 * half[i] + 2 * margin) for i in range(3)]
    if cube:
        size = [max(size)] * 3
    return centre, size


def nearest_protein(protein, point):
    return min(math.dist(point, a["xyz"]) for a in protein)


def atoms_inside(atoms, centre, edge):
    half = edge / 2
    return sum(1 for a in atoms
               if all(abs(a["xyz"][i] - centre[i]) <= half for i in range(3)))


def analyse(pdb_id):
    atoms = parse_pdb(fetch(pdb_id))
    protein = [a for a in atoms if not a["het"]]
    groups = het_groups(atoms)
    key = auto_select(groups)
    if key is None:
        return {"pdb": pdb_id, "note": "no ligand-class group found"}

    resn = key[0]
    site = groups[key]
    pooled = [a for k, v in groups.items() if k[0] == resn for a in v]
    n_copies = sum(1 for k in groups if k[0] == resn)

    correct_centre, correct_size = box(site, AUTO_MARGIN)
    pooled_centre, pooled_size = box(pooled, AUTO_MARGIN)

    bbox_mid = tuple(
        (min(a["xyz"][i] for a in site) + max(a["xyz"][i] for a in site)) / 2
        for i in range(3))

    return {
        "pdb": pdb_id, "ligand": resn, "ligand_class": kind(resn),
        "chain": key[1], "resi": key[2],
        "n_copies": n_copies, "n_ligand_atoms": len(site),
        "correct_centre": correct_centre, "correct_edge": correct_size[0],
        "pooled_centre": pooled_centre, "pooled_edge": pooled_size[0],
        "displacement": math.dist(correct_centre, pooled_centre),
        "centroid_vs_bbox_mid": math.dist(correct_centre, bbox_mid),
        "near_correct": nearest_protein(protein, correct_centre),
        "near_pooled": nearest_protein(protein, pooled_centre),
        "atoms_in_cube_at_pooled": atoms_inside(site, pooled_centre, CUBE_EDGE),
        "note": "",
    }


def write_csv(rows, path="gridbox_pilot_benchmark.csv"):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "pdb_id", "auto_selected_ligand", "assigned_class", "chain", "resi", "n_copies",
            "n_ligand_atoms", "correct_centre_xyz", "correct_cube_edge_A",
            "pooled_centre_xyz", "pooled_cube_edge_A", "displacement_A",
            "centroid_vs_bbox_midpoint_A", "near_protein_correct_A",
            "near_protein_pooled_A", f"ligand_atoms_in_{CUBE_EDGE:.0f}A_cube_at_pooled",
            "note"])
        for r in rows:
            if r.get("note") and "ligand" not in r:
                writer.writerow([r["pdb"]] + [""] * 15 + [r["note"]])
                continue
            writer.writerow([
                r["pdb"], r["ligand"], r["ligand_class"], r["chain"], r["resi"], r["n_copies"],
                r["n_ligand_atoms"],
                " ".join(f"{v:.3f}" for v in r["correct_centre"]), r["correct_edge"],
                " ".join(f"{v:.3f}" for v in r["pooled_centre"]), r["pooled_edge"],
                f"{r['displacement']:.1f}", f"{r['centroid_vs_bbox_mid']:.2f}",
                f"{r['near_correct']:.2f}", f"{r['near_pooled']:.2f}",
                r["atoms_in_cube_at_pooled"], r["note"]])
    return path


def make_figure(multi, path="fig_box_failure_modes.png"):
    multi = sorted(multi, key=lambda r: r["displacement"])
    labels = [f"{r['pdb']} ({r['ligand']}"
              + (f"\u00d7{r['n_copies']})" if r["n_copies"] > 2 else ")")
              for r in multi]
    y = np.arange(len(multi))
    near_correct = np.array([r["near_correct"] for r in multi])
    near_pooled = np.array([r["near_pooled"] for r in multi])
    displacement = np.array([r["displacement"] for r in multi])
    empty = [r["atoms_in_cube_at_pooled"] == 0 for r in multi]

    plt.rcParams.update({"font.size": 8, "axes.spines.top": False,
                         "axes.spines.right": False})
    fig, (ax_a, ax_b) = plt.subplots(
        1, 2, figsize=(7.0, 3.5), gridspec_kw={"wspace": 0.42})

    ax_a.axvspan(near_correct.min(), near_correct.max(),
                 color=CORRECT_COLOUR, alpha=0.10, lw=0, zorder=0)
    for i in y:
        ax_a.plot([near_correct[i], near_pooled[i]], [i, i],
                  color=NEUTRAL_COLOUR, lw=0.8, zorder=1)
    ax_a.scatter(near_correct, y, s=34, color=CORRECT_COLOUR, zorder=3,
                 label="Correct single-copy pocket")
    ax_a.scatter(near_pooled, y, s=34, color=ERROR_COLOUR, marker="D", zorder=3,
                 label="Centre of all copies pooled")
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(labels)
    ax_a.set_xlabel("Distance from box centre to\nnearest protein atom (Å)")
    ax_a.set_title("Both centres look equally buried", loc="left", pad=14)
    ax_a.set_xlim(0, max(7.6, near_pooled.max() + 1))
    ax_a.text((near_correct.min() + near_correct.max()) / 2, -1.08,
              "range spanned by\nthe correct centres", fontsize=6,
              color=CORRECT_COLOUR, ha="center", va="center", linespacing=1.25)
    ax_a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.33), frameon=False,
                handletextpad=0.3, labelspacing=0.35, fontsize=7)

    for i in y:
        ax_b.plot([0, displacement[i]], [i, i], color=NEUTRAL_COLOUR, lw=0.8, zorder=1)
        ax_b.scatter(displacement[i], i, s=38, zorder=3, marker="D",
                     color=ERROR_COLOUR if empty[i] else "white",
                     edgecolor=ERROR_COLOUR, linewidth=1.1)
    ax_b.set_yticks(y)
    ax_b.set_yticklabels([])
    ax_b.set_xlabel("Displacement of the pooled centre\nfrom the true pocket (Å)")
    ax_b.set_title("…but it is tens of ångströms away", loc="left", pad=14)
    ax_b.set_xlim(0, displacement.max() * 1.15)
    ax_b.legend(handles=[
        Line2D([], [], marker="D", ls="", mfc=ERROR_COLOUR, mec=ERROR_COLOUR, ms=5.5,
               label=f"{CUBE_EDGE:.0f} Å box holds no true-ligand atoms"),
        Line2D([], [], marker="D", ls="", mfc="white", mec=ERROR_COLOUR, ms=5.5,
               label=f"{CUBE_EDGE:.0f} Å box holds some true-ligand atoms")],
        loc="upper center", bbox_to_anchor=(0.5, -0.33), frameon=False,
        handletextpad=0.3, labelspacing=0.35, fontsize=7)

    for ax in (ax_a, ax_b):
        ax.set_ylim(len(multi) - 0.5, -1.55)
    for ax, letter in ((ax_a, "a"), (ax_b, "b")):
        ax.text(-0.02, 1.06, letter, transform=ax.transAxes,
                fontweight="bold", fontsize=10, ha="right", va="bottom")

    fig.savefig(path, dpi=300, bbox_inches="tight")
    return path


def main():
    rows = [analyse(pdb_id) for pdb_id in PDB_IDS]
    resolved = [r for r in rows if "ligand" in r]
    multi = [r for r in resolved if r["n_copies"] > 1]

    csv_path = write_csv(rows)
    fig_path = make_figure(multi)

    offsets = [r["centroid_vs_bbox_mid"] for r in resolved]
    shifts = [r["displacement"] for r in multi]
    empty = [r for r in multi if r["atoms_in_cube_at_pooled"] == 0]
    looks_buried = [r for r in multi if r["near_pooled"] <= BURIED_CUTOFF]

    print(f"entries analysed: {len(resolved)} of {len(rows)}")
    print(f"no ligand-class group: "
          f"{[r['pdb'] for r in rows if 'ligand' not in r] or 'none'}")
    print(f"multiple ligand copies: {len(multi)}/{len(resolved)} "
          f"({100 * len(multi) / len(resolved):.0f}%)")
    print(f"pooled-centre displacement: median {statistics.median(shifts):.1f} A, "
          f"range {min(shifts):.1f}-{max(shifts):.1f} A")
    print(f"{CUBE_EDGE:.0f} A cube at pooled centre holds no true-ligand atoms: "
          f"{len(empty)}/{len(multi)}")
    print(f"pooled centre within {BURIED_CUTOFF:.1f} A of protein "
          f"(i.e. still looks buried): {len(looks_buried)}/{len(multi)}")
    print(f"correct centres {min(r['near_correct'] for r in multi):.1f}-"
          f"{max(r['near_correct'] for r in multi):.1f} A from protein; pooled centres "
          f"{min(r['near_pooled'] for r in multi):.1f}-"
          f"{max(r['near_pooled'] for r in multi):.1f} A")
    print(f"centroid vs bounding-box midpoint: median "
          f"{statistics.median(offsets):.2f} A, max {max(offsets):.2f} A")
    print(f"wrote {csv_path} and {fig_path}")


if __name__ == "__main__":
    main()
