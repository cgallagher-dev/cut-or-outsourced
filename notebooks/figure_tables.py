from pathlib import Path

import pandas as pd

PROC = Path("data/processed")
OUT = PROC / "figures"
OUT.mkdir(exist_ok=True)

NAMES = {"IE": "Ireland", "UK": "United Kingdom", "DK": "Denmark", "DE": "Germany",
         "FR": "France", "SE": "Sweden", "NL": "Netherlands"}
YEAR = 2024

print("== Figure 1. Territorial and consumption CO2, index 1990 = 100 (OWID)")
owid = pd.read_csv(PROC / "owid_peers.csv")
f1 = owid[["country", "year"]].copy()
f1["territorial_mt"] = owid["co2"]
f1["consumption_mt"] = owid["consumption_co2"]
base = f1[f1["year"] == 1990].set_index("country")
f1["territorial_index"] = f1["territorial_mt"] / f1["country"].map(base["territorial_mt"]) * 100
f1["consumption_index"] = f1["consumption_mt"] / f1["country"].map(base["consumption_mt"]) * 100
# Panels run from the biggest 2023 gap between the two measures to the smallest
gap = f1[f1["year"] == 2023].set_index("country").eval("consumption_index - territorial_index")
f1["panel_order"] = f1["country"].map(gap.rank(ascending=False).astype(int))
print(gap.sort_values(ascending=False).round(1).to_string())
f1.round(3).to_csv(OUT / "fig1_owid_index.csv", index=False)

print("\n== Figure 2. Footprint balance, % of production (FIGARO)")
bal = pd.read_csv(PROC / "figaro_balance_peers.csv")
f2 = bal[["country", "year"]].copy()
f2["country_name"] = f2["country"].map(NAMES)
f2["balance_pct"] = bal["balance_pct_of_production"]
f2["balance_excl_transport_pct"] = bal["balance_excl_transport_pct"]
# Sorting by the 2010-2024 median, not one year, so Ireland's volatile years can't reorder rows
med = f2.groupby("country")["balance_pct"].median()
f2["median_balance_pct"] = f2["country"].map(med)
f2["sort_order"] = f2["country"].map(med.rank().astype(int))
f2 = f2[["country", "country_name", "year", "balance_pct", "balance_excl_transport_pct",
         "median_balance_pct", "sort_order"]]
print(med.sort_values().round(1).to_string())
f2.round(3).to_csv(OUT / "fig2_balance.csv", index=False)

print(f"\n== Figure 3. Ireland's production by industry, {YEAR}, where it is consumed (FIGARO)")
ind = pd.read_csv(PROC / "figaro_ie_industry_exports.csv")
ind = ind[ind["year"] == YEAR].set_index("nace_r2")
labels = {"A01": "Farming", "H51": "Airlines", "C": "Manufacturing", "H50": "Shipping"}
f3 = ind.loc[list(labels), ["produced_mt", "consumed_abroad_mt", "share_abroad_pct"]]
# The named industries plus the rest make up the total, so the bars form a real whole
other = ind.loc["TOTAL", ["produced_mt", "consumed_abroad_mt"]] - f3[["produced_mt", "consumed_abroad_mt"]].sum()
other["share_abroad_pct"] = other["consumed_abroad_mt"] / other["produced_mt"] * 100
f3.loc["OTHER"] = other
f3 = f3.rename_axis("industry_code").reset_index()
f3["industry_label"] = f3["industry_code"].map({**labels, "OTHER": "All other industries"})
f3["consumed_in_ireland_mt"] = f3["produced_mt"] - f3["consumed_abroad_mt"]
f3 = f3[["industry_code", "industry_label", "produced_mt", "consumed_in_ireland_mt",
         "consumed_abroad_mt", "share_abroad_pct"]]
assert abs(f3["produced_mt"].sum() - ind.loc["TOTAL", "produced_mt"]) < 0.001
print(f3.round(1).to_string(index=False))
f3.round(3).to_csv(OUT / "fig3_ie_industries.csv", index=False)

print(f"\n== Figure 4. From the inventory to FIGARO production, Ireland {YEAR} (bridging table)")
r = pd.read_csv(PROC / "ie_reconciliation.csv").set_index("time").loc[YEAR]
f4 = pd.DataFrame([
    # The bridging table's own inventory figure, slightly below the env_air_gge total
    ("Inventory (territory principle)", r["inventory_territory"], "total"),
    ("Fuel Irish residents bought abroad", r["plus_residents_fuel_abroad"], "add"),
    ("Fuel non-residents bought in Ireland", abs(r["minus_nonresidents_in_ie"]), "subtract"),
    ("All Irish residents", r["aea_residents_total"], "total"),
    ("Households' own emissions", abs(r["minus_households"]), "subtract"),
    ("FIGARO production (industries)", r["figaro_production"], "total"),
], columns=["label", "value_mt", "kind"])
f4.insert(0, "step", range(1, len(f4) + 1))
f4["of_which_air_mt"] = [None, r["of_which_air"], None, None, None, None]
running = []
for value, kind in zip(f4["value_mt"], f4["kind"]):
    if kind == "total":
        # Each total must follow from the steps before it, or the bridge doesn't add up
        assert not running or abs(running[-1] - value) < 0.05, (running[-1], value)
        running.append(value)
    else:
        running.append(running[-1] + (value if kind == "add" else -value))
f4["running_total_mt"] = running
print(f4.round(2).to_string(index=False))
f4.round(3).to_csv(OUT / "fig4_ie_bridge.csv", index=False)

print("\n== Figure 5. Consumption footprint per person by final use, 2023 (FIGARO, OWID population)")
pp = pd.read_csv(PROC / "figaro_footprint_per_person.csv")
# OWID population stops at 2023, so that is the latest year with a per-person value
f5 = pp[pp["year"] == pp["year"].max()].copy()
f5["country_name"] = f5["country"].map(NAMES)
f5 = f5.rename(columns={"households_gov_t_per_person": "households_gov_t",
                        "investment_t_per_person": "investment_t",
                        "inventories_t_per_person": "inventories_t",
                        "total_t_per_person": "total_t"})
# Inventories are small and can be negative, so the parts are checked against the total
assert (f5[["households_gov_t", "investment_t", "inventories_t"]].sum(axis=1)
        - f5["total_t"]).abs().max() < 0.01
f5["sort_order"] = f5["total_t"].rank(ascending=False).astype(int)
f5 = f5[["country", "country_name", "year", "households_gov_t", "investment_t",
         "inventories_t", "total_t", "sort_order"]].sort_values("sort_order")
print(f5.round(2).to_string(index=False))
f5.round(3).to_csv(OUT / "fig5_per_person.csv", index=False)

print("\nSaved:", sorted(p.name for p in OUT.glob("*.csv")))
