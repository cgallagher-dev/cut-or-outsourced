import json
from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
OUT = Path("data/processed")
OUT.mkdir(exist_ok=True)

PEERS_OWID = ["Ireland", "United Kingdom", "Denmark", "Germany", "France", "Sweden", "Netherlands"]
PEERS = ["IE", "UK", "DK", "DE", "FR", "SE", "NL"]
AGGREGATES = {"EU27_2020", "EXT_EU27_2020", "WORLD"}


def jsonstat_frame(path, keep):
    """Flatten a Eurostat JSON-stat file, keeping only rows where each dim is in keep[dim]."""
    d = json.load(open(path))
    dims, sizes = d["id"], d["size"]
    idx = {k: d["dimension"][k]["category"]["index"] for k in dims}
    rev = {k: {v: c for c, v in idx[k].items()} for k in dims}
    strides, step = {}, 1
    for k, s in zip(reversed(dims), reversed(sizes)):
        strides[k] = step
        step *= s
    status = d.get("status", {})
    rows = []
    for key, value in d["value"].items():
        k = int(key)
        rec = {dim: rev[dim][(k // strides[dim]) % size] for dim, size in zip(dims, sizes)}
        if all(rec[dim] in allowed for dim, allowed in keep.items()):
            rec["value"] = value
            rec["flag"] = status.get(key, "")
            rows.append(rec)
    return pd.DataFrame(rows)


def report(name, df, keys):
    print(f"\n-- {name}: {len(df)} rows, {df.shape[1]} columns")
    print("Missing values per column:")
    print(df.isna().sum()[lambda s: s > 0].to_string() or "  none")
    print("Duplicate rows on", keys, ":", df.duplicated(keys).sum())


print("== 1. Our World in Data")
owid = pd.read_csv(RAW / "owid-co2-data.csv")
print("Raw:", owid.shape, "| years", owid["year"].min(), "-", owid["year"].max(),
      "| entities", owid["country"].nunique())
print("Entities without an ISO code (regions/aggregates):", owid["iso_code"].isna().sum(), "rows")
cols = ["country", "year", "population", "gdp", "co2", "consumption_co2", "trade_co2",
        "trade_co2_share", "co2_per_capita", "consumption_co2_per_capita"]
owid_p = owid.loc[owid["country"].isin(PEERS_OWID) & owid["year"].between(1990, 2023), cols]
report("OWID peers 1990-2023", owid_p, ["country", "year"])
print("Negative trade_co2 (net exporter years) by country:")
print(owid_p[owid_p["trade_co2"] < 0].groupby("country")["year"].agg(["count", "min", "max"]).to_string())

# Flag large year-on-year jumps so we can check them rather than smooth them away
owid_p = owid_p.sort_values(["country", "year"])
jump = owid_p.groupby("country")["consumption_co2"].pct_change().abs()
print("Consumption CO2 year-on-year changes over 15%:")
print(owid_p.loc[jump > 0.15, ["country", "year", "consumption_co2"]].assign(
    change=jump[jump > 0.15].round(2)).to_string(index=False))
owid_p.to_csv(OUT / "owid_peers.csv", index=False)

print("\n== 2. Eurostat FIGARO footprints (env_ac_ghgfp)")
fig = jsonstat_frame(RAW / "eurostat_env_ac_ghgfp.json",
                     {"na_item": {"TOTAL"}, "nace_r2": {"TOTAL", "A01", "H51", "C"}})
print("Rows kept (final use TOTAL, 4 industries):", len(fig))
print("Flags present:", fig["flag"].unique().tolist())
print("Negative values:", (fig["value"] < 0).sum())
fig = fig[~fig["c_orig"].isin(AGGREGATES) & ~fig["c_dest"].isin(AGGREGATES)]
fig["year"] = fig["time"].astype(int)
fig["mt"] = fig["value"] / 1000
report("FIGARO bilateral flows (aggregates removed)", fig, ["c_orig", "c_dest", "nace_r2", "year"])

tot = fig[fig["nace_r2"] == "TOTAL"]
prod = tot.groupby(["c_orig", "year"])["mt"].sum().rename("production_mt")
cons = tot.groupby(["c_dest", "year"])["mt"].sum().rename("consumption_mt")
bal = pd.concat([prod, cons], axis=1).rename_axis(["country", "year"]).reset_index()
bal = bal[bal["country"].isin(PEERS)]
bal["balance_mt"] = bal["consumption_mt"] - bal["production_mt"]
bal["balance_pct_of_production"] = bal["balance_mt"] / bal["production_mt"] * 100
report("FIGARO balance, peers", bal, ["country", "year"])
bal.round(3).to_csv(OUT / "figaro_balance_peers.csv", index=False)

ie = fig[fig["c_orig"] == "IE"]
ind = ie.groupby(["nace_r2", "year"]).agg(
    produced_mt=("mt", "sum"),
    consumed_abroad_mt=("mt", lambda s: s[ie.loc[s.index, "c_dest"] != "IE"].sum()),
).reset_index()
ind["share_abroad_pct"] = ind["consumed_abroad_mt"] / ind["produced_mt"] * 100
ind.round(3).to_csv(OUT / "figaro_ie_industry_exports.csv", index=False)
print("Ireland industry extract rows:", len(ind))

print("\n== 3. Official inventory (env_air_gge, Ireland)")
inv = jsonstat_frame(RAW / "eurostat_env_air_gge_IE.json",
                     {"unit": {"MIO_T"}, "airpol": {"GHG"},
                      "src_crf": {"TOTX4_MEMO", "CRF1", "CRF2", "CRF3", "CRF5", "CRF1A3", "CRF1D1A"}})
print("Flags in selected series:", inv["flag"].value_counts().to_dict())
inv["year"] = inv["time"].astype(int)
labels = {"TOTX4_MEMO": "total_excl_lulucf", "CRF1": "energy", "CRF2": "industrial_processes",
          "CRF3": "agriculture", "CRF5": "waste", "CRF1A3": "transport",
          "CRF1D1A": "intl_aviation_memo"}
inv_w = inv.pivot_table(index="year", columns="src_crf", values="value").rename(columns=labels)
inv_w = inv_w.reset_index()
report("Inventory Ireland by sector", inv_w, ["year"])
inv_w["agriculture_share_pct"] = inv_w["agriculture"] / inv_w["total_excl_lulucf"] * 100
inv_w.round(3).to_csv(OUT / "inventory_ie_sectors.csv", index=False)

print("\n== 4. Cross-source check, Ireland")
ie_owid = owid_p[owid_p["country"] == "Ireland"].set_index("year")["co2"]
ie_fig = bal[bal["country"] == "IE"].set_index("year")["production_mt"]
ie_inv = inv_w.set_index("year")["total_excl_lulucf"]
xcheck = pd.DataFrame({"owid_co2_only": ie_owid, "figaro_production_allgas": ie_fig,
                       "inventory_allgas": ie_inv}).loc[[1990, 2010, 2018, 2020, 2023]]
print(xcheck.round(1).to_string())

print("\n== 5. Reconciling FIGARO production with the inventory (Eurostat bridging table)")
# FIGARO production uses air emissions accounts (residence principle), not the territorial inventory
aea = jsonstat_frame(RAW / "eurostat_env_ac_ainah_r2_IE.json", {})
aea = aea.pivot_table(index="time", columns="nace_r2", values="value") / 1000
brid = jsonstat_frame(RAW / "eurostat_env_ac_aibrid_r2_IE.json", {})
brid = brid.pivot_table(index="time", columns="indic_env", values="value") / 1000
recon = pd.DataFrame({
    "inventory_territory": brid["AEMIS_TER"],
    "plus_residents_fuel_abroad": brid["AEMIS_RES_ABR"],
    "of_which_air": brid["AEMIS_RES_ABR_ATR"],
    "minus_nonresidents_in_ie": -brid["AEMIS_TER_NRES"],
    "aea_residents_total": brid["AEMIS_RES"],
    "minus_households": -aea["HH"],
    "aea_industries": aea["TOTAL"],
})
recon.index = recon.index.astype(int)
recon["figaro_production"] = bal[bal["country"] == "IE"].set_index("year")["production_mt"]
print(recon.loc[[2010, 2018, 2023]].round(2).T.to_string())
recon.round(3).to_csv(OUT / "ie_reconciliation.csv")

print("\nSaved:", sorted(p.name for p in OUT.glob("*.csv")))
