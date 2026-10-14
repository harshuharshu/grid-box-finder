# Supporting Information

**Grid Box Finder: A Zero-Installation Browser Tool for Defining and Checking Docking Search Boxes**

Harshita Tiwari

For submission, split this document into the separate PDFs listed in the manuscript's
Associated Content section. All box values quoted in Part C were computed from the current
RCSB coordinate files and are tabulated in `si_answer_key.csv`.

---

# Part A — Student handout

## Defining and checking a docking search box

**Time:** 90 minutes · **What you need:** a web browser · **Work:** individually or in pairs

### Why this matters

AutoDock Vina only looks for poses *inside a box you define*. If the box is in the wrong place,
Vina does not tell you. It completes normally and reports binding affinities in kcal mol⁻¹ that
look exactly like correct ones. Everything you conclude afterwards depends on six numbers you
typed before the calculation started. Today you will learn to produce those six numbers and —
more importantly — to check them.

Open the tool: **[URL]**

---

### Part 1 — Orientation (15 min)

The tool opens with a structure already loaded: rofecoxib (Vioxx) bound to human
cyclooxygenase-2, PDB entry 5KIR.

**1.1** Look at the molecule table on the left. It lists every non-protein molecule in the file.
Find the row labelled **RCX**.

| | |
|---|---|
| What class does the tool assign to RCX? | ____________________ |
| How many atoms does it have? | ____________________ |
| Which chain is it in? | ____________________ |

**1.2** The file also contains **COH**, which has more atoms than RCX. Why did the tool not
select COH as the ligand? What is COH?

> ______________________________________________________________________

**1.3** Record the box the tool gives you at the default 7 Å margin:

| centre X | centre Y | centre Z | size X | size Y | size Z |
|---|---|---|---|---|---|
| | | | | | |

**1.4** Beside the size readout the tool reports how far the ligand itself spans. Compare the two.
Roughly what fraction of the box volume is ligand, and what fraction is margin?

> ______________________________________________________________________

**1.5** Move the margin slider from 2 Å to 12 Å and watch the orange box in the 3D view. At what
margin does the box start to include parts of the protein well outside the pocket?

> ______________________________________________________________________

---

### Part 2 — The multiple-copy trap (25 min)

Most crystal structures contain more than one copy of the protein, and therefore more than one
copy of the ligand. This part shows you what happens when you select them all at once — which is
what happens by default in most other software when you select a ligand by its three-letter code.

Your assigned structure: **______** (from the list your instructor gives you)

**2.1** Load your structure. Select the drug-like ligand in chain A. Record:

| | centre X | centre Y | centre Z | cube size |
|---|---|---|---|---|
| **Correct box** (chain A only) | | | | |

**2.2** The tool should now be showing an orange warning panel about other copies of the same
molecule. Read it. Record the centre it says you would get **if all copies were pooled**:

| | centre X | centre Y | centre Z |
|---|---|---|---|
| **Pooled-copies centre** | | | |

**2.3** How far apart are the two centres? (The warning states this.)  ________ Å

**2.4** **Predict before you check.** A very common piece of advice is "use a 25 Å cube". Suppose
you used the pooled centre from 2.2 with a 25 Å cube. Would the ligand be inside that box?

> Prediction: ☐ yes ☐ partly ☐ no — because ______________________________

**2.5** Check your prediction. Half the distance across a 25 Å cube is 12.5 Å. Compare the
displacement you recorded in 2.3 against 12.5 Å. Was your prediction right?

> ______________________________________________________________________

**2.6** Now the important question. Look at the warning panel again: does it say the pooled
centre is still inside the protein, or in empty space?

> ______________________________________________________________________

**2.7** If the pooled centre is still inside the protein, what does that mean for the common
advice "just look at the 3D view and check the box is on the protein"?

> ______________________________________________________________________

---

### Part 3 — Building a box without a ligand (20 min)

Many interesting targets have no co-crystallised drug. Then you must define the site from
residues reported in the literature.

**3.1** Reload the 5KIR example and switch to the **Residues** tab. The cyclooxygenase active
site is lined by Arg120, Tyr355, Tyr385, Arg513, Val523 and Ser530. Enter them for chain A:

```
A:120 A:355 A:385 A:513 A:523 A:530
```

Record the box at a 3 Å margin:

| centre X | centre Y | centre Z | cube size |
|---|---|---|---|
| | | | |

**3.2** Compare this centre with the ligand-derived centre you recorded in 1.3. How far apart
are they?  ________ Å

**3.3** What does that agreement tell you about using literature residues when no ligand is
available?

> ______________________________________________________________________

