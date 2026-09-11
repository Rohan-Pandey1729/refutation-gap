"""Shared figure style. Grayscale-safe: one hue + value ramp, shape/fill carry meaning."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Single-hue ramp (dark -> light). Prints legibly in grayscale.
INK      = "#12263a"   # darkest - primary ink
DEEP     = "#1f3f5f"   # certified / verified
MID      = "#4a6f8f"   # secondary
SOFT     = "#8fa8bd"   # tertiary
PALE     = "#d6e0e9"   # fills
FAINT    = "#eef2f6"   # backgrounds
GREY     = "#8a8a8a"   # uncertified / absent
LIGHTGREY= "#c9c9c9"

def setup():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["DejaVu Serif"],
        "mathtext.fontset": "dejavuserif",
        "font.size": 8.2,
        "axes.labelsize": 8.2,
        "axes.titlesize": 8.6,
        "xtick.labelsize": 7.6,
        "ytick.labelsize": 7.6,
        "legend.fontsize": 7.4,
        "axes.linewidth": 0.7,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "axes.edgecolor": INK,
        "text.color": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "axes.grid": False,
        "figure.dpi": 200,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "pdf.fonttype": 42,
    })

def despine(ax, keep=("left","bottom")):
    for s in ("top","right","left","bottom"):
        ax.spines[s].set_visible(s in keep)
