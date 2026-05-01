# Demo Data Layout

This directory contains the structured assets needed to validate and demo the backend cleanly.

## Folders

- `sae_cases/`: sample SAE intake text files
- `labels/`: extracted ground-truth JSON for each sample
- `rules/`: machine-readable rule packs for validation and compliance logic

## Demo Highlights

- `sae_case_006_incomplete.txt` is intentionally missing critical fields for completeness checks.
- `sae_case_001_revised.txt` is a follow-up version of case 001 for comparison and change tracking demos.

## Recommended Use

- Use `sae_cases/*.txt` as upload inputs.
- Use `labels/*.json` as expected-output references during testing and judge walkthroughs.
- Use `rules/*.json` to drive completeness, anonymization, and category-specific validations.
