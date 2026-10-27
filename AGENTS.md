# AGENTS.md

The ways of working we've agreed as a group. It's written for the AI assistants each of us
uses (Copilot, Claude, ChatGPT, etc.) so they all follow the same process. Point your
assistant at this file, or paste it in, before starting work, and update it when we agree
something new.

## The project

"Cut or Outsourced? What Europe's Emissions Success Means for Ireland". We compare
territorial and consumption-based greenhouse gas emissions for Ireland and six peers (UK,
Denmark, Germany, France, Sweden, Netherlands), to see whether the usual comparisons change
once emissions embodied in imports are counted.

- Audience: Oireachtas committee and Climate Change Advisory Council staff who write
  briefings. Policy-literate, not statisticians, about 5-10 minutes per read.
- Final output: a static A4 visual report of 4-5 figures, also used as presentation slides.
  We chose static over a dashboard because Ireland's year-to-year figures are volatile and
  free exploration of single years could mislead.

## Project instructions

The course brief is not in the repo (it's the lecturer's material, so it stays out via
`.gitignore`). Before starting any deliverable:

1. Look for a folder whose name starts with `Project Instructions` in the repo root. It
   should contain:
   - Document 1 - Group Data Visualization Project Brief.docx
   - Document 2 - Integrating AI into the Data Visualization Project.docx
   - Document 3 - Required Project Submissions.docx
   - What AI Can Do.pdf
2. If it's there, read the parts that apply to the deliverable you're working on, not just
   the summary. Use the documents for different things:
   - Document 3 is the checklist. It lists the required content and suggested length for
     each of the seven submissions. Every required item should appear in the deliverable,
     under a heading that makes it easy for the marker to find.
   - Document 1 explains what good work looks like at each step (e.g. what a data audit
     should investigate, what to keep for data provenance, what the oral defence covers)
     and has the suggested timeline. Use it to judge quality, not just completeness.
   - Document 2 sets the rules for AI use, the AI Decision Log and the final reflection.
     Check it before any step where AI is doing a lot of the work.
   Before calling a deliverable done, go back through Document 3 item by item and check
   each one is covered. Say which items are missing or thin rather than assuming.
3. If it's missing, stop and ask the person you're helping to download the project
   instructions from Moodle and save them in a `Project Instructions/` folder in the repo
   root. Don't guess the requirements from memory.

## Who owns what

| Member | GitHub | Primary | Secondary review |
|---|---|---|---|
| Charlie | @cgallagher-dev | Data preparation, processing scripts, prepared CSVs. Submits all group deliverables | Visualisation |
| Lucy | @DipsyTheCPU | Design cards, plotting code, final figures | Story and audience |
| Seán | @Seanwbardon | Messages, narrative, presentation, AI Decision Log | Data |

- Only work on issues assigned to the person you are helping. If a task belongs to someone
  else's issue, stop and say so.
- Everyone must understand the whole project. Any of us can be asked about any decision in
  the oral defence, so explain reasoning, not just output.
- Commits only go in under the name of the person who did the work.

## Schedule

No fixed submission dates, so we follow the suggested timeline in the brief (week of 28
September = Week 3). Drafts are reviewed at our Wednesday meeting and finished that Friday.
Due dates are on each GitHub issue.

| Week | Deliverable | Draft (Wed) | Done (Fri) |
|---|---|---|---|
| 7 | Team Charter; Audience Brief and Data Audit | 28 Oct | 30 Oct |
| 7-8 | Message statement and design cards | 4 Nov | 6 Nov |
| 9 | Draft visual story | 11 Nov | 13 Nov |
| 10 | Final visualisation package | 18 Nov | 20 Nov |
| 11 | Presentation (rehearsal Mon 23 Nov), AI log and reflections | 25 Nov | 27 Nov |

## Git and GitHub

- Repo: https://github.com/cgallagher-dev/cut-or-outsourced (public).
- Every piece of work has an issue with an owner, a reviewer and a due date. Labels:
  `submission-1` to `submission-7`, plus `data`, `visualisation`, `story`, `review`.
- One branch per issue, named after the task (e.g. `investment-spike`). Branch from `main`.
- Open a pull request that says `Closes #N` and requests the issue's reviewer. `main` needs
  one approving review.
- PR description: purpose first, then "What it shows", "What I think this means for us" and
  "Worth checking in review". Include the key numbers so the reviewer can check them. See
  PR #17 for an example.
- Commit with your GitHub no-reply email, not a work or college address
  (`git config user.email <id>+<username>@users.noreply.github.com`).
- Don't commit, push, merge or open PRs unless the person you're helping asks. Ask before
  anything public or hard to undo.
- Not in the repo (`.gitignore`): course instructions, the AI Decision Log (until the end),
  the 243 MB FIGARO file, `.venv/`.
- Agreed changes to questions, data or design go in one line in the Discord #decisions
  channel.

