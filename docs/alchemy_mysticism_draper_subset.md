# Alchemy & Mysticism → Draper Subset

## Summary

This change captures the integration of `Alchemy & Mysticism — Taschen (2003)` into the Draper research and app pipeline.

### App update
- Updated `draper_sphere_v2.html` to include Alchemy & Mysticism-informed features:
  - 28 lunar mansions (Picatrix/Agrippa style) with talisman and operation descriptions
  - Kircher planetary-organ correspondences in the reading tab
  - Bruno combinatory disk visualization for zodiac decans and lunar mansion alignment
  - Yeats Great Wheel quadrant reading for lunar phase / spiritual orientation
  - Picatrix-style talisman guidance based on planetary dignity and lunar mansion nature
  - Angelic correspondences, planetary hours, and Renaissance cipher context

### Pipeline update
- Extended `scripts/pipeline.py` with a new `subset` command:
  - `python scripts/pipeline.py subset --source alchemy_mysticism`
- Added `stage_draper_subset()` to export Draper-relevant distilled entities to CSV.
- Added `is_draper_relevant_entity()` to filter by:
  - relevant entity types (`lunar_mansion`, `organ_correspondence`, `talisman`, `seal`, `bruno_disk`, etc.)
  - Draper-related keywords in `name`, `description`, and `type`
- Output is written to `data/distilled/alchemy_mysticism_draper_subset.csv`.

## Generated output
- `data/distilled/alchemy_mysticism_draper_subset.csv`

## How to use
1. Run aggregate for the source if not already generated:
   ```bash
   python scripts/pipeline.py aggregate --source alchemy_mysticism
   ```
2. Export the Draper subset:
   ```bash
   python scripts/pipeline.py subset --source alchemy_mysticism
   ```

## Notes
- The subset file preserves the entity metadata fields: `name`, `type`, `description`, `source_ref`, `source_id`, `chunk_id`, and serialized `attributes`.
- This document is intentionally focused on the new pipeline export and the Draper app enhancements derived from the same source.
