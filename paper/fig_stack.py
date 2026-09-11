"""Figure: the construction-side stack -- what each layer establishes, trusts, costs."""
import sys; sys.path.insert(0, __file__.rsplit("/",1)[0])
from figstyle import *
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

setup()
fig = plt.figure(figsize=(6.9, 2.30))
gs  = fig.add_gridspec(1, 2, width_ratios=[1.44, 1.0], wspace=0.40)
axL = fig.add_subplot(gs[0, 0]); axR = fig.add_subplot(gs[0, 1])

# ---------------- (a) the ladder ----------------------------------------
axL.set_xlim(0, 100); axL.set_ylim(0, 46); axL.axis("off")
LAYERS = [
    ("Layer 1   re-execution", r"$P \vDash M$  in the bitmask model", "the abstraction itself", PALE),
    ("Layer 2   symbolic equivalence", r"$\forall x.\ c(x) = Mx$  over $\mathrm{GF}(2)$", "Z3", MID),
    ("Layer 3   Lean 4 proof term", r"the same, as a checked term", r"Lean kernel $+$ $\mathtt{propext}$", DEEP),
]
y, xs = 3.0, [3, 3, 3]
for i, (name, est, trust, col) in enumerate(LAYERS):
    x0 = xs[i]; w = 100 - x0 - 2
    axL.add_patch(FancyBboxPatch((x0, y), w, 11.6,
                  boxstyle="round,pad=0,rounding_size=1.0", fc=col, ec=INK,
                  lw=0.9, zorder=3))
    tc = "white" if col in (DEEP, MID) else INK
    sc = "#dbe5ee" if col in (DEEP, MID) else MID
    axL.text(x0+2.6, y+8.5, name, ha="left", va="center", fontsize=7.4,
             color=tc, fontweight="bold", zorder=4)
    axL.text(x0+2.6, y+5.4, "establishes:  " + est, ha="left", va="center",
             fontsize=6.6, color=tc, zorder=4)
    axL.text(x0+2.6, y+2.4, "trusts:  " + trust, ha="left", va="center",
             fontsize=6.6, color=sc, zorder=4)
    y += 13.5

axL.add_patch(FancyArrowPatch((1.0, 4.0), (1.0, 41.0), arrowstyle="-|>",
              mutation_scale=8, color=INK, lw=1.0, shrinkA=0, shrinkB=0, zorder=4))
axL.text(-1.2, 22.5, "strictly stronger obligation", rotation=90, ha="center",
         va="center", fontsize=6.7, color=INK)
axL.set_title("(a)  three layers, no shared code", loc="left", fontweight="bold")

# ---------------- (b) measured cost -------------------------------------
# Layer 1: 17.5 us median, re-verifying the 108-gate Paar circuit for AES MixColumns.
# Layer 2: runs/layer2_timing.jsonl -- fast encoding 0.020-0.131 s but returns
#          `unknown` on 1 of the 5 cipher matrices; complete encoding 2.59-4.58 s, 5/5.
# Layer 3: runs/lean/axioms.txt -- 4.99-7.60 s over the 13 emitted certificates.
RANGES = [
    (17.5e-6, 17.5e-6, "17.5 $\\mu$s",  "Layer 1",             None),
    (0.0205,  0.1312,  "0.02–0.13 s",  "Layer 2  fast",      "4/5"),
    (2.59,    4.58,    "2.6–4.6 s",    "Layer 2  full",  "5/5"),
    (4.99,    7.60,    "5.0–7.6 s",    "Layer 3",            None),
]
ypos = list(range(len(RANGES)))[::-1]
for yp, (lo, hi, lab, _n, tag) in zip(ypos, RANGES):
    if hi > lo:
        axR.plot([lo, hi], [yp, yp], color=INK, lw=4.6, solid_capstyle="butt", zorder=3)
    else:
        axR.plot([lo], [yp], marker="|", ms=10, mew=2.0, color=INK, zorder=3)
    axR.text(hi * 2.0, yp, lab, ha="left", va="center", fontsize=6.7, color=INK)
    if tag:
        axR.text(lo / 2.2, yp, tag, ha="right", va="center", fontsize=6.0,
                 color=MID if tag == "5/5" else GREY,
                 fontweight="bold" if tag == "4/5" else "normal")
axR.set_xscale("log")
axR.set_xlim(2.2e-6, 2.6e3)
axR.set_ylim(-0.68, len(RANGES) - 0.32)
axR.set_yticks(ypos)
axR.set_yticklabels([r[3] for r in RANGES])
axR.set_xticks([1e-5, 1e-3, 1e-1, 1e1])
axR.set_xlabel("cost per circuit (s, log scale)")
axR.set_title("(b)  measured, over five decades", loc="left", fontweight="bold")
axR.tick_params(axis="y", length=0)
despine(axR, keep=("bottom",))

fig.savefig("paper/figs/stack.pdf")
fig.savefig("paper/figs/stack.png", dpi=190)
print("wrote stack")
