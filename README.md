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

## Data sources

| Dataset | Source |
|---|---|
| CO2 and greenhouse gas emissions | [Our World in Data](https://github.com/owid/co2-data) |
| Greenhouse gas footprints, FIGARO (`env_ac_ghgfp`) | [Eurostat](https://ec.europa.eu/eurostat/databrowser/product/view/env_ac_ghgfp) |
| Greenhouse gas emissions by source sector (`env_air_gge`) | [Eurostat](https://ec.europa.eu/eurostat/databrowser/product/view/env_air_gge) |
| Air emissions accounts (`env_ac_ainah_r2`) and bridging items (`env_ac_aibrid_r2`) | [Eurostat](https://ec.europa.eu/eurostat/databrowser/product/view/env_ac_aibrid_r2) |

The FIGARO file is too large for GitHub. Download the full dataset in JSON-stat format from
the Eurostat API and save it as `data/raw/eurostat_env_ac_ghgfp.json`:

```
curl -o data/raw/eurostat_env_ac_ghgfp.json "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/env_ac_ghgfp"
```

## Running

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python notebooks/data_audit.py
```

Scripts are run from the repository root.
