#!/usr/bin/env python3
"""Figures for the VeriCodeGen paper. Print- and grayscale-legible by construction:
single-hue sequential shading (maps to lightness), one series per panel, no dual axes,
recessive grid, direct annotation instead of dense labels."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parent.parent
rows = [json.loads(l) for l in (REPO / "runs" / "certified_decisive.jsonl").read_text().splitlines() if l.strip()]
ref = [r for r in rows if r.get("decisive")]
cl = np.array([r["decisive"]["n_clauses"] for r in ref], float)
pb = np.array([r["decisive"]["proof_bytes"] for r in ref], float) / 1e6
ss = np.array([r["decisive"]["solve_seconds"] for r in ref], float)
cs = np.array([r["decisive"]["check_seconds"] for r in ref], float)
nn = np.array([r["n"] for r in ref], float)

plt.rcParams.update({
    "font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8.5,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "grid.linewidth": 0.4, "grid.alpha": 0.35,
    "figure.dpi": 200, "savefig.bbox": "tight",
})
INK = "#1a1a1a"
fig, (a, b) = plt.subplots(1, 2, figsize=(6.6, 2.5))

# --- Panel A: proof size vs formula size. One series -> no legend, title names it.
a.scatter(cl, pb, s=14, c="#2b6cb0", alpha=0.75, linewidths=0.5, edgecolors="white", zorder=3)
a.set_xscale("log"); a.set_yscale("log")
a.set_xlabel("CNF size (clauses)"); a.set_ylabel("DRAT proof size (MB)")
a.set_title("(a) Refutation certificates stay small", loc="left", color=INK)
a.grid(True, which="major", zorder=0)
a.annotate(f"median {np.median(pb):.2f} MB\nmax {pb.max():.1f} MB",
           xy=(0.04, 0.93), xycoords="axes fraction", va="top", fontsize=7, color="#444")

# --- Panel B: check vs solve. Shade by n with a single-hue sequential ramp so the
# encoding survives grayscale; y=x separates "checking costs more" from "less".
lo = min(ss.min(), cs.min()) * 0.5
hi = max(ss.max(), cs.max()) * 2
b.plot([lo, hi], [lo, hi], ls="--", lw=0.9, color="#999", zorder=2)
sc = b.scatter(ss, cs, s=16, c=nn, cmap="Blues", vmin=nn.min() - 1.2, vmax=nn.max(),
               alpha=0.9, linewidths=0.5, edgecolors="#2b6cb0", zorder=3)
b.set_xscale("log"); b.set_yscale("log"); b.set_xlim(lo, hi); b.set_ylim(lo, hi)
b.set_xlabel("solve time with proof logging (s)"); b.set_ylabel("independent check time (s)")
b.set_title("(b) Checking costs a small multiple of solving", loc="left", color=INK)
b.grid(True, which="major", zorder=0)
b.text(0.96, 0.06, "$y=x$", transform=b.transAxes, ha="right", fontsize=7, color="#777")
ratio = cs / np.maximum(ss, 1e-9)
b.annotate(f"median check/solve\n= {np.median(ratio):.1f}$\\times$",
           xy=(0.04, 0.93), xycoords="axes fraction", va="top", fontsize=7, color="#444")
cb = fig.colorbar(sc, ax=b, pad=0.02, fraction=0.045)
cb.set_label("inputs $n$", fontsize=7); cb.ax.tick_params(labelsize=6)
cb.set_ticks(sorted(set(nn.tolist())))

out = REPO / "paper" / "figs" / "certification.pdf"
fig.savefig(out); fig.savefig(out.with_suffix(".png"))
print(f"wrote {out}  ({len(ref)} refutations)")
print(f"  proof MB   median {np.median(pb):.3f}  max {pb.max():.2f}")
print(f"  solve s    median {np.median(ss):.3f}  max {ss.max():.2f}")
print(f"  check s    median {np.median(cs):.3f}  max {cs.max():.2f}")
print(f"  check/solve median {np.median(ratio):.2f}  max {ratio.max():.1f}")