**3.4** Now deliberately make a mistake: change one residue number to `A:9999`. What does the
tool report? Why is it useful that it says this out loud?

> ______________________________________________________________________

---

### Part 4 — Transfer and run (30 min)

**4.1** Copy the Vina configuration for your **correct** box from Part 2.1 and save it as
`config_correct.txt`. Then edit a copy, replacing only the three centre values with the
**pooled** centre from 2.2, and save it as `config_pooled.txt`. Keep the size the same.

**4.2** Dock your ligand with both configurations.

| | best affinity (kcal mol⁻¹) | did Vina report an error? |
|---|---|---|
| correct box | | |
| pooled-copy box | | |

**4.3** Open both results in a viewer. Where did the ligand end up in each case?

> ______________________________________________________________________

**4.4** **The point of today.** Vina gave you a number for the wrong box. In one or two
sentences, write down the check you will apply to every box you define from now on.

> ______________________________________________________________________

---

# Part B — Instructor notes

## Placement in the curriculum

Intended for upper-division undergraduate or master's students in medicinal chemistry,
biochemistry, or pharmacy who have had an introductory lecture on structure-based drug design.
The activity assumes no prior use of docking software and no command-line experience, but
Part 4 requires that students have access to PyRx or AutoDock Vina. If they do not, Part 4 can be
replaced by a demonstration; the conceptual content is in Parts 2 and 3.

## Preparation

The tool is a single HTML file with no installation and no server. Host it on the course page or
distribute the file itself. Verify once, on a lab machine, that the 3D panel renders — it loads a
visualisation library from a public CDN, and some institutional networks block it. The numerical
output and all warnings work without the 3D panel, so a blocked CDN degrades the activity but
does not stop it. For a fully offline deployment, download the library and reference it locally.

Students can type a four-character PDB ID straight into the tool, which fetches the structure
from rcsb.org — both PDB and mmCIF formats are read, so there is no format trap. If the
teaching network blocks outbound requests to rcsb.org, download the files in advance and put
them in a shared folder for students to drag onto the page.

## Structure assignment list for Part 2

Assign one per student or pair. All have multiple copies of the ligand. The last two are
deliberately included as instructive exceptions — see the discussion note below.

| Structure | Target | Ligand | Copies | Displacement if pooled |
|---|---|---|---|---|
| 3LN1 | COX-2 | CEL (celecoxib) | 4 | 40.8 Å |
| 2HYY | ABL kinase | STI (imatinib) | 4 | 34.1 Å |
| 1IEP | ABL kinase | STI (imatinib) | 2 | 30.9 Å |
| 4EY7 | Acetylcholinesterase | E20 (donepezil) | 2 | 29.2 Å |
| 3PP0 | HER2 kinase | 03Q | 2 | 25.2 Å |
| 5KIR | COX-2 | RCX (rofecoxib) | 2 | 24.7 Å |
| 4GBD | — | MCF | 2 | 21.2 Å |
| 4DJU | — | 0KK | 2 | 20.8 Å |
| 2P2I | — | 608 | 2 | 18.9 Å *(exception)* |

## Discussion note: the exception, and a second use for 3NY8

Deliberately assign 2P2I to at least one pair and bring it into the whole-class discussion. There
the pooled box still retains 11 of the ligand's 30 atoms, so the error is partial rather than
total. That case makes the intended point better than the dramatic ones: the error is *not* quite
universal, so a student cannot learn a rule of thumb and must actually check each structure. The
warning panel still fires, which is the correct behaviour — it reports the displacement and lets
the student judge.

PDB 3NY8 (the β2-adrenergic receptor) is worth loading as a demonstration for a different reason.
It contains the inverse agonist JRZ together with two copies of cholesterol, two of monoolein, and
several detergent molecules. The tool pre-selects JRZ because lipids rank below true ligands, but
the table shows the whole crystallisation environment at once — a good opening for the question
"which of these would you dock against, and why?". Cholesterol is also elongated, so selecting it
manually and toggling the cube constraint shows how much search volume a cube wastes on a
non-spherical site.

## Common student difficulties

- **Typing the PDB ID wrong.** The fetch needs exactly four characters. If rcsb.org is
  unreachable from the teaching network the tool says so; fall back to the pre-downloaded files.
- **Selecting the cofactor.** In 5KIR, COH (a protoporphyrin derivative) has twice as many atoms
  as rofecoxib. Students who assume "biggest = the drug" pick it. The class label is the cue, and
  the discussion of why a haem is not a drug target here is worth the two minutes.
