import json

import pandas as pd

PEERS_OWID = ["Ireland", "United Kingdom", "Denmark", "Germany", "France", "Sweden", "Netherlands"]
PEERS = ["IE", "UK", "DK", "DE", "FR", "SE", "NL"]


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
    rows = []
    for key, value in d["value"].items():
        k = int(key)
        rec = {dim: rev[dim][(k // strides[dim]) % size] for dim, size in zip(dims, sizes)}
        if all(rec[dim] in allowed for dim, allowed in keep.items()):
            rec["value"] = value
            rows.append(rec)
    return pd.DataFrame(rows)


print("== 1. Our World in Data (CO2, territorial + consumption)")
owid = pd.read_csv("data/raw/owid-co2-data.csv")
sub = owid[owid["country"].isin(PEERS_OWID) & owid["year"].between(1990, 2023)]
cov = sub.groupby("country")[["co2", "consumption_co2", "population", "gdp"]].count()
print("Years with data, 1990-2023 (34 possible):")
print(cov.to_string())

print("\n== 2. Eurostat FIGARO footprints (all GHG, 2010-2023)")
fig = jsonstat_frame("data/raw/eurostat_env_ac_ghgfp.json",
                     {"na_item": {"TOTAL"}, "unit": {"THS_T"}})
agg = {"EU27_2020", "EXT_EU27_2020", "WORLD"}
fig = fig[~fig["c_orig"].isin(agg) & ~fig["c_dest"].isin(agg)]
fig["time"] = fig["time"].astype(int)
tot = fig[fig["nace_r2"] == "TOTAL"]
print("Years per peer (14 possible):",
      {c: tot[tot["c_orig"] == c]["time"].nunique() for c in PEERS})

ie_prod = fig[(fig["c_orig"] == "IE")]
ie_exported = ie_prod[ie_prod["c_dest"] != "IE"].groupby(["nace_r2", "time"])["value"].sum() / 1000
ie_all = ie_prod.groupby(["nace_r2", "time"])["value"].sum() / 1000
for code, label in [("A01", "Farming (A01)"), ("H51", "Air transport (H51)"), ("C", "Manufacturing (C)")]:
    print(f"\nIreland {label}, Mt CO2e produced / of which consumed abroad:")
    for yr in (2010, 2015, 2020, 2023):
        print(f"  {yr}: {ie_all.get((code, yr), float('nan')):.1f} / {ie_exported.get((code, yr), float('nan')):.1f}")

ie_cons = tot[tot["c_dest"] == "IE"].groupby("time")["value"].sum() / 1000
by_item = jsonstat_frame("data/raw/eurostat_env_ac_ghgfp.json",
                         {"nace_r2": {"TOTAL"}, "c_dest": {"IE"}, "time": {"2019", "2020", "2021"}})
by_item = by_item[~by_item["c_orig"].isin(agg)].groupby(["time", "na_item"])["value"].sum().unstack() / 1000
print("\nIreland consumption footprint by final use, Mt (checking the 2020 spike):")
print(by_item.round(1).to_string())

print("\n== 3. Official inventory (Eurostat env_air_gge)")
inv = jsonstat_frame("data/raw/eurostat_env_air_gge_IE.json",
                     {"unit": {"MIO_T"}, "airpol": {"GHG"},
                      "src_crf": {"TOTX4_MEMO", "CRF3", "CRF1A3A", "CRF1D1A"}})
inv = inv.pivot_table(index="time", columns="src_crf", values="value")
inv.columns = [{"TOTX4_MEMO": "total", "CRF3": "agriculture",
                "CRF1A3A": "domestic_aviation", "CRF1D1A": "intl_aviation_memo"}.get(c, c) for c in inv.columns]
print(inv.loc[["1990", "2010", "2018", "2023"]].round(2).to_string())
