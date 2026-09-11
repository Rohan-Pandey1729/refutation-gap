"""Figure: AES MixColumns published counts. Record status is set explicitly from
SOURCES.md section 2 (chronological by first public posting), NOT computed by
year, because 2017 and 2019 each contain two entries and 94 (Tan-Peyrin, ePrint
2019/847, 22 Jul 2019) appeared after 92 (Maximov, ePrint 2019/833, 19 Jul 2019).
"""
import sys; sys.path.insert(0, __file__.rsplit("/",1)[0])
from figstyle import *
import matplotlib.pyplot as plt
import numpy as np

setup()

# x, gates, was-a-record-when-published, dx_pt, dy_pt, ha
PUB = [
    (2001.00, 108, True,   4,   6, "left"),
    (2017.00, 103, True,  -3,   6, "right"),
    (2017.55,  97, True,   3,  -7, "left"),
    (2019.00,  95, True,  -3,   6, "right"),
    (2019.45,  92, True,   3,  -7, "left"),
    (2020.10,  94, False,  4,   6, "left"),
    (2021.00,  91, True,   3,  -7, "left"),
    (2025.00,  89, True,  -2,   7, "right"),
    (2026.00,  88, True,   4,  -5, "left"),
]
TRIVIAL_LB = 32   # computed: slp.optimal.trivial_lower_bound(aes_mixcolumns())

fig, ax = plt.subplots(figsize=(6.9, 2.72))

rec = [(x, g) for x, g, r, *_ in PUB if r]
sx = np.array([p[0] for p in rec] + [2027.0])
sy = np.array([p[1] for p in rec] + [rec[-1][1]])

ax.fill_between(sx, TRIVIAL_LB, sy, step="post", facecolor="white",
                edgecolor=SOFT, hatch="////", linewidth=0.0, zorder=1, alpha=0.8)
ax.step(sx, sy, where="post", color=INK, lw=1.6, zorder=4)
ax.axhline(TRIVIAL_LB, color=INK, lw=1.0, ls=(0, (4, 2)), zorder=3)

for x, g, is_rec, dx, dy, ha in PUB:
    ax.plot(x, g, marker="o", ms=4.8, zorder=6,
            mfc=INK if is_rec else "white", mec=INK, mew=1.05)
    ax.annotate(f"{g}", (x, g), xytext=(dx, dy), textcoords="offset points",
                fontsize=7.5, color=INK, ha=ha,
                va="bottom" if dy > 0 else "top", fontweight="bold", zorder=7)

ax.annotate("no lower bound published for this matrix:\n"
            "nothing excludes any circuit in here",
            xy=(2009.0, 66), fontsize=7.8, color=MID, ha="center", va="center",
            zorder=6, linespacing=1.4)
ax.annotate("free counting bound, 32", xy=(2001.3, 34.0), fontsize=6.9,
            color=INK, ha="left", va="bottom", zorder=6)

ax.text(0.985, 0.045,
        "9 published upper bounds   ·   0 carry a refutation certificate",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=7.8,
        color=INK, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.38", fc="white", ec=INK, lw=0.9))

ax.set_xlim(2000.0, 2027.2)
ax.set_ylim(17, 116)
ax.set_xticks([2001, 2005, 2009, 2013, 2017, 2021, 2025])
ax.set_yticks([32, 50, 70, 90, 110])
ax.set_ylabel("XOR gates")
despine(ax)
fig.savefig("paper/figs/records.pdf")
fig.savefig("paper/figs/records.png", dpi=190)
print("wrote records; records=%d non-records=%d" %
      (sum(1 for *_, r, a, b, c in [(p[0],p[1],p[2],p[3],p[4],p[5]) for p in PUB] if r),
       sum(1 for p in PUB if not p[2])))
