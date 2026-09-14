"""Figure 1: an optimality claim has two halves, and only one can be checked.

Deliberately typographic rather than diagrammatic: booktabs-style rules, no
boxes, no arrows. The three empty slots on the right are the argument.
"""
import sys; sys.path.insert(0, __file__.rsplit("/",1)[0])
from figstyle import *
import matplotlib.pyplot as plt

setup()
fig, ax = plt.subplots(figsize=(6.9, 2.72))
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

GUT   = 15.5     # right edge of the row-label gutter
COL_L = 19.5     # left column text origin
COL_R = 60.0     # right column text origin
COL_W = 34.5     # width used for the cost / slot alignment
X0, X1 = 0.0, 100.0

def rule(y, lw):
    ax.plot([X0, X1], [y, y], color=INK, lw=lw, solid_capstyle="butt", zorder=2)

def rowlabel(y, line1, line2=None):
    ax.text(GUT, y, line1, ha="right", va="baseline", fontsize=6.9, color=MID)
    if line2:
        ax.text(GUT, y - 5.9, line2, ha="right", va="baseline", fontsize=6.9, color=MID)

# the single claim both columns come from
ax.text(50, 95.0, r"one claim:   the minimum is $m$", ha="center", va="baseline",
        fontsize=8.0, color=MID, style="italic")

rule(89.0, 1.15)

ax.text(COL_L, 81.0, "UPPER BOUND", ha="left", va="baseline",
        fontsize=8.4, color=INK, fontweight="bold")
ax.text(COL_R, 81.0, "LOWER BOUND", ha="left", va="baseline",
        fontsize=8.4, color=INK, fontweight="bold")
ax.text(COL_L, 72.6, r"$\exists P.\ |P| = m \ \wedge\ P \vDash M$",
        ha="left", va="baseline", fontsize=7.9, color=INK)
ax.text(COL_R, 72.6, r"$\neg\,\exists P.\ |P| = m\!-\!1 \ \wedge\ P \vDash M$",
        ha="left", va="baseline", fontsize=7.9, color=INK)

rule(67.0, 0.55)

rowlabel(58.6, "the artifact")
ax.text(COL_L, 58.6, "a circuit, handed to you", ha="left", va="baseline",
        fontsize=7.9, color=INK)
ax.text(COL_R, 58.6, "no object is produced", ha="left", va="baseline",
        fontsize=7.9, color=GREY, style="italic")

rowlabel(45.6, "what can", "check it")
CHECKS = [("re-execution",         r"17.5 $\mu$s"),
          ("Z3, over every input", "2.6 s"),
          ("the Lean 4 kernel",    "5.8 s")]
y = 45.6
for name, cost in CHECKS:
    ax.text(COL_L, y, name, ha="left", va="baseline", fontsize=7.7, color=INK)
    ax.text(COL_L + COL_W, y, cost, ha="right", va="baseline", fontsize=7.0, color=MID)
    ax.plot([COL_R, COL_R + COL_W], [y + 2.0, y + 2.0], color=SOFT,
            lw=0.75, ls=(0, (1.1, 2.1)), solid_capstyle="butt", zorder=2)
    y -= 8.9

ax.text(COL_R + COL_W / 2, 20.4, "nothing to re-execute, nothing to check",
        ha="center", va="baseline", fontsize=6.9, color=GREY, style="italic")

rule(14.2, 0.55)

rowlabel(5.6, "what reaches", "the reader")
ax.text(COL_L, 5.6, "a machine-checked certificate", ha="left", va="baseline",
        fontsize=7.9, color=INK, fontweight="bold")
ax.text(COL_R, 5.6, "a solver’s word", ha="left", va="baseline",
        fontsize=7.9, color=GREY, fontweight="bold")

rule(-4.6, 1.15)
ax.set_ylim(-6.5, 100)

fig.savefig("paper/figs/asymmetry.pdf")
fig.savefig("paper/figs/asymmetry.png", dpi=200)
print("wrote asymmetry")