- **Assuming the pre-selection is always right.** It is a heuristic. Tell students explicitly
  that when the molecule of interest is itself a cofactor analogue — biotin, methotrexate, a
  non-hydrolysable ATP analogue — the tool files it as a cofactor and will not pre-select it.
- **Reading the warning as an error.** The multiple-copy panel is informational: the box
  currently shown is correct. Students sometimes think they have done something wrong.
- **Confusing centre with size.** Six numbers, two meanings. The recording tables are laid out to
  separate them.

## Timing

Parts 1–3 reliably fit 60 minutes. Part 4 runs long if students have not used PyRx before;
consider pre-loading the receptor and ligand files.

---

# Part C — Answer key

Values below are for the current RCSB coordinate files, 7 Å margin, cube constraint on, unless
stated. Student values should match to the nearest 0.1 Å; small differences arise if a student
changes the margin. Full table: `si_answer_key.csv`.

### Part 1 (5KIR)

- **1.1** RCX is classed as *Likely drug / ligand*; 22 heavy atoms; chain A (also present in
  chain B).
- **1.2** COH is classed as *Cofactor*. It is cobalt protoporphyrin IX (C₃₄H₃₂CoN₄O₄), the
  redox-inactive haem substitute used in cyclooxygenase crystallography, bound at the peroxidase
  site. It is a prosthetic group, not the pharmacological target of rofecoxib (RCX, C₁₇H₁₄O₄S),
  which binds in the cyclooxygenase channel.
- **1.3** Centre (23.206, 1.318, 34.259) Å; cube edge 24 Å. *(Per-axis sizing gives 21 × 24 × 23.)*
- **1.4** The ligand spans roughly 6.8 × 8.2 × 7.9 Å ≈ 440 Å³ of bounding box, against a 24 Å
  cube of 13 824 Å³ — the ligand's own bounding box is about 3% of the search volume. Students
  are usually surprised by this; it motivates Part 4's discussion of search volume.
- **1.5** Qualitative. Around 10–12 Å the box visibly extends past the mouth of the channel.

### Part 2 — by structure

All values computed with the v1.2.0 classification and the symmetric sizing rule
(`ceil(2 x max|atom - centre| + 2 x margin)`), 7 Å margin, cube constrained. Also in
`si_answer_key.csv`.

| Structure | Correct centre (Å) | Cube | Pooled centre (Å) | Displacement | Ligand atoms in a 25 Å cube at the pooled centre |
|---|---|---|---|---|---|
| 3LN1 | 30.989, −22.284, −16.507 | 26 | 48.103, −33.801, 18.659 | 40.8 Å | 0 / 26 |
| 2HYY | 14.251, 15.283, 17.632 | 32 | 37.201, 37.003, 30.442 | 34.1 Å | 0 / 37 |
| 1IEP | 15.614, 53.380, 15.455 | 32 | 14.081, 75.123, 37.365 | 30.9 Å | 0 / 37 |
| 4EY7 | −14.108, −43.833, 27.670 | 28 | −1.582, −50.192, 2.101 | 29.2 Å | 0 / 28 |
| 3PP0 | 17.099, 16.549, 26.601 | 30 | 25.856, 30.612, 7.552 | 25.2 Å | 0 / 34 |
| 5KIR | 23.206, 1.318, 34.259 | 24 | 23.459, 20.752, 19.058 | 24.7 Å | 0 / 22 |
| 4GBD | −37.908, −7.466, 38.697 | 25 | −31.873, 0.123, 19.869 | 21.2 Å | 0 / 21 |
| 4DJU | 21.616, 10.988, 21.549 | 23 | 21.575, 22.637, 38.824 | 20.8 Å | 0 / 20 |
| 2P2I | 38.203, 35.466, 12.087 | 32 | 31.373, 19.851, 20.158 | 18.9 Å | 11 / 30 |

- **2.4 / 2.5** Any displacement greater than about 12.5 Å plus the ligand's own half-span puts
  the ligand wholly outside a 25 Å cube. That is the case for eight of the nine structures; 2P2I
  is the single partial case, retaining 11 of 30 atoms.
- **2.6 / 2.7** For every structure except 3LN1, the pooled centre is within about 3 Å of a
  protein atom — it sits at the interface between the two chains. The intended conclusion: "the
  box looks like it is on the protein" is not a valid check, because a box between two chains
  also looks like it is on the protein. The displacement, not the appearance, is the evidence.
  3LN1 is the one case where the pooled centre (6.6 Å from protein) is far enough into solvent
  that the tool's distance warning fires.


### Part 3 (5KIR, residues, 3 Å margin)

- **3.1** The six residues contribute 59 heavy atoms in chain A. Centre
  (22.119, 2.916, 34.389) Å; cube edge 28 Å. *(Per-axis sizing gives 27 × 28 × 23.)*
