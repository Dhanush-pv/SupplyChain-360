# Synthetic sample data

**Everything in this folder is SYNTHETIC** (invented values, generated deterministically by
`scripts/generate_sample_data.py`, seed 42). Column names mirror the public M5, DataCo and Olist files so the
pipeline can be demonstrated and tested without downloading the real datasets. These files are not real
data and must not be used for analysis or presented as such.

Regenerate with `make sample`. A unit test fails if the committed files drift from the generator.
