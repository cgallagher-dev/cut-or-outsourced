import json

import pandas as pd

d = json.load(open("data/raw/eurostat_env_ac_ghgfp.json"))
dims, sizes = d["id"], d["size"]
index = {dim: d["dimension"][dim]["category"]["index"] for dim in dims}

# JSON-stat stores values against a flat index, so work out the stride per dimension
strides = {}
step = 1
for dim, size in zip(reversed(dims), reversed(sizes)):
    strides[dim] = step
    step *= size

aggregates = {"EU27_2020", "EXT_EU27_2020", "WORLD"}
print("Partner codes:", [c for c in index["c_orig"] if c not in aggregates])

size_of = dict(zip(dims, sizes))
lookup = {dim: {v: c for c, v in index[dim].items()} for dim in ("c_orig", "c_dest", "time")}
total_item = index["na_item"]["TOTAL"]
total_nace = index["nace_r2"]["TOTAL"]

rows = []
for key, value in d["value"].items():
    k = int(key)
    if (k // strides["na_item"]) % size_of["na_item"] != total_item:
        continue
    if (k // strides["nace_r2"]) % size_of["nace_r2"] != total_nace:
        continue
    rows.append((lookup["c_orig"][(k // strides["c_orig"]) % size_of["c_orig"]],
                 lookup["c_dest"][(k // strides["c_dest"]) % size_of["c_dest"]],
                 int(lookup["time"][(k // strides["time"]) % size_of["time"]]), value))

df = pd.DataFrame(rows, columns=["orig", "dest", "year", "kt"])
# Drop EU aggregates so flows aren't double counted; keep rest-of-world partners
df = df[~df["orig"].isin(aggregates) & ~df["dest"].isin(aggregates)]

production = df.groupby(["orig", "year"])["kt"].sum() / 1000
consumption = df.groupby(["dest", "year"])["kt"].sum() / 1000
out = pd.DataFrame({"production_mt": production, "consumption_mt": consumption})
out.index.names = ["country", "year"]
out["net_import_%"] = (out["consumption_mt"] / out["production_mt"] - 1) * 100

peers = ["IE", "UK", "DK", "DE", "FR", "SE", "NL", "US", "CN"]
print(out.loc[peers].xs(2023, level="year").round(1).to_string())
print("\nIreland over time:")
print(out.loc["IE"].loc[[2010, 2015, 2020, 2023]].round(1).to_string())

change = (out.xs(2023, level="year") / out.xs(2010, level="year") - 1) * 100
print("\n% change 2010 -> 2023:")
print(change.loc[peers, ["production_mt", "consumption_mt"]].round(1).to_string())
