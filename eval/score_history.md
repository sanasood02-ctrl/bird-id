# Score history

One row per change, from the 100-row test list. "Worst errors" means Wrong +
Guessed: the app confidently misleading the user.

| Run | Date | What changed | Accuracy | Confident | Possible | Not enough | Worst errors | Results file |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-10-20 | Starting point | 83% ± 7% | 47 of 50 | 11 of 25 | 25 of 25 | 7 | `results_real_2026-10-20_2014.csv` |
| 2 | 2026-11-09 | Added RAG (seven species, word matching, best two records) | 77% ± 8% | 46 of 50 | 6 of 25 | 25 of 25 | 6 | `results_real_2026-11-09_0058.csv` |
| 3 | 2026-11-09 | Step 18b: three worked examples and the field notes added to Haiku's instructions | 81% ± 8% | 46 of 50 | 10 of 25 | 25 of 25 | 4 | `results_real_2026-11-09_0120.csv` |

## Notes on each change

### Run 2: RAG

- Accuracy went down by 6 points. The margins of error overlap, so this could
  partly be ordinary variation.
- The biggest change was in the "possible" rows: the app answered "confident"
  on 12 of them, up from 5 in the starting run. Most of these named the right
  bird, but with too much certainty.
- 49 rows matched no record, so Haiku received the same description as before.
  Only its instructions had changed, yet these rows went from 38 right to 34.
  That drop comes from the new paragraph in the instructions or from ordinary
  variation, not from the records themselves.
- 51 rows matched at least one record, and went from 45 right to 43. Most of
  those records were for an unrelated bird.
- Rows 26 (Australian Magpie) and 41 (Kakapo) became Wrong after being handed
  unrelated records.
- Only two of the seven species are in the test list (Red-vented Bulbul and
  Indian Peafowl, four rows). Rows 12, 23 and 80 kept their right answers.
  Row 58 (bulbul) went from a wrong species to the right species, but was
  overconfident.
- Word matching and two embedding models were compared on the test
  descriptions before this run. Neither method could reliably separate
  matching records from unrelated ones, because bird descriptions all use
  similar words. Embeddings were not used.

### Run 3: Step 18b (worked examples and field notes)

- Accuracy rose by 4 points from run 2, and is 2 points below the starting
  point. The margins of error overlap across all three runs.
- Worst errors fell to 4, the lowest so far (7 at the start, 6 in run 2).
- On "possible" rows, the app said "confident" 8 times, down from 12 in run 2
  (5 at the start). The cautious worked example was aimed at this.
- 6 "possible" rows were answered "not enough data" (6 in run 2 as well).
- Rows that matched a field record: 88% right, up from 84% in run 2.
- Row 41 (Kakapo) became right again. Row 26 (Australian Magpie) stayed Wrong.
  Row 17 (Spoon-billed Sandpiper) went back to Wrong, this time as Black
  Spoonbill.
