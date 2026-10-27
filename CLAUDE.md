# CI review and test standards

The project lives in `kafka_cluster_namer/` (package `kafka_namer`, Python >= 3.10, source in `src/kafka_namer/`).
All paths below are relative to the repository root, which is also the path format findings must use.

## Testing standards

- Framework: pytest (`pytest>=8.0`, installed with `pip install -e ".[dev]"`). Run with `cd kafka_cluster_namer && pytest`.
- Layout: one `tests/test_<module>.py` per module under `src/kafka_namer/` (`test_generator.py`, `test_cli.py`). Plain functions, no test classes.
- Naming: `test_<behaviour>`, describing the expected outcome (`test_zero_count_is_an_error`), not the function under test.
- A good test here:
  - Asserts something observable. A test that only calls code or `print`s its result is not a test: it cannot fail.
  - Is deterministic. Pass `random.Random(seed)` to the generator functions or `--seed` to the CLI. Never depend on unseeded randomness for the assertion.
  - Covers the failure path as well as the happy path. Every validator or error branch needs at least one invalid input that must be rejected, and one valid input that must be accepted. A validator tested only with valid input is untested.
  - Uses `pytest.raises(ValueError, match="...")` and checks the message, not just the exception type.
  - Uses `@pytest.mark.parametrize` for several inputs to the same rule, not a loop inside one test.
  - Checks CLI behaviour through `main([...])`: assert the exit code (0 success, 1 generation error, 2 usage error), then `capsys` for stdout and stderr.
  - Checks boundaries: count 1 and the maximum, an empty prefix, a name just under and just over `MAX_NAME_LENGTH`.
- A bug fix comes with a regression test that fails without the fix.
- Tests must not touch the real filesystem outside pytest's `tmp_path`, and must not depend on test order or on state left by another test (for example a shared mutable `exclude` list).

## Fixtures and test data

Use what exists; do not invent word lists or data files.

- Word lists: `kafka_cluster_namer/src/kafka_namer/words.py` (`ADJECTIVES`, `NOUNS`). Import them to build expectations, for example the total number of combinations is `len(ADJECTIVES) * len(NOUNS)`.
- Existing tests to extend rather than duplicate: `kafka_cluster_namer/tests/test_generator.py`, `kafka_cluster_namer/tests/test_cli.py`.
- Built-in pytest fixtures: `capsys` for CLI output, `tmp_path` for `--exclude-file` and `--audit-log` files (write the content in the test, one name per line).
- There is no `fixtures/` or `conftest.py` yet. If a test needs shared data, add it in `kafka_cluster_namer/tests/conftest.py` and mention it in the PR, rather than creating ad hoc files.

## Review severity criteria

Report each finding with exactly one of the three severities the output schema allows.
Judge by impact on the code as changed, not by how the code looks.

- `critical`: must be fixed before merge.
  - Security flaws a user input can trigger: command or shell injection, path traversal, writing to arbitrary files, secrets in code or logs.
  - Data loss or corruption.
  - A crash or hang on the main code path.
- `major`: a real defect, but not a security hole.
  - Wrong results in normal use, such as a validator that accepts invalid input or an exclude list that never matches.
  - Errors swallowed so the program continues in a wrong state (`except Exception: return []`).
  - Possible infinite loops, shared mutable default arguments, mutating caller-owned data.
  - Missing handling of an error the CLI can reasonably hit.
  - A change to behaviour with no test, or tests that would not catch the bug being fixed.
- `minor`: should be improved, would not cause a failure on its own.
  - Tests that cannot fail (no assertion, only `print`), or a validator test with no invalid cases, when this does not hide a `major` or `critical` bug. If it does hide one, mention it in that finding instead.
  - Naming, structure, comments or docstrings that are wrong or misleading, duplicated code.
  - Style issues that a formatter or linter would not already catch.

When unsure between two levels, pick the lower one and say what would make it higher.
Do not report: formatting a linter handles, personal preferences, or code that the diff did not touch unless the diff makes it wrong.

## How to report

- One finding per distinct problem. Do not repeat the same root cause on several lines; point at the line where the fix goes and mention the others in the message.
- `file` is the path from the repository root. `line` is the line number in the new version of the file.
- `message` says what is wrong, why it matters, and the fix, in a few sentences.
- No findings is a valid result: return an empty list.
