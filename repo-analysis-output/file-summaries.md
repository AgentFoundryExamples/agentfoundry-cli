# File Summaries

Heuristic summaries of source files based on filenames, extensions, and paths.

Schema Version: 2.0

Total files: 8

## agentfoundry_cli/__init__.py
**Language:** Python  
**Role:** module-init  
**Role Justification:** module initialization file '__init__'  
**Size:** 1.19 KB  
**LOC:** 8  
**TODOs/FIXMEs:** 0  

## agentfoundry_cli/__main__.py
**Language:** Python  
**Role:** entry-point  
**Role Justification:** common entry point name '__main__'  
**Size:** 1.02 KB  
**LOC:** 6  
**TODOs/FIXMEs:** 0  

## agentfoundry_cli/cli.py
**Language:** Python  
**Role:** cli  
**Role Justification:** CLI-related name 'cli'  
**Size:** 4.90 KB  
**LOC:** 114  
**TODOs/FIXMEs:** 0  
**Declarations:** 5  
**Top-level declarations:**
  - function hello
  - function run
  - function help
  - function version
  - function main
**External Dependencies:**
  - **Stdlib:** `json`, `pathlib.Path`, `sys`, `typing.Optional`
  - **Third-party:** `typer`

## agentfoundry_cli/parser.py
**Language:** Python  
**Role:** implementation  
**Role Justification:** general implementation file (default classification)  
**Size:** 36.56 KB  
**LOC:** 744  
**TODOs/FIXMEs:** 0  
**Declarations:** 18  
**Top-level declarations:**
  - function _levenshtein_distance
  - function _find_closest_key
  - class TokenType
  - class Token
  - class AFParseError
  - class AFMissingKeyError
  - class AFDuplicateKeyError
  - class AFUnknownKeyError
  - class AFSyntaxError
  - class AFEmptyValueError
  - ... and 8 more
**External Dependencies:**
  - **Stdlib:** `dataclasses.dataclass`, `enum.Enum`, `enum.auto`, `io`, `pathlib.Path`
    _(and 7 more)_

## tests/__init__.py
**Language:** Python  
**Role:** test  
**Role Justification:** located in 'tests' directory  
**Size:** 0.92 KB  
**LOC:** 1  
**TODOs/FIXMEs:** 0  

## tests/test_cli.py
**Language:** Python  
**Role:** test  
**Role Justification:** filename starts with 'test_'  
**Size:** 3.89 KB  
**LOC:** 64  
**TODOs/FIXMEs:** 0  
**Declarations:** 10  
**Top-level declarations:**
  - function test_main_help_flag
  - function test_hello_command_default
  - function test_hello_command_with_name
  - function test_version_command
  - function test_version_format
  - function test_run_command_stub
  - function test_run_command_in_help
  - function test_help_command
  - function test_help_command_with_subcommand
  - function test_help_command_with_unknown_subcommand
**External Dependencies:**
  - **Stdlib:** `re`
  - **Third-party:** `typer.testing.CliRunner`

## tests/test_cli_run.py
**Language:** Python  
**Role:** test  
**Role Justification:** filename starts with 'test_'  
**Size:** 16.83 KB  
**LOC:** 328  
**TODOs/FIXMEs:** 0  
**Declarations:** 20  
**Top-level declarations:**
  - function test_run_command_with_valid_file
  - function test_run_command_with_example_file
  - function test_run_command_json_only_stdout
  - function test_run_command_with_missing_file
  - function test_run_command_with_directory
  - function test_run_command_with_wrong_extension
  - function test_run_command_with_missing_required_key
  - function test_run_command_with_duplicate_key
  - function test_run_command_with_syntax_error
  - function test_run_command_with_empty_list
  - ... and 10 more
**External Dependencies:**
  - **Stdlib:** `json`, `os`, `pathlib.Path`, `tempfile`
  - **Third-party:** `typer.testing.CliRunner`

## tests/test_parser.py
**Language:** Python  
**Role:** test  
**Role Justification:** filename starts with 'test_'  
**Size:** 49.46 KB  
**LOC:** 1308  
**TODOs/FIXMEs:** 0  
**Declarations:** 97  
**Top-level declarations:**
  - function test_parse_valid_file
  - function test_parse_valid_file_with_single_quotes
  - function test_parse_with_apostrophes
  - function test_parse_with_escaped_quotes
  - function test_case_insensitive_keys
  - function test_whitespace_tolerance
  - function test_empty_lines_and_comments
  - function test_missing_purpose_key
  - function test_missing_vision_key
  - function test_missing_must_key
  - ... and 87 more
**External Dependencies:**
  - **Stdlib:** `io`, `os`, `pathlib.Path`, `sys`, `tempfile`
  - **Third-party:** `pytest`
