import json
from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
AGGREGATES = {"EU27_2020", "EXT_EU27_2020", "WORLD"}


def jsonstat_frame(path, keep):
    """Flatten a Eurostat JSON-stat file, keeping only rows where each dim is in keep[dim]."""
    d = json.load(open(path))
    dims, sizes = d["id"], d["size"]
    rev = {k: {v: c for c, v in d["dimension"][k]["category"]["index"].items()} for k in dims}
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


YEARS = {str(y) for y in range(2016, 2024)}

# Every industry, but only flows consumed in Ireland
fp = jsonstat_frame(RAW / "eurostat_env_ac_ghgfp.json", {"c_dest": {"IE"}, "time": YEARS})
fp = fp[~fp["c_orig"].isin(AGGREGATES)]
fp["year"] = fp["time"].astype(int)
fp["mt"] = fp["value"] / 1000

print("== Ireland's consumption footprint by final use, Mt CO2e")
by_use = fp[fp["nace_r2"] == "TOTAL"].pivot_table(index="year", columns="na_item",
                                                  values="mt", aggfunc="sum")
print(by_use.round(1).to_string())

inv = fp[fp["na_item"] == "P51G"]
inv_total = inv[inv["nace_r2"] == "TOTAL"]
# One-letter NACE sections don't overlap; the subsector and services codes do
sections = inv[inv["nace_r2"].str.fullmatch(r"[A-U]")]
labels = json.load(open(RAW / "eurostat_env_ac_ghgfp.json"))["dimension"]["nace_r2"]["category"]["label"]

print("\n== Investment footprint by producing industry section, Mt CO2e (top 8 in 2019)")
ind = sections.pivot_table(index="nace_r2", columns="year", values="mt", aggfunc="sum")
ind.index = [f"{c} {labels[c][:35]}" for c in ind.index]
print(ind.sort_values(2019, ascending=False).head(8).round(1).to_string())

print("\n== Investment footprint by country of origin, Mt CO2e (top 8 in 2019)")
orig = inv_total.pivot_table(index="c_orig", columns="year", values="mt", aggfunc="sum")
print(orig.sort_values(2019, ascending=False).head(8).round(1).to_string())

print("\nSum of sections vs reported investment total:")
print(pd.DataFrame({"sum_of_sections": sections.groupby("year")["mt"].sum(),
                    "reported_total": by_use["P51G"]}).round(2).to_string())

print("\n== Ireland's investment (GFCF) by asset type, EUR bn, current prices (nama_10_an6)")
gfcf = jsonstat_frame(RAW / "eurostat_nama_10_an6_IE.json", {})
asset_labels = json.load(open(RAW / "eurostat_nama_10_an6_IE.json"))["dimension"]["asset10"]["category"]["label"]
gfcf = gfcf.pivot_table(index="asset10", columns="time", values="value") / 1000
gfcf.index = [f"{a} {asset_labels[a][:45]}" for a in gfcf.index]
print(gfcf.round(1).to_string())
