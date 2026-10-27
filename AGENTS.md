# AGENTS.md

Instructions for AI coding assistants (Copilot, Claude, ChatGPT, etc.) working in this repo.
Read this before doing anything. It applies to all three of us: Charlie Gallagher,
Lucy O'Connor and Seán Bardon.

## The project

"Cut or Outsourced? What Europe's Emissions Success Means for Ireland". A group data
visualisation project comparing territorial and consumption-based greenhouse gas emissions
for Ireland and six peers (UK, Denmark, Germany, France, Sweden, Netherlands).

Audience: Oireachtas committee and Climate Change Advisory Council staff who write briefings.
Final output: a static A4 visual report of 4-5 figures, also used as presentation slides.

## Who owns what

| Member | GitHub | Primary | Secondary review |
|---|---|---|---|
| Charlie | @cgallagher-dev | Data preparation, processing scripts, prepared CSVs. Submits all group deliverables | Visualisation |
| Lucy | @DipsyTheCPU | Design cards, plotting code, final figures | Story and audience |
| Seán | @Seanwbardon | Messages, narrative, presentation, AI Decision Log | Data |

- Only work on issues assigned to the person you are helping. If a task belongs to someone
  else's issue, stop and say so rather than doing it.
- Everyone must understand the whole project. Any of us can be asked about any decision in
  the oral defence, so explain your reasoning rather than just producing output.

## How we work

- Every piece of work has a GitHub issue with an owner, a reviewer and a due date.
- Work on a branch, open a pull request that says `Closes #N`, and ask the reviewer on the
  issue to review it. `main` needs one approving review.
- Do not commit, push, merge or open pull requests unless the person you are helping asks.
- Drafts are reviewed at our Wednesday meeting and finished by that Friday.
- Agreed changes to questions, data or design go in one line in the Discord #decisions
  channel.

## Writing (comments, commit messages, PRs, deliverables)

Everything public should read like one of us wrote it.

- Plain and short. Say what changed and why, then stop.
- Irish/UK spelling (visualisation, colour, analyse).
- No em dashes, no emoji, no filler ("delve", "leverage", "robust", "seamless",
  "comprehensive", "it's worth noting"). Don't scatter bold headings everywhere.
- Commit subject: short, imperative, capitalised, no full stop ("Add design cards").
- Code comments only where they explain why, in one short line.
- Match the style of the existing scripts in `notebooks/`. Keep code simple enough that the
  owner can explain every line.

## Data rules

- Run scripts from the repo root. `notebooks/data_audit.py` writes everything in
  `data/processed/`.
- The three sources use different accounting rules. Never add them together or treat one
  as a correction of another. Compare them side by side and explain the difference.
  - Our World in Data: CO2 only, 1990-2023, territorial and consumption-based.
  - Eurostat FIGARO footprints (`env_ac_ghgfp`): all gases, 2010-2023, residence principle,
    excludes households' own emissions.
  - EPA inventory (`env_air_gge`): all gases, territory principle, the basis of the 51% target.
- In FIGARO, drop the `EU27_2020`, `EXT_EU27_2020` and `WORLD` aggregates before summing,
  or totals double.
- Ireland's 2019-20 footprint spike comes from intellectual property investment (see
  `notebooks/investment_spike.py`). Keep the values, annotate them, and don't draw trends
  through those years. Don't state why IP investment surged as fact; we haven't checked.
- The FIGARO raw file (243 MB) is not in the repo. See the README for how to get it.
- Check every number before it goes in a deliverable. Re-run the script; don't copy
  figures from chat.

## AI use

The project brief allows AI but we must show human judgement.

- If AI meaningfully changes a decision (topic, data, cleaning, chart, design, story), post
  a short note in #decisions: what it suggested, what we did, and why. Seán adds it to the
  AI Decision Log.
- The AI Decision Log stays out of the repo until the end (it is in `.gitignore`).
- Don't accept AI chart or analysis suggestions without comparing alternatives. "The AI
  chose it" is not a reason we can give.
- Don't make claims the data can't support (causes, motives). Say what we checked and what
  we didn't.
