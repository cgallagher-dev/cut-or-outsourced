from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.text import Text
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

DATA = Path("data/processed/figures")
OUT = Path("figures")
OUT.mkdir(exist_ok=True)

# Slide size. The A4 report version is made by changing these values, not by copying code
FIG_SIZE = (13.33, 7.5)
DPI = 200
TITLE_PT = 20
SUBTITLE_PT = 15
TEXT_PT = 14
SOURCE_PT = 11

# Draft titles. Lucy decides the final wording with Seán
TITLES = {
    "fig1": "Five of Ireland's six peers cut territorial CO₂ faster than the CO₂ they consume",
    "fig2": "Without shipping and airlines, all seven countries are net importers of emissions",
    "fig3": "Most emissions from Irish farming and airlines are consumed abroad",
    "fig4": "The inventory and FIGARO totals differ for known reasons",
    "fig5": "Ireland has the highest footprint per person, but its lead is mostly investment",
}

BLUE = "#2a78d6"
ORANGE = "#eb6834"
PEER = "#b5b3ad"
TOTAL = "#52514e"
TEXT = "#0b0b0b"
AXIS = "#52514e"
GRID = "#e1e0d9"

FIGARO_SOURCE = ("Source: Eurostat, greenhouse gas footprints, FIGARO (env_ac_ghgfp), release of "
                 "30 October 2026. All greenhouse gases.")

plt.rcParams.update({
    # DejaVu Sans ships with matplotlib, so the figures look the same on every machine
    "font.family": "DejaVu Sans",
    "font.size": TEXT_PT,
    "text.color": TEXT,
    "axes.labelcolor": AXIS,
    "axes.edgecolor": AXIS,
    "xtick.color": AXIS,
    "ytick.color": AXIS,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "lines.linewidth": 2,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "svg.fonttype": "none",
    # Fixed IDs, so rebuilding unchanged figures gives identical SVGs
    "svg.hashsalt": "cut-or-outsourced",
})


def frame(key, subtitle, source):
    fig = plt.figure(figsize=FIG_SIZE, dpi=DPI)
    fig.text(0.02, 0.965, TITLES[key], fontsize=TITLE_PT, fontweight="bold", va="top")
    fig.text(0.02, 0.905, subtitle, fontsize=SUBTITLE_PT, color=AXIS, va="top")
    fig.text(0.02, 0.02, source, fontsize=SOURCE_PT, color=AXIS)
    return fig


def save(fig, name):
    # Stop if any text runs off the edge, e.g. after a longer title is typed in
    fig.canvas.draw()
    edge = fig.bbox
    for t in fig.findobj(Text):
        if t.get_visible() and t.get_text().strip():
            box = t.get_window_extent()
            assert (box.x0 >= edge.x0 - 1 and box.x1 <= edge.x1 + 1
                    and box.y0 >= edge.y0 - 1 and box.y1 <= edge.y1 + 1), \
                f"{name}: text runs off the edge: {t.get_text()[:50]!r}"
    for ext in ("png", "svg"):
        # No timestamp in the SVG, for the same reason
        fig.savefig(OUT / f"{name}.{ext}", dpi=DPI,
                    metadata={"Date": None} if ext == "svg" else None)
    plt.close(fig)
    print("Saved", name)


# Figure 1. Long-term cuts, small multiples
f1 = pd.read_csv(DATA / "fig1_owid_index.csv")
fig = frame("fig1", "Territorial and consumption-based CO₂, index 1990 = 100, 1990–2023",
            "Source: Our World in Data CO₂ dataset (Global Carbon Budget), 1990–2023.")
grid = fig.add_gridspec(2, 4, left=0.06, right=0.98, top=0.82, bottom=0.11, hspace=0.38,
                        wspace=0.12)
