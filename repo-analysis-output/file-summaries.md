# File Summaries

Heuristic summaries of source files based on filenames, extensions, and paths.

Schema Version: 2.0

Total files: 7

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
**Size:** 2.51 KB  
**LOC:** 55  
**TODOs/FIXMEs:** 0  
**Declarations:** 4  
**Top-level declarations:**
  - function hello
  - function run
  - function version
  - function main
**External Dependencies:**
  - **Stdlib:** `typing.Optional`
  - **Third-party:** `typer`

## agentfoundry_cli/parser.py
**Language:** Python  
**Role:** implementation  
**Role Justification:** general implementation file (default classification)  
**Size:** 14.60 KB  
**LOC:** 345  
**TODOs/FIXMEs:** 0  
**Declarations:** 12  
**Top-level declarations:**
  - class AFParseError
  - class AFMissingKeyError
  - class AFDuplicateKeyError
  - class AFUnknownKeyError
  - class AFSyntaxError
  - class AFEmptyValueError
  - function _strip_utf8_bom
  - function _tokenize_line
  - function _parse_quoted_string
  - function _parse_list
  - ... and 2 more
**External Dependencies:**
  - **Stdlib:** `pathlib.Path`, `re`, `typing.Any`, `typing.Dict`, `typing.List`
    _(and 1 more)_

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
**Size:** 2.82 KB  
**LOC:** 46  
**TODOs/FIXMEs:** 0  
**Declarations:** 7  
**Top-level declarations:**
  - function test_help_command
  - function test_hello_command_default
  - function test_hello_command_with_name
  - function test_version_command
  - function test_version_format
  - function test_run_command_stub
  - function test_run_command_in_help
**External Dependencies:**
  - **Stdlib:** `re`
  - **Third-party:** `typer.testing.CliRunner`

## tests/test_parser.py
**Language:** Python  
**Role:** test  
**Role Justification:** filename starts with 'test_'  
**Size:** 21.48 KB  
**LOC:** 576  
**TODOs/FIXMEs:** 0  
**Declarations:** 46  
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
  - ... and 36 more
**External Dependencies:**
  - **Stdlib:** `os`, `pathlib.Path`, `tempfile`
  - **Third-party:** `pytest`
