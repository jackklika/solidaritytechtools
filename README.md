# Solidarity Tech Tools

An unofficial python library to help you automate solidarity tech (ST).

See the ST api page for more details: https://www.solidarity.tech/reference/

This is still in beta, and there is a bit more work to do. But you can still use this in production if you are bold.

## Features

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

### JSON Export Tools

The library includes tools for validating and parsing Solidarity Tech JSON export files into structured models.

```python
from solidaritytechtools import get_persons_from_json_export

# Load and validate an export file
people = get_persons_from_json_export("export-members-data.json")

for person in people:
    print(f"{person.first_name} {person.last_name} has {len(person.notes)} notes")
```

### Contact Matching

Given a JSON contact export and a live ST account, you can find the best matches to link local data to live API users. This is extremely useful for migrating historical data (like notes) from one ST account to another.

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


## Using

1. Add `solidaritytechtools` as a dependency via `uv add solidaritytechtools`, `pip install solidaritytechtools`, etc
1. Import the client, models, or functions, like `from solidaritytechtools import STClient, models, find_best_match`

See the `/examples` directory for scripts demonstrating usage.

Using Pydantic models provides better type safety and IDE autocompletion, but you can always fall back to a `dict` if the API spec drifts or a model is missing a field.

If you notice client functions not working as expected, feel free to use raw internal methods like `client._get("path")` or `client._put("path", json=payload)` to do what you need, and then submit an issue or a MR.

## Contributing

1. Clone the repo 
2. Install pre-commit hooks (`uv run pre-commit install`)
3. Start coding and make a MR :)

Please use `uv run ty check .` to check the type safety of your code before submitting a MR. 
When possible, `ty check .` will be added to pre-commit hooks.

## Publishing

The maintainer will probably take care of this

1. `uv version --bump patch` (or minor, major etc)
1. `uv sync`
1. `git add pyproject.toml uv.lock`
1. `git commit -m "Release $(uv version)" && git tag v$(uv version --short)`
1. `git push origin main --tags`

Github workflow will push to pypi.
