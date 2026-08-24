# Solidarity Tech Tools

[![PyPI - Latest Version](https://img.shields.io/pypi/v/solidaritytechtools?label=PyPI)](https://pypi.org/project/solidaritytechtools/)
[![PyPI - Total Downloads](https://static.pepy.tech/personalized-badge/solidaritytechtools?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=BLUE&left_text=Total+PyPI+Downloads)](https://pepy.tech/projects/solidaritytechtools)
[![PyPI - Monthly Downloads](https://static.pepy.tech/personalized-badge/solidaritytechtools?period=monthly&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=BLUE&left_text=Monthly+PyPI+Downloads)](https://pepy.tech/projects/solidaritytechtools)

[![Build & Publish](https://img.shields.io/github/actions/workflow/status/jackklika/solidaritytechtools/release.yml?branch=main&label=Build%20%26%20Publish)](https://github.com/jackklika/solidaritytechtools/actions/workflows/release.yml)
[![Python Checks](https://img.shields.io/github/actions/workflow/status/jackklika/solidaritytechtools/python.yml?branch=main&label=Python%20Checks)](https://github.com/jackklika/solidaritytechtools/actions/workflows/python.yml)
[![Coverage](https://raw.githubusercontent.com/jackklika/solidaritytechtools/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/jackklika/solidaritytechtools/blob/python-coverage-comment-action-data/htmlcov/index.html)

An unofficial python library to help you automate solidarity tech (ST).

Based on the official ST api page: https://www.solidarity.tech/reference/

This library has tools that have been developed in the act of organizing and working with ST contact data, and should be useful to anyone doing analysis or advanced/bulk operations with Solidarity Tech data, especially when integrating with external data.

solidaritytechtools is technically in beta, but you can still use this in production if you are bold, and I am safely using it on thousands of records. But **I recommend pinning specific versions in your dependencies** to be extra sure things don't break as we increment versions. 

## Getting Started

### Installing as a package (Normal usage)

1. Add `solidaritytechtools` as a dependency via `uv add solidaritytechtools`, `pip install solidaritytechtools`, etc
1. Import the client, models, or functions, like `from solidaritytechtools import STClient, models, best_match_per_person`
1. Pass your ST API Key where required, for example `UserStore.from_api(api_key="...")` or `STClient(api_key="...")`

### Working with source code / running examples (Advanced usage)

If you want to run and edit examples, or fork the code to extend functionality, you should clone the repo:

1. `git clone https://github.com/jackklika/solidaritytechtools.git`
1. `cd solidaritytechtools`
1. `uv sync`

Then you can look at the `/examples` directory for scripts demonstrating usage, and run them.

We want the library to require minimal dependencies, to reduce size and complexity. But some of the the example scripts write parquet, which needs pandas and pyarrow, which are larger dependencies. So they are kept out of the default install and put behind an `analysis` extra instead, so you would need to install this group manually:

```sh
uv sync --extra analysis
```

The `AGENTS.md` file will explain what the agent needs to know

Using Pydantic models provides better type safety and IDE autocompletion, but you can always fall back to a `dict` if the API spec drifts or a model is missing a field.

If you notice client functions not working as expected, feel free to use raw internal methods like `client._get("path")` or `client._put("path", json=payload)` to do what you need, and then submit an issue or a MR.

## Features

- Work with ST entities like Users and Events in python data code
- Create tooling around your ST universe beyond the existing Automations functionality, for example ETL jobs
- Match ST `User` entities with external data sources, like exported VAN lists or DOT data to identify priority targets for yard signs

### Client  
Call python methods to interact with the ST api. You can pass pydantic models and receive pydantic models in return, so you can rely on the response structure.

```python
from solidaritytechtools import STClient, models

with STClient(api_key="...") as client:
    # Perform calls
    users = client.get_users()

    # When passing arguments, you can either pass a Pydantic model (recommended)...
    user_1 = client.create_user(models.UserCreate(
        chapter_id=1, 
        phone_number='4145551234'
    ))

    # ...or a raw dict
    user_2 = client.create_user({
        "chapter_id": 1, 
        "phone_number": "4145551234"
    })
```

The client also handles rate limiting, honoring `Retry-After` headers, so you can be confident scripts won't break when rate limited.


### Contact Matching

You often need to line up the same people across two sources: a csv export from VAN, action network exports, an older ST export, or a live ST account. And sometimes phone numbers are formatted differently, (like `(414) 555-1234` vs `14145551234`) or addresses/zipcodes are typed inconsistantly.

`ContactIndex` normalizes both sides, indexes one of them, and looks the other up. It tries the strongest key first, so a weak name match never overrides a good email match. It is also configurable if you want to tune it, for example setting alternative strategies or changinghow it evaluates ties. 

```python
from solidaritytechtools import ContactIndex, STClient, contact_keys, get_all_users, keys_from_user

with STClient(api_key="...") as client:
    users = get_all_users(client)

index = ContactIndex(users, keys_from_user)

match = index.match(contact_keys(emails="a@example.com", phones="(414) 555-1234"))
if match:
    # .strategy is which key hit, .confidence is how much to trust it
    print(match.record.id, match.strategy, match.confidence)
```

Email and phone are treated as identifying (confidence 1.0), name plus zip code is 0.9, and a name on its own is 0.7 and only matches when exactly one record has that name, since a name shared by five people identifies nobody. **Please look through the code before using this in production to understand what it's doing.**

This works on any record type, you just tell it how to pull the identifiers out of yours. For csv rows, or anything else dict-shaped, `keys_from_mapping` will find the columns for you. Headers are matched ignoring case, spaces and underscores, so `Cell Phone`, `cell_phone` and `cellphone` all work.

```python
import csv
from solidaritytechtools import ContactIndex, contact_keys, keys_from_mapping

with open("volunteers.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

index = ContactIndex(rows, keys_from_mapping)
match = index.match(contact_keys(phones="+1 414-555-1234"))
```

To run a whole dataset through at once, `match_contacts(left, right, left_keys, right_keys)` returns a mapping of left-side position to match. If your source doesn't have an adapter yet, write a function that returns `contact_keys(...)` and pass that in instead. You can also replace the cascade entirely with `strategies=[...]` if you have a better key to match on, like an external id.

#### JSON ST Export -> New ST Account

Use `export_matching.best_match_per_person` to match a solidarity tech json export with a different ST account, for example to migrate notes or properties from one account to another. Every person in the export gets an entry, so a `None` means nothing met the confidence threshold.

```python
from solidaritytechtools import best_match_per_person, ClientUserMatch

# Returns a mapping of {person_id: ClientUserMatch}
# Behind the scenes, this is using the `solidaritytechtools.client` and `solidaritytechtools.json_export`
matches: dict[int, ClientUserMatch | None] = best_match_per_person(
    json_export_file="old_account_export.json",
    api_key="new_account_api_key"
)

for person_id, match in matches.items():
    if match:
        print(f"Export Person {person_id} -> API User {match.user_id} ({match.confidence*100}% confidence)")
```

### Email Matching & Bulk User Operations

Common operations like lookups or updating users require individual API calls per operation, which hits ST rate limits. There are limited batch endpoints, so this makes it hard to work with bulk data.

My solution has been a a cached `UserStore` for fast local lookups and bulk updates, which loads all universe users into memory, and avoids one API call per user (and the rate limits that come with it).

```python
from solidaritytechtools import STClient, UserStore, match_emails_to_user_ids, set_email_permission

# Map a list of emails -> ST user ids (optionally ignoring "+subaddressing")
matches = match_emails_to_user_ids(["a@example.com", "b+promo@example.com"], api_key="...", strip_subaddress=True)

# Or build a reusable, file-cached store and query it locally
store = UserStore.from_api(api_key="...")
user = store.match_email("a@example.com")

# Bulk-set a permission across many users
with STClient(api_key="...") as client:
    set_email_permission(client, matches.values(), permission=False)
```

### Traffic Scoring (yard-sign prioritization) (Currently WI only)

Score contacts by how much traffic passes their home and optionally write the score to a custom user property. You can then then create sorted lists in ST to prioritize who to call to make sure yard signs get the most views.

It includes some logic where freeways are excluded so homes snap to the nearest sign-visible surface street. Supports dry runs and a Members-in-Good-Standing filter.

```python
from solidaritytechtools import add_traffic_data

# Dry run: score Members in Good Standing, write nothing
result = add_traffic_data(api_key="...", members_in_good_standing_only=True, dry_run=True)
for contact in result.scored[:10]:
    print(contact.hash_id, contact.aadt, contact.address)
```

### CSV Tools

When working with VAN or ActionNetwork or other tools, you commonly get a csv export. There is some minor convenience tooling to help make working with this easier.

The csv tools have a convenince function to get the only column with emails. This package can be extended for other types.

```python
from solidaritytechtools.utils.csv_tools import get_emails_from_csv

emails = get_emails_from_csv("contacts.csv")
```

### JSON Export Tools

The library includes tools for validating and parsing Solidarity Tech JSON export files into structured models.

```python
from solidaritytechtools import get_persons_from_json_export

# Load and validate an export file
people = get_persons_from_json_export("export-members-data.json")

for person in people:
    print(f"{person.first_name} {person.last_name} has {len(person.notes)} notes")
```

## Contributing

1. Clone the repo 
1. Run `uv sync`
1. Install pre-commit hooks (`uv run pre-commit install`) and make sure they run on commit - If you don't, your changes will likely break CICD.
1. Start coding and make a MR :)
1. Add some tests around your functionality
1. Ensure all tests and github workflows are passing before requesting review, including `ty`, `ruff format`, and `ruff check`.

Note that we purposely gitignore common data extensions like `*.csv`, `*.pdf`, or `*.parquet` since it is critical we do not introduce any PII into source control. So if you want to add a file with this format, for example for testing, you need to whitelist specific files in `.gitignore`.

### Contribution Guidelines:
- Don't introduce new dependencies, especially heavy dependencies, unless it it makes sense to do so.
- Preserve compatibility with previous versions, so people's code doesn't break if they are using this pypi package and bump minor versions.
- Try to match existing style.
- Don't vibecode too hard, make sure you understand what is happening and try to keep things modular and clean. 
  The human contributor must review and be accountable for all LLM-generated code.
- Do not commit any PII, or files containing PII, to this repo. This includes tests, comments, and example scripts.

## Publishing

The maintainer will probably take care of this

1. `uv version --bump patch` (or minor, major etc)
1. `uv sync`
1. `git add pyproject.toml uv.lock`
1. `git commit -m "Release $(uv version)" && git tag v$(uv version --short)`
1. `git push origin main --tags`

Github workflow will push to pypi.
