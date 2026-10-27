import pandas as pd

df = pd.read_csv("data/raw/owid-co2-data.csv")
countries = df[df["iso_code"].notna() & ~df["iso_code"].str.startswith("OWID", na=False)]

cons = countries[countries["consumption_co2"].notna()]
print("Consumption CO2 coverage:", cons["year"].min(), "-", cons["year"].max(),
      "|", cons["country"].nunique(), "countries")

cols = ["year", "co2", "consumption_co2", "trade_co2_share", "total_ghg", "methane",
        "co2_per_capita", "consumption_co2_per_capita", "gdp"]
ire = countries[countries["country"] == "Ireland"].set_index("year")
print("\nIreland:")
print(ire.loc[[1990, 2000, 2005, 2010, 2015, 2018, 2020, 2021, 2022, 2023], cols[1:]].round(1).to_string())

last = int(cons["year"].max())
a = cons[cons["year"] == 1990].set_index("country")
b = cons[cons["year"] == last].set_index("country")
both = a.index.intersection(b.index)
cmp = pd.DataFrame({
    "territorial_change_%": (b.loc[both, "co2"] / a.loc[both, "co2"] - 1) * 100,
    "consumption_change_%": (b.loc[both, "consumption_co2"] / a.loc[both, "consumption_co2"] - 1) * 100,
    f"trade_share_{last}": b.loc[both, "trade_co2_share"],
    "pop_m": b.loc[both, "population"] / 1e6,
}).round(1)
cmp["gap_pts"] = cmp["consumption_change_%"] - cmp["territorial_change_%"]
big = cmp[cmp["pop_m"] > 3]
print(f"\n1990 -> {last}, countries > 3m people, biggest gap between the two measures:")
print(big.sort_values("gap_pts", ascending=False).head(12).to_string())
print("\nSelected:")
print(cmp.loc[["Ireland", "United Kingdom", "Germany", "France", "Denmark",
               "United States", "China", "India", "Sweden"]].to_string())