order = f1.drop_duplicates("country").sort_values("panel_order")["country"].tolist()
first = None
for i, country in enumerate(order):
    ax = fig.add_subplot(grid[i // 4, i % 4], sharey=first)
    first = first or ax
    d = f1[f1["country"] == country]
    ax.fill_between(d["year"], d["territorial_index"], d["consumption_index"], color=GRID,
                    linewidth=0)
    ax.axhline(100, color=AXIS, linewidth=0.8)
    ax.plot(d["year"], d["territorial_index"], color=BLUE)
    ax.plot(d["year"], d["consumption_index"], color=ORANGE, linestyle="--")
    ax.set_title(country, fontsize=TEXT_PT, loc="left",
                 fontweight="bold" if country == "Ireland" else "normal",
                 color=BLUE if country == "Ireland" else TEXT)
    # Ticks kept inside the range, so neighbouring panels' labels don't meet at the edges
    ax.set_xticks([1995, 2005, 2015])
    ax.set_xlim(1990, 2023)
    if country == "Netherlands":
        # The 1999-2003 dip is all in OWID's modelled trade term, so say so before anyone asks
        ax.text(1992, 190, "Dip is in OWID's\ntrade estimate,\ncause not checked", va="top",
                fontsize=TEXT_PT, color=AXIS)
    if i % 4:
        ax.tick_params(labelleft=False)
    else:
        ax.set_ylabel("Index, 1990 = 100")
    if i == 0:
        # Label the two lines once, in the first panel, in empty space above and below them
        ax.text(2012, 126, "Consumption", ha="center", va="bottom", color=ORANGE,
                fontsize=TEXT_PT)
        ax.text(1997, 80, "Territorial", ha="center", va="top", color=BLUE, fontsize=TEXT_PT)
key = fig.add_subplot(grid[1, 3])
key.axis("off")
key.legend(handles=[Line2D([], [], color=BLUE, label="Territorial CO₂"),
                    Line2D([], [], color=ORANGE, linestyle="--", label="Consumption CO₂"),
                    Patch(color=GRID, label="Gap between them")],
           loc="upper left", frameon=False, fontsize=TEXT_PT)
key.text(0.03, 0.4, "CO₂ only: excludes\nmethane and nitrous\noxide, so most of\n"
         "Ireland's farming\nis missing. Panels\nordered by 2023 gap.",
         transform=key.transAxes, va="top", fontsize=TEXT_PT, color=AXIS)
save(fig, "fig1_long_term_cuts")


# Figure 2. Footprint balance, 2024 snapshot and 2010-2024 lines
f2 = pd.read_csv(DATA / "fig2_balance.csv")
fig = frame("fig2", "Consumption minus production, % of production",
            FIGARO_SOURCE + " Shipping is NACE H50, airlines H51.")
ax_a = fig.add_axes([0.14, 0.13, 0.33, 0.61])
ax_b = fig.add_axes([0.55, 0.13, 0.32, 0.61])

snap = f2[f2["year"] == 2024].sort_values("sort_order")
rows = range(len(snap))
for y, (_, r) in zip(rows, snap.iterrows()):
    colour = BLUE if r["country"] == "IE" else TOTAL
    ax_a.plot([r["balance_pct"], r["balance_excl_transport_pct"]], [y, y], color=PEER,
              linewidth=1.5, zorder=1)
    ax_a.scatter(r["balance_pct"], y, s=110, color=colour, zorder=2)
    ax_a.scatter(r["balance_excl_transport_pct"], y, s=110, facecolor="white", edgecolor=colour,
                 linewidth=2, zorder=2)
ax_a.axvline(0, color=AXIS, linewidth=0.8)
ax_a.set_yticks(list(rows), snap["country_name"])
for label, code in zip(ax_a.get_yticklabels(), snap["country"]):
    if code == "IE":
        label.set_color(BLUE)
        label.set_fontweight("bold")
ax_a.invert_yaxis()
ax_a.grid(False)
ax_a.grid(axis="x")
ax_a.set_xlabel("% of production (consumption minus production)")
ax_a.set_title("A. 2024", loc="left", fontsize=TEXT_PT, fontweight="bold", pad=30)
fig.legend(handles=[Line2D([], [], marker="o", color=TOTAL, linestyle="", markersize=10,
                            label="All industries"),
                     Line2D([], [], marker="o", color=TOTAL, markerfacecolor="white",
                            markeredgewidth=2, linestyle="", markersize=10,
                            label="Without shipping and airlines")],
           loc="upper left", bbox_to_anchor=(0.015, 0.875), ncol=2, frameon=False,
           fontsize=TEXT_PT)
ax_a.text(0, 1.01, "← Net exporter  ", transform=ax_a.get_xaxis_transform(),
          ha="right", va="bottom", fontsize=TEXT_PT, color=AXIS)
ax_a.text(0, 1.01, "  Net importer →", transform=ax_a.get_xaxis_transform(),
          ha="left", va="bottom", fontsize=TEXT_PT, color=AXIS)

# The Denmark share is not in fig2_balance.csv, so it is read from the processed balance file
dk = pd.read_csv("data/processed/figaro_balance_peers.csv").query("country == 'DK' and year == 2024")
dk_share = (1 - dk["production_excl_transport_mt"] / dk["production_mt"]).iloc[0] * 100
dk_row = snap.reset_index(drop=True).query("country == 'DK'").index[0]
ax_a.text(snap.iloc[dk_row]["balance_pct"], dk_row + 0.2,
          f"Shipping and airlines are\n{dk_share:.0f}% of Denmark's production",
          fontsize=TEXT_PT, color=AXIS, va="top")

ax_b.axvspan(2018.5, 2020.5, color=GRID, linewidth=0)
# Placed below zero, where no line passes in 2019-2020
ax_b.text(2019.5, -15, "Ireland: investment\nin intellectual\nproperty", ha="center",
          va="center", fontsize=TEXT_PT, color=AXIS)
ax_b.axhline(0, color=AXIS, linewidth=0.8)
ends = []
for code, d in f2.groupby("country"):
    is_ie = code == "IE"
    ax_b.plot(d["year"], d["balance_pct"], color=BLUE if is_ie else PEER,
              linewidth=2.5 if is_ie else 1.2, zorder=3 if is_ie else 2)
    ends.append([d["balance_pct"].iloc[-1], d["country_name"].iloc[0], is_ie])
# Nudge end labels apart so close values (Ireland and the Netherlands) don't overlap
ends.sort()
gap = 9
for i in range(1, len(ends)):
    ends[i][0] = max(ends[i][0], ends[i - 1][0] + gap)
for y, name, is_ie in ends:
    ax_b.text(2024.4, y, name, va="center", fontsize=TEXT_PT,
              color=BLUE if is_ie else AXIS, fontweight="bold" if is_ie else "normal")
ax_b.set_xlim(2010, 2024)
ax_b.set_xticks([2010, 2014, 2018, 2022])
ax_b.set_ylabel("% of production")
ax_b.set_title("B. All industries, 2010–2024", loc="left", fontsize=TEXT_PT,
               fontweight="bold", pad=30)
save(fig, "fig2_footprint_balance")


# Figure 3. Irish industries, where their emissions are consumed
f3 = pd.read_csv(DATA / "fig3_ie_industries.csv")
f4 = pd.read_csv(DATA / "fig4_ie_bridge.csv")
figaro_total = f4.loc[f4["step"] == 6, "value_mt"].iloc[0]
# The five bars should make up Ireland's whole FIGARO production
assert abs(f3["produced_mt"].sum() - figaro_total) < 0.05, (f3["produced_mt"].sum(), figaro_total)
fig = frame("fig3", "Emissions produced by Irish industries in 2024, by where they were consumed, "
            "Mt CO₂e", FIGARO_SOURCE)
ax = fig.add_axes([0.2, 0.17, 0.7, 0.6])
ys = range(len(f3))
ax.barh(ys, f3["consumed_in_ireland_mt"], color=BLUE, edgecolor="white", linewidth=2,
        height=0.62)
ax.barh(ys, f3["consumed_abroad_mt"], left=f3["consumed_in_ireland_mt"], color=ORANGE,
        edgecolor="white", linewidth=2, height=0.62)
for y, r in zip(ys, f3.itertuples()):
    ax.text(r.produced_mt + 0.3, y, f"{r.produced_mt:.1f} Mt, {r.share_abroad_pct:.1f}% abroad",
            va="center",
            fontsize=TEXT_PT, color=TEXT)
ax.set_yticks(list(ys), f3["industry_label"])
ax.invert_yaxis()
ax.grid(False)
ax.grid(axis="x")
ax.set_xlabel("Mt CO₂e")
ax.set_xlim(0, f3["produced_mt"].max() * 1.35)
ax.legend(handles=[Patch(color=BLUE, label="Consumed in Ireland"),
                   Patch(color=ORANGE, label="Consumed abroad")],
          loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, frameon=False, fontsize=TEXT_PT)
fig.text(0.98, 0.065, f"The five bars add up to Ireland's total of {figaro_total:.1f} Mt.",
         ha="right", fontsize=TEXT_PT, color=AXIS)
save(fig, "fig3_irish_industries")


# Figure 4. Waterfall from the inventory to FIGARO production
fig = frame("fig4", "Ireland, 2024, Mt CO₂e, all greenhouse gases excluding land use",
            "Source: Eurostat env_ac_aibrid_r2 and env_ac_ainah_r2, Ireland, all greenhouse gases "
            "excluding land use.")
ax = fig.add_axes([0.08, 0.2, 0.9, 0.62])
colours = {"total": TOTAL, "add": ORANGE, "subtract": BLUE}
level = 0
for i, r in enumerate(f4.itertuples()):
    if r.kind == "total":
        # Each total must equal the steps before it, or the bridge doesn't add up
        assert i == 0 or abs(level - r.value_mt) < 0.05, (level, r.value_mt)
        bottom, height, level = 0, r.value_mt, r.value_mt
        label = f"{r.value_mt:.2f}"
    elif r.kind == "add":
        bottom, height = level, r.value_mt
        level += r.value_mt
        label = f"+{r.value_mt:.2f}"
    else:
        level -= r.value_mt
        bottom, height = level, r.value_mt
        label = f"−{r.value_mt:.2f}"
    ax.bar(i, height, bottom=bottom, color=colours[r.kind], width=0.62)
    ax.text(i, bottom + height + 1, label, ha="center", va="bottom", fontsize=TEXT_PT,
            fontweight="bold" if r.kind == "total" else "normal")
    if i < len(f4) - 1:
        ax.plot([i + 0.31, i + 0.69], [level, level], color=AXIS, linewidth=0.8)
air = f4.loc[f4["step"] == 2, "of_which_air_mt"].iloc[0]
ax.annotate(f"of which\nIrish-resident\nairlines {air:.2f}", (1, f4.loc[0, "value_mt"]),
            xytext=(1, f4.loc[0, "value_mt"] - 12), ha="center", va="top", fontsize=TEXT_PT,
            color=TEXT, arrowprops={"arrowstyle": "-", "color": AXIS, "linewidth": 0.8})
ax.set_xticks(range(len(f4)),
              [l.replace(" (", "\n(").replace(" bought", "\nbought").replace("Households' own",
               "Households'\nown") for l in f4["label"]], fontsize=TEXT_PT)
ax.set_ylabel("Mt CO₂e")
ax.set_ylim(0, f4["running_total_mt"].max() * 1.25)
ax.legend(handles=[Patch(color=TOTAL, label="Total"), Patch(color=ORANGE, label="Added"),
                   Patch(color=BLUE, label="Taken away")],
          loc="upper left", frameon=False, fontsize=TEXT_PT, ncol=3)
save(fig, "fig4_why_numbers_differ")

# Figure 5. Consumption footprint per person by final use, 2023
f5 = pd.read_csv(DATA / "fig5_per_person.csv").sort_values("sort_order")
# Inventories are small and can be negative, so they stay in the total but aren't drawn
assert (f5[["households_gov_t", "investment_t", "inventories_t"]].sum(axis=1)
        - f5["total_t"]).abs().max() < 0.01
FIG5_NOTE = (f"Totals include changes in inventories ({f5['inventories_t'].min():+.1f} to "
             f"{f5['inventories_t'].max():+.1f} t), not drawn. FIGARO leaves out households' own "
             "heating and cars for every country.")


def fig5_bars(ax, fontsize):
    ys = range(len(f5))
    ax.barh(ys, f5["households_gov_t"], color=BLUE, edgecolor="white", linewidth=2, height=0.62)
    ax.barh(ys, f5["investment_t"], left=f5["households_gov_t"], color=ORANGE,
            edgecolor="white", linewidth=2, height=0.62)
    for y, r in zip(ys, f5.itertuples()):
        ax.text(r.households_gov_t + r.investment_t + 0.15, y, f"{r.total_t:.1f} t", va="center",
                fontsize=fontsize, fontweight="bold" if r.country == "IE" else "normal")
    ax.set_yticks(list(ys), f5["country_name"], fontsize=fontsize)
    for label, code in zip(ax.get_yticklabels(), f5["country"]):
        if code == "IE":
            label.set_color(BLUE)
            label.set_fontweight("bold")
    ax.invert_yaxis()
    ax.grid(False)
    ax.grid(axis="x")
    ax.tick_params(axis="x", labelsize=fontsize)
    ax.set_xlim(0, f5["total_t"].max() * 1.15)
    ax.set_xticks([0, 4, 8, 12])
    return [Patch(color=BLUE, label="Households and government"),
            Patch(color=ORANGE, label="Investment")]


# Report and full-slide version, same frame as the other figures
fig = frame("fig5", "Consumption footprint per person by final use, 2023, t CO₂e",
            FIGARO_SOURCE + " Population: Our World in Data.")
ax = fig.add_axes([0.16, 0.2, 0.74, 0.58])
handles = fig5_bars(ax, TEXT_PT)
ax.set_xlabel("t CO₂e per person")
ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, frameon=False,
          fontsize=TEXT_PT)
fig.text(0.02, 0.065, FIG5_NOTE, fontsize=SOURCE_PT, color=AXIS)
save(fig, "fig5_per_person")

# Panel version for the limitations slide, sized to sit in two card slots
PANEL_SIZE, PANEL_PT = (7.96, 2.6), 10
fig = plt.figure(figsize=PANEL_SIZE, dpi=DPI)
fig.text(0.01, 0.97, "Per person, 2023: Ireland is highest, but 5.4 of its 12.7 t is investment",
         fontsize=PANEL_PT + 2, fontweight="bold", va="top")
ax = fig.add_axes([0.17, 0.2, 0.8, 0.62])
handles = fig5_bars(ax, PANEL_PT)
ax.legend(handles=handles, loc="lower right", bbox_to_anchor=(1.0, 0.02), frameon=False,
          fontsize=PANEL_PT - 1)
fig.text(0.01, 0.02, "t CO₂e per person. Source: Eurostat FIGARO (30 Oct 2026 release), "
         "OWID population. Inventories in totals, not drawn.", fontsize=PANEL_PT - 2, color=AXIS)
save(fig, "fig5_per_person_panel")
