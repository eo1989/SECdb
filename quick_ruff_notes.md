# Ruff Notes

## Docstring rules

like black, ruff supports "\# fmt: on|off|skip" pragma comments

- ie:

    ```python
    # fmt: off
    not_formatted=3
    also_not_formatted=4
    # fmt: on
    ```

- below is incorrect

    ```python
    [
        # fmt: off
        1,
        # fmt: on
        2,
    ]
    ```

- do this instead

    ```python
    # fmt: off
    [
        1,
        2,
    ]
    # fmt: on
    ```

- "fmt: skip" ex

    ```python
    if True:
        pass
    elif False: # fmt: skip
        pass

    @Test
    @Test2 # fmt: skip
    def test(): ...

    a = [1, 2, 3, 4, 5] # fmt: skip

    def test(a, b, c, d, e, f) -> int: # fmt: skip
        pass
    ```

- This is wrong

    ```python
    a = call(
        [
            '1',  # fmt: skip
            '2',
        ],
        b
    )
    ```

- Do this instead

    ```python
    a = call(
        [
            '1',
            '2',
        ],
        b
    ) # fmt: skip
    ```
