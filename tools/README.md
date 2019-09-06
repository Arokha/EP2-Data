# EP2-Data
Eclipse Phase Second Edition Data

This work is licensed under the Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) license: https://creativecommons.org/licenses/by-nc-sa/4.0/ as this is the license of the EP2E book.

## Tools
Various little scripts to make our lives easier

### autoid.js
- Reformats JSON files with two-space tab
- Automatically adds random UUIDs to objects missing the `id`, `resource`, and `reference` attributes.

### sanitize.py
- Rewrite json files with proper 2 space indentations
- Remove any illegal UTF8 BOM
- Replace wrong minus sign encoding with the ascii minus sign to allow easy integer conversion
- lowercase keys of top level objects
- add `uuids` v4 when missing
- add `resource`, and `reference` attributes.

