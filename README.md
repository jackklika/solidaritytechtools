# Solidarity Tech Tools

A python library to help you automate solidarity tech (ST).

This is still in beta, and there is a bit more work to do. But you can still use this in production if you are bold.

## Features

### Client  
Call python methods to interact with the ST api. You can pass pydantic models and receive pydantic models in return, so you can rely on the response structure.

## Todo: Contact Matching
Given a contact export and a ST account with contacts, attempt to match the two, so you can perform operations.

This is useful for example if you want to export migrate resources from one ST account to another.

## Using

1. Add `solidaritytechtools` as a dependency via `uv add solidaritytechtools`, `pip install solidaritytechtools`, etc
1. Import stuff from here, like `from solidaritytechtools import STClient`
1. Initialize the client with the api key: `st_client = STClient(api_key="...")`
1. Perform calls, like `st_client.get_users()`

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