## Writing (commits, comments, PRs, deliverables)

Everything public should read like one of us wrote it.

- Plain and short. Say what changed and why, then stop.
- Irish/UK spelling (visualisation, colour, analyse).
- No em dashes, no emoji, no filler ("delve", "leverage", "robust", "seamless",
  "comprehensive", "it's worth noting", "not just X but Y"). Don't scatter bold headings.
- Commit subject: short, imperative, capitalised, no full stop ("Add design cards"). Body
  only if needed, wrapped at about 72 characters, saying what and why.
- Code comments only where they explain why, in one short line.
- Never include a predetermined conclusion. State what the data shows and what we haven't
  checked.

## Deliverables (Word documents)

- Saved in `deliverables/` as `Cut or Outsourced (<Name>).docx`.
- Built with python-docx in the same style as the existing ones: `Heading 1` for the
  document title, a bold "Group members:" line, `Heading 2` for sections, `List Bullet` and
  `List Number` for lists, tables in `Light Grid Accent 1` at 9pt. Spacing: 6pt before,
  4pt after.
- Check the page count in Microsoft Word against the brief (pitch about 1 page, proposal
  2-3 pages) and trim content rather than shrinking fonts. Decide what to cut; don't just
  shorten everything evenly.
- Cite sources with real hyperlinks: inline on the first mention of a dataset, policy or
  organisation, plus a "Sources" list at the end. Only use URLs you have opened and checked.
- Before committing, clear python-docx metadata: set the author to the three of us and
  empty the comments field (python-docx writes "generated by python-docx").
- Every figure in a deliverable must come from a script run, not from memory or chat.

## Checking facts

This has caught several mistakes already, so keep doing it.

- Re-run the script and read the number from its output before writing it down.
- Check claims about a dataset against its official metadata page, not memory. Example:
  the gap between FIGARO and the inventory was only explained after reading Eurostat's
  metadata and reconciling with the bridging table (`notebooks/data_audit.py`, section 5).
- If something can't be verified yet, write it as "likely" or "not checked" and add a task
  for it.
- Sanity-check totals against a known figure (e.g. Ireland is about 55-62 Mt CO2e). Our
  first FIGARO total was double because aggregates were included.
- When breaking a total into parts, check the parts add up to the reported total.

## Code and data

- Plain Python scripts in `notebooks/`, run from the repo root
  (`python notebooks/<script>.py`). Top-level code that prints its results, no classes or
  frameworks. Match the existing scripts.
- Set up with `python -m venv .venv`, `source .venv/bin/activate`,
  `pip install -r requirements.txt`. Add any new package to `requirements.txt`.
- Eurostat JSON-stat files are flattened with the `jsonstat_frame` function (copied into
  each script that needs it, since the scripts aren't importable modules).
- Raw downloads go in `data/raw/` (Eurostat API:
  `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/<code>?...`) and are
  kept unchanged. Record the download date in the data audit.
- Prepared data goes in `data/processed/`, written by a script, never edited by hand.
- Don't remove outliers or impute values without discussing it. Unusual values are flagged,
  investigated and annotated.

## Data rules

- The three sources use different accounting rules. Never add them together or treat one
  as a correction of another. Compare side by side and explain the difference.
  - Our World in Data: CO2 only, 1990-2023, territorial and consumption-based.
  - Eurostat FIGARO footprints (`env_ac_ghgfp`): all gases, 2010-2023. Production side uses
    the residence principle (includes Irish airlines flying abroad) and excludes households'
    own emissions (heating, private cars).
  - EPA inventory (`env_air_gge`): all gases, territory principle, the basis of the 51%
    target (vs 2018).
- In FIGARO, drop the `EU27_2020`, `EXT_EU27_2020` and `WORLD` aggregates before summing.
  For industries, use the one-letter NACE sections (A-U); other codes overlap.
- Ireland's 2019-20 footprint spike comes from intellectual property investment
  (`notebooks/investment_spike.py`). Keep the values, annotate them, don't draw trends
  through those years, and don't state why IP investment surged as fact.
- The UK is missing from the Eurostat peer inventory file (it left EU reporting). OWID GDP
  is missing for 2023.

## AI use

The brief allows AI but marks us on human judgement.

- AI suggests, we decide. Compare alternatives before accepting a chart or analysis
  suggestion. "The AI chose it" is not a reason we can give.
- Log every case where AI meaningfully affected the project. Post a short note in
  #decisions and Seán adds it to the AI Decision Log, which has the columns: Date
  (dd/mm/yyyy), Stage (Topic, Data, Cleaning, Analysis, Chart, Design, Story), AI
  Contribution, Decision (e.g. Accepted, Accepted with revision, Rejected, Rejected and
  corrected, Accepted after verification), Explanation.
- Rejections and corrections are the most valuable entries. Write down exactly what the AI
  got wrong and how we found out.
- Don't make claims the data can't support (causes, motives).
