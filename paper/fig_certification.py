"""Figure 4: what proof-carrying refutation costs, from runs/certified_decisive.jsonl."""
import sys, json, collections, statistics as st
sys.path.insert(0, __file__.rsplit("/",1)[0])
from figstyle import *
import matplotlib.pyplot as plt
import numpy as np

setup()
ROWS = [json.loads(l) for l in open("runs/certification_final.jsonl")]

def status(r):
    if r["route"] == "counting bound":
        return "free"
    return "verified" if r["verdict"] == "VERIFIED" else "resisted"

V = [r for r in ROWS if status(r) == "verified"]
pb = np.array([r["proof_bytes"] for r in V]) / 1e6
nc = np.array([r["n_clauses"]   for r in V])
ss = np.array([r["solve_seconds"] for r in V])
cs = np.array([r["check_seconds"] for r in V])
nn = np.array([r["n"] for r in V])

fig = plt.figure(figsize=(6.9, 2.16))
gs  = fig.add_gridspec(1, 3, width_ratios=[1.06, 1.0, 1.0], wspace=0.40)
axA, axB, axC = (fig.add_subplot(gs[0, i]) for i in range(3))

# ---- (a) coverage by n --------------------------------------------------
ct = collections.defaultdict(collections.Counter)
for r in ROWS:
    ct[r["n"]][status(r)] += 1
ns = sorted(ct)
cats = [("verified", "checked refutation", DEEP, None),
        ("free",     "counting bound",     SOFT, None)]
left = np.zeros(len(ns))
ypos = np.arange(len(ns))[::-1]
for key, lab, col, hatch in cats:
    vals = np.array([ct[n][key] for n in ns], float)
    axA.barh(ypos, vals, left=left, height=0.62, color=col, edgecolor=INK,
             linewidth=0.7, label=lab, hatch=hatch, zorder=3)
    for y, v, l in zip(ypos, vals, left):
        if v >= 4:
            axA.text(l + v/2, y, f"{int(v)}", ha="center", va="center",
                     fontsize=6.8, zorder=4,
                     color="white" if col == DEEP else INK,
                     fontweight="bold")
    left += vals
for y, n in zip(ypos, ns):
    tot = sum(ct[n].values())
    axA.text(left[list(ypos).index(y)] + 1.8, y, f"{tot}/{tot}",
             ha="left", va="center", fontsize=6.6, color=MID)
axA.set_yticks(ypos); axA.set_yticklabels([f"$n\\!=\\!{n}$" for n in ns])
axA.set_xlim(0, 62); axA.set_xlabel("optimality results")
axA.set_title("(a)  every result certified", loc="left", fontweight="bold")
axA.legend(loc="lower right", bbox_to_anchor=(1.02, 0.10), frameon=False, handlelength=1.1,
           handletextpad=0.45, borderpad=0.1, labelspacing=0.28, fontsize=6.2)
despine(axA, keep=("bottom",)); axA.tick_params(axis="y", length=0)

# ---- (b) proof size vs formula size ------------------------------------
for n, mk in zip([6, 7, 8, 9], ["o", "s", "^", "D"]):
    m = nn == n
    if m.any():
        axB.scatter(nc[m], pb[m], s=13, marker=mk, facecolor="none",
                    edgecolor=INK, linewidth=0.75, zorder=3, label=f"$n\\!=\\!{n}$")
axB.set_xscale("log"); axB.set_yscale("log")
axB.set_xlabel("clauses in formula"); axB.set_ylabel("DRAT proof (MB)")
axB.set_title("(b)  proof size", loc="left", fontweight="bold")
axB.axhline(np.median(pb), color=MID, lw=0.9, ls=(0, (4, 2)), zorder=2)
axB.text(0.96, 0.05, f"median {np.median(pb):.2f} MB",
         transform=axB.transAxes, fontsize=6.4, color=INK, ha="right",
         va="bottom", bbox=dict(boxstyle="round,pad=0.26", fc="white",
                                ec=SOFT, lw=0.7))
axB.legend(loc="upper left", frameon=False, handlelength=0.9,
           handletextpad=0.35, borderpad=0.1, labelspacing=0.2, fontsize=6.2)
despine(axB)

# ---- (c) check vs solve -------------------------------------------------
lo = min(ss.min(), cs.min())*0.55; hi = max(ss.max(), cs.max())*1.9
axC.plot([lo, hi], [lo, hi], color=MID, lw=0.9, ls=(0, (4, 2)), zorder=2)
axC.scatter(ss, cs, s=13, marker="o", facecolor="none", edgecolor=INK,
            linewidth=0.75, zorder=3)
axC.set_xscale("log"); axC.set_yscale("log")
axC.set_xlim(lo, hi); axC.set_ylim(lo, hi)
axC.set_xlabel("solve time (s)"); axC.set_ylabel("independent check (s)")
axC.set_title("(c)  checking cost", loc="left", fontweight="bold")
axC.text(0.95, 0.06, f"median {st.median(cs/ss):.1f}$\\times$ solving",
         transform=axC.transAxes, ha="right", va="bottom", fontsize=6.6,
         color=INK, bbox=dict(boxstyle="round,pad=0.28", fc="white", ec=SOFT, lw=0.7))
axC.text(0.055, 0.93, "$y=x$", transform=axC.transAxes, fontsize=6.3,
         color=MID, ha="left", va="top")
despine(axC)

fig.savefig("paper/figs/certification.pdf")
fig.savefig("paper/figs/certification.png", dpi=190)
print("wrote certification;  verified=%d  medianMB=%.2f  ratio=%.2f"
      % (len(V), np.median(pb), st.median(cs/ss)))
