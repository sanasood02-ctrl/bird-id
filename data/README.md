# Data files

## avilist_species.csv

The official list of bird species used by the name check (`name_check.py`).

- **Source:** AviList v2025b (published 11 June 2026), short version,
  downloaded from https://www.avilist.org/checklist/v2025b/
  (file `AviList-v2025b-10Jun2026-short.xlsx`).
- **How it was made:** only the rows where `Taxon_rank` is `species` were kept
  (11,131 species; subspecies, genus, family and order rows were removed), and
  only two columns: `Scientific_name` (saved as `scientific_name`) and
  `English_name_AviList` (saved as `english_name`). Names were not changed,
  apart from removing extra spaces at the start or end.
- **Licence:** CC BY 4.0 (free to use with credit).
- **Citation:** AviList Core Team. 2026. AviList: The Global Avian Checklist,
  v2025b. https://doi.org/10.2173/avilist.v2025b