- **3.2** 1.9 Å from the ligand-derived centre of 1.3.
- **3.3** Intended answer: a correctly chosen set of literature pocket residues reproduces the
  ligand-derived site to within about 2 Å, which is well inside the margin. Residue-defined boxes
  are therefore a sound fallback for apo structures — provided the residue numbering in the paper
  matches the numbering in the file, which is the failure mode probed next.
- **3.4** The tool reports the residue as not found and states how many were matched. Without
  that message a box built from five residues instead of six — or from zero, if the numbering
  scheme differs — would be produced silently. Numbering mismatches between a paper and a PDB
  entry (construct numbering, mature versus precursor sequence) are common.

### Part 4

Both runs complete. Affinities depend on the ligand and Vina version, so no key value is given;
the observation that matters is that the pooled-copy run **reports a plausible affinity and no
error**, with the ligand placed at the chain–chain interface rather than in the pocket.

A good answer to 4.4 names a check that is quantitative rather than visual — for example: confirm
that only one copy of the ligand was selected; confirm the box centre is within a few ångströms
of the known pocket residues; confirm the box edge is not much more than about 25–30 Å.

---

# Part D — Pre/post assessment instrument

Administer identically before and after the session. Items 1–8 are scored 1/0; items 9 and 10 are
scored on the rubric below. **Not yet administered** — see the manuscript's Assessment section.

**1.** In AutoDock Vina, the search box determines:
(a) which protein conformations are sampled (b) the region of space in which ligand poses are
generated (c) the scoring function used (d) the number of output poses
→ **b**

**2.** If the search box is placed away from the binding site, Vina will:
(a) report an error and stop (b) automatically re-centre the box (c) complete and report binding
affinities (d) return zero poses
→ **c**

**3.** A PDB file contains two protein chains, A and B, each with one copy of ligand LIG. You
select "all atoms of LIG" and compute the centre. That centre will most likely be:
(a) in the chain A pocket (b) in the chain B pocket (c) between the two chains (d) at the origin
→ **c**

**4.** In the situation in question 3, the resulting box centre is 25 Å from either pocket. Using
a 25 Å cube at that centre, the ligand's true binding site will be:
(a) at the centre of the box (b) near the edge of the box (c) outside the box (d) impossible to say
→ **c**

**5.** Which of these HETATM molecules is *least* likely to be the drug you want to dock against?
(a) a 30-atom molecule with a sulfonamide group (b) GOL (c) a 28-atom indole derivative
(d) a 22-atom molecule with three fluorines
→ **b** *(glycerol, a cryoprotectant)*

**6.** A docking box 60 Å on each side, compared with one 25 Å on each side:
(a) always gives better results because it searches more space (b) searches a volume roughly 14
times larger, making the search less reliable at fixed exhaustiveness (c) is required for large
proteins (d) makes no difference to Vina
→ **b**

**7.** You are told "the box is fine, you can see it is sitting on the protein in the 3D view."
This reasoning is:
(a) sufficient (b) sufficient if the protein is a monomer (c) insufficient, because a box between
two chains also appears to be on the protein (d) insufficient only for membrane proteins
→ **c**

**8.** You have an apo structure and a paper listing the pocket residues. The best way to define
the box is:
(a) centre it on the whole protein (b) centre it on the geometric centre of those residues
(c) guess from the surface (d) it cannot be done without a ligand
→ **b**

**9.** *(Open response.)* You are shown a docking box defined on a two-chain structure: centre
(23.5, 20.8, 19.1), size 62 × 62 × 62 Å, built by selecting every copy of the ligand. Give two
specific reasons to reject this box, and state what you would do instead.

**10.** *(Open response.)* Describe one check you would run on a search box before starting a
docking calculation, and state what result would make you reject the box.

### Rubric for items 9 and 10

| Score | Criterion |
|---|---|
| 0 | No answer, or restates the question |
| 1 | Identifies that something is wrong but gives no mechanism (e.g. "the box is too big") |
| 2 | Identifies one correct, specific problem with a mechanism (pooled copies displace the centre; or 62 Å is far above a workable search volume) |
| 3 | Identifies both problems and proposes a correct remedy (select a single copy; re-derive centre and size from that copy) |

**Suggested analysis.** Report item-level pre/post proportions for items 1–8 and mean rubric
scores for items 9–10, with a paired test (McNemar for the binary items, Wilcoxon signed-rank for
the rubric items) and an effect size. Items 3, 4, and 7 together form the multiple-copy
misconception subscale and should be reported as a group.
