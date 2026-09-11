"""Figure 1 (thesis figure): the two halves of an optimality claim are not symmetric."""
import sys; sys.path.insert(0, __file__.rsplit("/",1)[0])
from figstyle import *
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

setup()
fig, ax = plt.subplots(figsize=(6.9, 3.35))
ax.set_xlim(0, 100); ax.set_ylim(0, 50); ax.axis("off")

def box(x, y, w, h, lines, fill=PALE, edge=INK, ls="-", lw=0.9,
        fs=7.9, tc=INK, bold=False, subfs=6.7, subc=MID):
    """lines = [main] or [main, sub1, sub2...]; vertically centred as a block."""
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle="round,pad=0,rounding_size=1.1",
                 fc=fill, ec=edge, lw=lw, linestyle=ls, zorder=2))
    n = len(lines)
    gaps = [0.0] + [1.0]*(n-1)
    unit = h / (n + 0.9)
    total = sum(gaps) * unit + n*unit*0.0
    ytop = y + h/2 + (n-1)*unit/2
    for i, t in enumerate(lines):
        yy = ytop - i*unit
        ax.text(x+w/2, yy, t, ha="center", va="center",
                fontsize=fs if i == 0 else subfs,
                color=tc if i == 0 else subc, zorder=3,
                fontweight="bold" if (bold and i == 0) else "normal")

def arrow(x1, y1, x2, y2, color=INK, ls="-", lw=0.9, ms=7):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                 mutation_scale=ms, color=color, lw=lw, linestyle=ls,
                 shrinkA=0, shrinkB=0, zorder=4,
                 mutation_aspect=1))

# ---- header -------------------------------------------------------------
ax.text(50, 48.2, r'the claim:   "the minimum is $m$"', ha="center", va="center",
        fontsize=9.4, color=INK, fontweight="bold")
arrow(45.5, 46.6, 26.5, 43.6, color=MID, lw=0.85)
arrow(54.5, 46.6, 73.5, 43.6, color=MID, lw=0.85)

# ---- column headings ----------------------------------------------------
ax.text(24, 41.9, "UPPER BOUND", ha="center", fontsize=8.4, fontweight="bold", color=INK)
ax.text(24, 39.3, r'"a program of size $m$ exists"', ha="center", fontsize=7.6, color=MID)
ax.text(76, 41.9, "LOWER BOUND", ha="center", fontsize=8.4, fontweight="bold", color=INK)
ax.text(76, 39.3, r'"no program of size $m\!-\!1$ exists"', ha="center", fontsize=7.6, color=MID)

ax.add_patch(Rectangle((6, 35.4), 36, 2.6, fc=DEEP, ec="none", zorder=2))
ax.text(24, 36.7, "WITNESSED", ha="center", va="center", fontsize=7.5,
        color="white", fontweight="bold", zorder=3)
ax.add_patch(Rectangle((58, 35.4), 36, 2.6, fc="white", ec=GREY, lw=0.9,
                       ls=(0, (2.5, 1.6)), zorder=2))
ax.text(76, 36.7, "NOT WITNESSED", ha="center", va="center", fontsize=7.5,
        color=GREY, fontweight="bold", zorder=3)

# ---- left column --------------------------------------------------------
box(9, 29.9, 30, 4.0, ["circuit   (the object)"], fill=PALE, fs=8.0)
arrow(24, 29.7, 24, 27.5)

L = [("Layer 1    re-execution",          r"$\mu$s  ·  shares no code with search"),
     ("Layer 2    symbolic equivalence",  r"$\forall x.\ \mathrm{circuit}(x)=Mx$  ·  Z3"),
     ("Layer 3    proof term",            r"Lean 4 kernel  ·  axioms: [propext]")]
y = 22.6
for lab, sub in L:
    box(6, y, 36, 4.9, [lab, sub], fill=FAINT, fs=7.6, subfs=6.6)
    if y > 14:
        arrow(24, y, 24, y - 1.55)
    y -= 6.45

arrow(24, 9.7, 24, 7.6)
box(6, 2.6, 36, 5.0, ["machine-checked certificate"], fill=DEEP, edge=DEEP,
    fs=8.2, tc="white", bold=True)

# ---- right column -------------------------------------------------------
box(61, 29.9, 30, 4.0, ["(no object exists)"], fill="white", edge=GREY,
    ls=(0, (2.5, 1.6)), fs=8.0, tc=GREY)
arrow(76, 29.7, 76, 27.5, color=GREY)

box(58, 19.9, 36, 7.6,
    ["SAT solver returns UNSAT",
     r"$10^4\!+$ lines of C: inprocessing,",
     "clause deletion, variable elimination"],
    fill=FAINT, fs=7.9, subfs=6.6)
arrow(76, 19.7, 76, 17.6, color=GREY)

box(58, 10.4, 36, 7.2,
    ["nothing to re-execute,", "nothing to check"],
    fill="white", edge=GREY, ls=(0, (2.5, 1.6)),
    fs=7.7, tc=GREY, subfs=7.7, subc=GREY)
arrow(76, 10.2, 76, 7.9, color=GREY)

box(58, 2.6, 36, 5.0, ["an unaudited assertion"], fill="white", edge=GREY,
    ls=(0, (2.5, 1.6)), fs=8.2, tc=GREY, bold=True)

# ---- the gap ------------------------------------------------------------
ax.plot([50, 50], [2.0, 38.4], color=LIGHTGREY, lw=0.7, ls=(0, (1.4, 1.8)), zorder=1)
ax.add_patch(FancyBboxPatch((41.6, 14.9), 16.8, 6.2,
             boxstyle="round,pad=0,rounding_size=1.0", fc="white", ec=INK,
             lw=1.05, zorder=5))
ax.text(50, 19.3, "the", ha="center", va="center", fontsize=7.0, color=MID, zorder=6)
ax.text(50, 17.4, "REFUTATION", ha="center", va="center", fontsize=6.9,
        color=INK, fontweight="bold", zorder=6)
ax.text(50, 15.9, "GAP", ha="center", va="center", fontsize=6.9,
        color=INK, fontweight="bold", zorder=6)

fig.savefig("paper/figs/asymmetry.pdf")
fig.savefig("paper/figs/asymmetry.png", dpi=190)
print("wrote asymmetry")
