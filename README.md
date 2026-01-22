# Solidarity Tech Tools

An unofficial python library to help you automate solidarity tech (ST).

See the ST api page for more details: https://www.solidarity.tech/reference/

This is still in beta, and there is a bit more work to do. But you can still use this in production if you are bold.

## Features

### Client  
Call python methods to interact with the ST api. You can pass pydantic models and receive pydantic models in return, so you can rely on the response structure.

## Todo: Contact Matching
Given a contact export and a ST account with contacts, attempt to match the two, so you can perform operations.

This is useful for example if you want to export migrate resources from one ST account to another, like notes or custom properties.

## Using

1. Add `solidaritytechtools` as a dependency via `uv add solidaritytechtools`, `pip install solidaritytechtools`, etc
1. Import the client and models: `from solidaritytechtools import STClient, models`
1. Use the client as a context manager:

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