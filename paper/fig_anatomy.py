"""Figure 3: what one certified optimality result actually ships.

Instance rand_n8_m8_d0.3_s11 (the median instance by proof size).
Every number is transcribed from runs/certified_decisive.jsonl; the program is
the solver's witness at k=8, re-verified by slp.instance.verify (returns 8).
"""
import sys; sys.path.insert(0, __file__.rsplit("/",1)[0])
from figstyle import *
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

setup()
fig, ax = plt.subplots(figsize=(6.9, 3.24))
ax.set_xlim(0, 100); ax.set_ylim(0, 46); ax.axis("off")
MONO = {"family": "monospace"}

def panel(x, y, w, h, fill="white", edge=INK, lw=0.95, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.0",
                 fc=fill, ec=edge, lw=lw, linestyle=ls, zorder=2))

def arrow(x1, y1, x2, y2, color=INK, lw=0.9, ms=7):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                 mutation_scale=ms, color=color, lw=lw, shrinkA=0, shrinkB=0, zorder=5))

def tick(x, y):
    ax.plot([x, x+0.75], [y-0.55, y-1.45], color=DEEP, lw=1.25, zorder=6,
            solid_capstyle="round")
    ax.plot([x+0.75, x+2.3], [y-1.45, y+0.85], color=DEEP, lw=1.25, zorder=6,
            solid_capstyle="round")

# ---------- header -------------------------------------------------------
ax.text(50, 44.6, r"instance $\mathtt{rand\_n8\_m8\_d0.3\_s11}$    ·    "
                  r"claim:  the minimum is $8$ gates",
        ha="center", va="center", fontsize=8.5, color=INK, fontweight="bold")

# ---------- left: the witness -------------------------------------------
panel(3, 4.6, 44.5, 36.8, fill="#fbfcfd")
ax.add_patch(Rectangle((3, 38.0), 44.5, 3.4, fc=DEEP, ec="none", zorder=3))
ax.text(25.25, 39.7, r"UPPER BOUND   ·   witness at $m=8$", ha="center",
        va="center", fontsize=7.7, color="white", fontweight="bold", zorder=4)

prog = [("s8",  "x1", "x3"), ("s9",  "x0", "x5"), ("s10", "x4", "x5"),
        ("s11", "x1", "s10"), ("s12", "x7", "s11"), ("s13", "x2", "s9"),
        ("s14", "x4", "x7"), ("s15", "s10", "s13")]
ax.add_patch(FancyBboxPatch((5.4, 23.8), 39.7, 12.6,
             boxstyle="round,pad=0,rounding_size=0.8", fc="white", ec=SOFT,
             lw=0.8, zorder=3))
for i, (o, a, b) in enumerate(prog):
    col = 5.4 + 1.9 + (i % 2) * 19.6
    row = 34.4 - (i // 2) * 2.75
    ax.text(col, row, f"{o:>3} = {a} ^ {b}", ha="left", va="center",
            fontsize=6.9, color=INK, zorder=4, **MONO)

checks = [("re-executed from scratch",      r"$8$ gates, all targets realised"),
          ("Z3: " + r"$\forall x.\ c(x)=Mx$", r"whole input space, $0.22$ s"),
          ("Lean 4 kernel", r"axioms: $\mathtt{[propext]}$")]
y = 20.4
for lab, sub in checks:
    tick(6.4, y + 1.15)
    ax.text(10.2, y + 1.65, lab, ha="left", va="center", fontsize=7.2, color=INK)
    ax.text(10.2, y - 0.05, sub, ha="left", va="center", fontsize=6.4, color=MID)
    y -= 4.4

ax.add_patch(Rectangle((5.4, 5.9), 39.7, 3.4, fc=PALE, ec=INK, lw=0.85, zorder=3))
ax.text(25.25, 7.6, r"$\Rightarrow$  $8$ gates suffice",
        ha="center", va="center", fontsize=7.9, color=INK,
        fontweight="bold", zorder=4)

# ---------- right: the refutation ---------------------------------------
panel(52.5, 4.6, 44.5, 36.8, fill="#fbfcfd")
ax.add_patch(Rectangle((52.5, 38.0), 44.5, 3.4, fc=DEEP, ec="none", zorder=3))
ax.text(74.75, 39.7, r"LOWER BOUND   ·   refutation at $k=7$", ha="center",
        va="center", fontsize=7.7, color="white", fontweight="bold", zorder=4)

steps = [("CNF encoding",          r"$1{,}010$ vars  ·  $17{,}636$ clauses"),
         ("Glucose 4.2 → UNSAT",   r"$0.17$ s, emitting a DRAT proof"),
         ("DRAT proof object",     r"$18{,}118$ lines  ·  $0.91$ MB"),
         ("drat-trim  (third party)", r"$\mathtt{s\ VERIFIED}$  in  $0.24$ s")]
y = 34.3
for i, (lab, sub) in enumerate(steps):
    ax.add_patch(FancyBboxPatch((54.9, y - 2.15), 39.7, 4.55,
                 boxstyle="round,pad=0,rounding_size=0.8", fc="white",
                 ec=SOFT if i < 3 else DEEP, lw=0.8 if i < 3 else 1.15, zorder=3))
    ax.text(57.0, y + 0.85, lab, ha="left", va="center", fontsize=7.2,
            color=INK, zorder=4, fontweight="bold" if i == 3 else "normal")
    ax.text(57.0, y - 0.85, sub, ha="left", va="center", fontsize=6.4,
            color=MID, zorder=4)
    if i == 3:
        tick(90.2, y + 1.2)
    if i < 3:
        arrow(74.75, y - 2.3, 74.75, y - 3.5, color=MID, lw=0.85)
    y -= 6.5

ax.text(74.75, 11.0, r"proof $\mathtt{sha256}$ 95fb1b6f…",
        ha="center", va="center", fontsize=6.4, color=MID, zorder=4)
ax.add_patch(Rectangle((54.9, 5.9), 39.7, 3.4, fc=PALE, ec=INK, lw=0.85, zorder=3))
ax.text(74.75, 7.6, r"$\Rightarrow$  $7$ gates impossible",
        ha="center", va="center", fontsize=7.9, color=INK,
        fontweight="bold", zorder=4)

# ---------- join ---------------------------------------------------------
ax.plot([50, 50], [5.4, 37.0], color=LIGHTGREY, lw=0.7, ls=(0, (1.4, 1.8)), zorder=1)
ax.text(50, 22.5, "+", ha="center", va="center", fontsize=13, color=MID, zorder=6,
        bbox=dict(boxstyle="circle,pad=0.20", fc="white", ec=LIGHTGREY, lw=0.8))

fig.savefig("paper/figs/anatomy.pdf")
fig.savefig("paper/figs/anatomy.png", dpi=190)
print("wrote anatomy")
