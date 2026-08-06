# Solidarity Tech Tools

[![PyPI - Latest Version](https://img.shields.io/pypi/v/solidaritytechtools?label=PyPI)](https://pypi.org/project/solidaritytechtools/)
[![PyPI - Total Downloads](https://static.pepy.tech/personalized-badge/solidaritytechtools?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=BLUE&left_text=Total+PyPI+Downloads)](https://pepy.tech/projects/solidaritytechtools)
[![PyPI - Monthly Downloads](https://static.pepy.tech/personalized-badge/solidaritytechtools?period=monthly&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=BLUE&left_text=Monthly+PyPI+Downloads)](https://pepy.tech/projects/solidaritytechtools)

[![Build & Publish](https://img.shields.io/github/actions/workflow/status/jackklika/solidaritytechtools/release.yml?branch=main&label=Build%20%26%20Publish)](https://github.com/jackklika/solidaritytechtools/actions/workflows/release.yml)
[![Python Checks](https://img.shields.io/github/actions/workflow/status/jackklika/solidaritytechtools/python.yml?branch=main&label=Python%20Checks)](https://github.com/jackklika/solidaritytechtools/actions/workflows/python.yml)
[![Coverage](https://raw.githubusercontent.com/jackklika/solidaritytechtools/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/jackklika/solidaritytechtools/blob/python-coverage-comment-action-data/htmlcov/index.html)

An unofficial python library to help you automate solidarity tech (ST).

See the ST api page for more details: https://www.solidarity.tech/reference/

This is still in beta, and there is a bit more work to do. But you can still use this in production if you are bold, and I am safely using it on thousands of records.

## Features

The primary benefit of using a library like this is to create tooling around your existing ST universe beyond the existing Automations functionality.

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

Given a JSON ST contact export and a live ST account, you can find the best matches to link local data to live API users. This is extremely useful for migrating historical data (like notes) from one ST account to another.

```python
from solidaritytechtools import find_best_match

# Returns a mapping of {person_id: ClientUserMatch}
# Behind the scenes, this is using the `solidaritytechtools.client` and `solidaritytechtools.json_export`
matches = find_best_match(
    json_export_file="old_account_export.json",
    api_key="new_account_api_key"
)

for person_id, match in matches.items():
    if match:
        print(f"Export Person {person_id} -> API User {match.user_id} ({match.confidence*100}% confidence)")
```

Current heuristics use email and phone for high-confidence matching, and name + zip code for lower-confidence fuzzy matching. **Please look through the code before using this in production to understand what it's doing.**

### Email Matching & Bulk User Operations

Common operations like lookups or updating users require individual API calls per operation, which hits ST rate limits. There are limited batch endpoints.

You can load every user once into a cached `UserStore` for fast local lookups and bulk updates, avoiding one API call per user (and the rate limits that come with it).

```python
from solidaritytechtools import STClient, UserStore, find_matches_emails, set_email_permission

# Map a list of emails -> ST user ids (optionally ignoring "+subaddressing")
matches = find_matches_emails(["a@example.com", "b+promo@example.com"], api_key="...", strip_subaddress=True)

# Or build a reusable, file-cached store and query it locally
store = UserStore.from_api(api_key="...")
user = store.match_email("a@example.com")

# Bulk-set a permission across many users
with STClient(api_key="...") as client:
    set_email_permission(client, matches.values(), permission=False)
```



### Traffic Scoring (yard-sign prioritization) (Currently WI only)

Score contacts by how much traffic passes their home and optionally write the score to a custom user property. You can then then create sorted lists in ST to prioritize who to call to make sure yard signs get the most views.

t includes some logic where freeways are excluded so homes snap to the nearest sign-visible surface street. Supports dry runs and a Members-in-Good-Standing filter.

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

## Using

1. Add `solidaritytechtools` as a dependency via `uv add solidaritytechtools`, `pip install solidaritytechtools`, etc
1. Import the client, models, or functions, like `from solidaritytechtools import STClient, models, find_best_match`

See the `/examples` directory for scripts demonstrating usage.

Using Pydantic models provides better type safety and IDE autocompletion, but you can always fall back to a `dict` if the API spec drifts or a model is missing a field.

If you notice client functions not working as expected, feel free to use raw internal methods like `client._get("path")` or `client._put("path", json=payload)` to do what you need, and then submit an issue or a MR.

## Contributing

1. Clone the repo 
2. Install pre-commit hooks (`uv run pre-commit install`) - If you don't, your changes will likely break CICD.
3. Start coding and make a MR :)

Please use `uv run ty check .` to check the type safety of your code before submitting a MR. 

## Publishing

The maintainer will probably take care of this

1. `uv version --bump patch` (or minor, major etc)
1. `uv sync`
1. `git add pyproject.toml uv.lock`
1. `git commit -m "Release $(uv version)" && git tag v$(uv version --short)`
1. `git push origin main --tags`

Github workflow will push to pypi.
