# varfinder
*Local variant annotation and interpretation search for pathologists*

## How to use:
- Install all requirements in a local python environment with pip.
- Create a CSV with variant annotations listed per line which should contain the following columns:
  - chr: chromosome (free text)
  - pos: genomic coordinate (int)
  - ref: reference annotation (free text)
  - alt: variant annotation (free text)
  - classification: One of the following: "Not set", "Pathogenic", "Likely Pathogenic"
  - somatic: One of the following: "Not set", "Somatic", "Not Confirmed Somatic", "Germline", "Artifact"
  - curation: Free text of the variant interpretation
  - enterDate: The date that the variant was entered, in YYYY-MM-DD HH:MM:SS format (e.g. 2023-06-21 11:29:01)
- Load this file into the window that appears, and search for something
