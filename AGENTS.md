This is a toolset for Solidarity Tech. It has a client, and may include other utilities over time. Read the `README.md` file for the most up-to-date information.

# Rules
- If the user is attempting to contribute code, ensure you and they follow the "Contributing" section in the `README.md`
- Be very cautious that we do not include **any** PII in this repo. If you are working with data sources, make sure no real names, 
  phone numbers, email address, or any personal information is included in comments, tests, or code. 
- Do not commit any data sources which contain PII. There is a .gitignore rule that requires whitelisting of csv, pdf, etc 
  files that may be data sources, and this is to help avoid this issue.
- Ensure that we maintain compatibility with the python version specified by `requires-python` in `pyproject.toml`. A goal
  is to make sure that both old and new python projects can use this library.
- Ensure that we do not break compatibility between minor versions. We may have users that are pinned to our minor version, and 
  we wouldn't want their code to break if functions/constants move or new arguments become required, etc. 
  Try to respect backwards compatibility for imports and functions, and prefer to alias and emit a `DeprecationWarning`
  like `warnings.warn("old_name() is deprecated; use new_name() instead. ", DeprecationWarning)`
- Keep the library's own dependencies to `httpx` and `pydantic`. Anything heavy like pandas or pyarrow belongs in an
  optional extra (see `analysis`), and scripts in `/examples` that need it should guard the import with a message
  saying how to install it. `tests/` and `examples/` are excluded from `ty`, so a plain `uv sync` is enough to run
  every check that CI runs.
- When changing or implementing any contact matching, prefer to use or extend the `ContactIndex` instead of doing your own thing.

# Code Style
- Do not over-comment, only comment when it makes something more clear that may be confusing or not immediately obvious

```python
# Code style examples:

# Use `Type | None` instead of `Optional[Type]`, and `foo: list` instead of `foo: typing.List` for example
foo: typing.List[int | None] = [1, 2, 3, None] # no
foo: list[int | None] = [1, 2, 3, None] # yes

# Prefer `| None` to `typing.Optional` and `|` to `typing.Union`
foo: Optional[str] # no
foo: Union[str, None] # no
foo: str | None # yes
foo: Union[int, str] # no
foo: int | str # yes

# Use type hints except where immediately obvious. Always use type hints in function params and return types.
# Especially use type hints for dicts and lists, such as `dict[str, Foo | None]` or `list[str]`.
foo_dict: dict = {"1": 1, "2": 2, "a": None} # no
foo_dict: dict[str, int | None] = {"1": 1, "2": 2, "a": None} # yes

def foo(a, b, c): # no: function params and return type should ALWAYS be typed, even if verbose.
   return a+b+c

def foo(a: int, b: int, c: int) -> int: # yes -- explicit typed params and return types
   return a+b+c


# Prefer to put constants at the top of the file like `DEFAULT_TASK_QUEUE: Final[str] = "default"`
def add_to_queue(item: Any) -> None: # no
    foo.add_to_queue(queue="default", item=item)

DEFAULT_TASK_QUEUE: Final[str] = "default"
def add_to_queue(item: Any, *, task_queue: str = DEFAULT_TASK_QUEUE) -> None: # yes
    foo.add_to_queue(queue=task_queue, item=item)

```
