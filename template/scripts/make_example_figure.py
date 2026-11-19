from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figure_style import apply, save, RED, BLUE, PALE, INK, COLUMN_IN
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
apply()
fig, ax = plt.subplots(figsize=(COLUMN_IN, 1.55))
fig.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
ax.set(xlim=(0, 10), ylim=(0, 4))
ax.axis('off')
for x, title, subtitle, colour in [(0.3, 'Record', 'Keep the\nobservation', INK), (3.7, 'Score', 'Apply the rule', RED), (7.1, 'Report', 'Expose\nuncertainty', BLUE)]:
    ax.add_patch(FancyBboxPatch((x, 1.4), 2.6, 1.75, boxstyle='round,pad=0.06,rounding_size=0.08', facecolor=PALE, edgecolor=colour, linewidth=0.65))
    ax.text(x+1.3, 2.55, title, ha='center', va='center', fontsize=9, color=colour, fontweight='bold')
    ax.text(x+1.3, 1.95, subtitle, ha='center', va='center', fontsize=7, color=INK)
for x in [3.0, 6.4]:
    ax.annotate('', xy=(x+0.6, 2.25), xytext=(x, 2.25), arrowprops={'arrowstyle':'->', 'color':INK, 'lw':0.7})
ax.text(5, 0.5, 'One record of evidence, from input to claim', ha='center', fontsize=8, color=INK)
save(fig, Path(__file__).resolve().parents[1] / 'figure-example.pdf')
