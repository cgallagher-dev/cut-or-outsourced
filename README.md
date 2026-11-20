# Cut or Outsourced? What Europe's Emissions Success Means for Ireland

Group data visualisation project by Charlie Gallagher, Lucy O'Connor and Seán Bardon.

We compare territorial and consumption-based greenhouse gas emissions for Ireland and six
European peers (UK, Denmark, Germany, France, Sweden, Netherlands), to see whether the usual
comparisons change once emissions embodied in imports are counted.

## Repository layout

- `deliverables/` - staged submissions (pitch, proposal, team charter, audience brief and data audit)
- `notebooks/` - data exploration and audit scripts
- `data/raw/` - downloaded source data
- `data/processed/` - prepared datasets written by `notebooks/data_audit.py`
- `data/processed/figures/` - one prepared table per figure, written by `notebooks/figure_tables.py`
- `figures/` - the figures as PNG and SVG, written by `notebooks/figures.py`

## Data sources

| Dataset | Source |
|---|---|
| CO2 and greenhouse gas emissions | [Our World in Data](https://github.com/owid/co2-data) |
| Greenhouse gas footprints, FIGARO (`env_ac_ghgfp`) | [Eurostat](https://ec.europa.eu/eurostat/databrowser/product/view/env_ac_ghgfp) |
| Greenhouse gas emissions by source sector (`env_air_gge`) | [Eurostat](https://ec.europa.eu/eurostat/databrowser/product/view/env_air_gge) |
| Air emissions accounts (`env_ac_ainah_r2`) and bridging items (`env_ac_aibrid_r2`) | [Eurostat](https://ec.europa.eu/eurostat/databrowser/product/view/env_ac_aibrid_r2) |

The FIGARO file (about 307 MB) is too large for GitHub. Download the full dataset in
JSON-stat format from the Eurostat API and save it as `data/raw/eurostat_env_ac_ghgfp.json`.
Eurostat sometimes answers a large request with error 413 ("asynchronous response") and
prepares the file in the background, so the command retries every minute until it arrives:

```
curl --fail --retry 20 --retry-delay 60 --retry-all-errors -o data/raw/eurostat_env_ac_ghgfp.json "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/env_ac_ghgfp"
```

We use the release of 30 October 2026 (2010-2024), downloaded on 18 November 2026. The
earlier release (2010-2023, downloaded 28 September 2026) gave different consumption
figures, so check the `updated` field in the file if your numbers don't match ours.

## Running

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python notebooks/data_audit.py
python notebooks/figure_tables.py
python notebooks/figures.py
```

Scripts are run from the repository root. On Windows, activate the environment with
`.venv\Scripts\Activate.ps1` instead of `source .venv/bin/activate`.

## Figures

`notebooks/figures.py` draws four figures from the tables in `data/processed/figures/` and
saves each as PNG (200 dpi) and SVG in `figures/`. It does no data preparation of its own.

| File | Shows | Data |
|---|---|---|
| `fig1_long_term_cuts` | Territorial and consumption-based CO2 for the seven countries, index 1990 = 100, 1990-2023 | Our World in Data |
| `fig2_footprint_balance` | Consumption minus production as % of production: 2024 with and without shipping and airlines, and 2010-2024 | FIGARO |
| `fig3_irish_industries` | Emissions produced by Irish industries in 2024, consumed in Ireland or abroad | FIGARO |
| `fig4_why_numbers_differ` | Ireland 2024, from the territorial inventory to FIGARO production | Eurostat bridging tables |

- Sizes, fonts, colours and the draft titles are set once at the top of the script. The
  slides use 13.33 x 7.5 in; the A4 report versions change those values, not the code.
- Text is set in DejaVu Sans, which ships with matplotlib, so the files are the same on
  every machine.
- The script stops if any text runs off the edge of a figure, if Figure 3's bars don't add
  up to Ireland's FIGARO total, or if a total in Figure 4 doesn't equal the steps before it.
- Figure 4's first bar is labelled "Inventory (territory principle)" in the script, because
  53.75 Mt is the bridging table's inventory figure rather than the `env_air_gge` total.
- Denmark's share of shipping and airlines in Figure 2 is read from
  `data/processed/figaro_balance_peers.csv`, the one value not in the figure tables.
