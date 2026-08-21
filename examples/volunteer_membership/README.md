# Volunteer → DSA membership analysis

Works out the DSA membership state of every campaign volunteer, and specifically **who
volunteered first and became a member afterwards**.

Takes two kinds of VAN export, collapses them into one row per distinct person, matches each
person to a Solidarity Tech user, and writes the result to parquet.

| Input | Shape | Carries |
|---|---|---|
| Volunteer-list PDFs | one block per person, two column layout | name, city/state/ZIP, age, sex, up to 3 phones |
| Shift-signup CSVs | one row per person per shift | VanID, event, date, name, phone, email, role, status |

The PDFs have no shift dates and no emails; the CSVs have both. Linking them is what gives
PDF-listed people a volunteer date.

## Running it

Needs poppler's `pdftotext` on PATH (`brew install poppler`), and the `analysis` extra for
pandas/pyarrow (they aren't installed by default, since they're ~200MB and nothing in the
library itself uses them).

```sh
export ST_API_KEY=...
export VOLUNTEER_PDF_DIR="/path/to/volunteer list pdfs"
export VOLUNTEER_CSV_DIR="/path/to/shift signup csvs"
export VOLUNTEER_OUTPUT_DIR="/path/to/write/parquet"   # keep this outside the repo

uv run --extra analysis python examples/volunteer_membership/run.py
```

`UserStore` caches every ST user to a temp file on first run, so re-runs are fast. Pass
`refresh=True` to `UserStore.from_api` to re-fetch.

Outputs `volunteers.parquet` (one row per person) and `volunteer_shifts.parquet` (one row per
shift, so any other definition of "volunteered" can be re-sliced without re-running).

## Where membership state comes from

The ST **api**, not a json export. Two reasons:

- The api returns every user, not just members, so "in ST but never a member" is
  distinguishable from "not in ST at all".
- Membership lives in custom user properties. `join-date` is populated for everyone carrying a
  membership status, and it is what makes the before/after comparison possible. See
  `solidaritytechtools.utils.membership`.

## Modules

| File | Does |
|---|---|
| `pdf_volunteers.py` | parses volunteer-list PDFs via `pdftotext -bbox-layout` |
| `shift_signups.py` | reads VAN shift-signup CSVs |
| `roster.py` | dedupes both sources into one row per person |
| `matching.py` | matches people to ST users on email / phone / name+ZIP |
| `run.py` | wires it together, prints the summary, writes parquet |

### Why the PDFs are parsed by coordinate

`pdftotext -layout` puts the right-hand column at a different character offset in every file
(it sizes to the widest value), so a fixed character split does not hold. Reading word
coordinates avoids that.

Within a record, fields are looked up by **expected y-offset** on the 11pt row pitch rather than
by row index. A missing phone value emits no line at all, so an index-based read would silently
shift every later field — this is the one real trap in the format.

Extraction is checked against an independent count of `"Preferred Phone"` occurrences in the raw
text (one per record) and the run fails if the two disagree.

## Reading the results

`membership_state` is the headline column:

- `Member in Good Standing` / `Lapsed` / `Lapsed Member` / `Constitutional Member` — matched, with that status
- `In ST, never a member` — matched to an ST user with no membership status
- `Not in Solidarity Tech` — no match at all

`became_member_after_first_shift` is the answer to the main question. It is only set where both
a completed-shift date and a join date are known.

### Caveats

- **`join-date` reflects the current membership start.** Someone who lapsed and rejoined may
  show a later date than their true first join, which inflates
  `became_member_after_first_shift` for returning members.
- **Volunteers with no shift date** (listed only in a PDF) can't be compared per-person. They
  get the coarser `joined_during_or_after_campaign` flag instead, based on the campaign window.
- **Chapter coverage.** Matching is chapter-agnostic, but the ST instance only holds the
  chapters you have access to. Watch the per-region unmatched rate in the summary: if one
  region is largely unmatched, the headline rate reflects the covered chapters only, not the
  whole state.
- Name-only matches are recorded at 0.7 confidence and excluded from headline figures, which
  use `>= 0.9`.
