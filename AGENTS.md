This is a toolset for Solidarity Tech. It has a client, and may include other utilities over time.

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
