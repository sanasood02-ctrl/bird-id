# Score history

One row per change, from the 100-row test list. "Worst errors" means Wrong +
Guessed: the app confidently misleading the user.

| Run | Date | What changed | Accuracy | Confident | Possible | Not enough | Worst errors | Results file |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-10-20 | Starting point | 83% ± 7% | 47 of 50 | 11 of 25 | 25 of 25 | 7 | `results_real_2026-10-20_2014.csv` |
| 2 | 2026-11-09 | Added RAG (seven species, word matching, best two records) | 77% ± 8% | 46 of 50 | 6 of 25 | 25 of 25 | 6 | `results_real_2026-11-09_0058.csv` |
| 3 | 2026-11-09 | Step 18b: three worked examples and the field notes added to Haiku's instructions | 81% ± 8% | 46 of 50 | 10 of 25 | 25 of 25 | 4 | `results_real_2026-11-09_0120.csv` |
| 4 | 2026-11-09 | Step 18c: two new rules for choosing "possible" | 81% ± 8% | 45 of 50 | 11 of 25 | 25 of 25 | 4 | `results_real_2026-11-09_0129.csv` |
| 5 | 2026-11-09 | Switched from Claude Haiku 4.5 to Claude Haiku 5.5 | 76% ± 8% | 38 of 50 | 13 of 25 | 25 of 25 | 3 | `results_real_2026-11-09_0208.csv` |
| 6 | 2026-11-09 | Adjusted the instructions for Haiku 5.5's caution | 79 of 100 right (81% ± 8% of the 98 rows that got an answer) | 43 of 49 | 11 of 24 | 25 of 25 | 1 | `results_real_2026-11-09_0218.csv` |

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

### Run 4: Step 18c (two new rules for "possible")

- The two rules: answer "possible" if a look-alike has not been ruled out by
  something the user wrote, and use "not enough data" only when more than 3
  species remain.
- Accuracy did not change. 8 rows changed verdict: 4 got better (26, 52, 53,
  54) and 4 got worse (8, 41, 67, 68), which cancelled out.
- On "possible" rows, the app said "confident" 7 times (8 in run 3) and "not
  enough data" 6 times (6 in run 3). The rules barely moved either problem.
- Some rows flip between runs after small wording changes. Row 41 (Kakapo) was
  right, wrong, right, wrong across the four runs. Row 26 (Australian Magpie)
  was right, wrong, wrong, right. Differences of a few points between runs
  should not be over-read.

### Run 5: Claude Haiku 5.5

- Accuracy fell by 5 points from run 4, but the margins of error overlap.
- The new model is much more cautious. "Too cautious" rose from 8 rows to 20,
  and "Lucky (overconfident)" fell from 7 rows to 1.
- No row named a wrong bird. All 3 Wrong verdicts (rows 14, 23, 29) were
  "confident" answers with an empty species list. In each one, the written
  reasoning had picked the right bird. If those 3 had named it, the score
  would have been 79%.
- The app would have crashed on an empty list, so a check was added that shows
  a friendly error instead. The check was added after this run.
- This model does not accept the temperature setting, so the same description
  can get different answers on different runs.

### Run 6: instructions adjusted for Haiku 5.5

- Four changes made together: a sentence requiring species to be listed;
  removing "not_enough over possible"; removing the first Step 18c rule; and a
  new rule to count only realistic look-alikes for the location and season.
- 79 of 100 rows were right, up from 76 in run 5. The script reports 81%
  because it leaves out the 2 rows that got an error instead of an answer.
  Counting those as misses, 79% is the fair comparison with earlier runs.
- Worst errors fell to 1, the lowest of all runs. Row 11 (Common Myna) was
  answered as Yellow-wattled Lapwing, and that row is handed the Red-wattled
  Lapwing field record, so RAG may have pulled it towards a lapwing.
- Empty species lists stopped appearing as Wrong, but 2 rows (5 and 65) hit the
  friendly error message. The same message covers several causes, so these may
  or may not be empty lists.
- Confident rows improved. "Too cautious" on confident rows fell from 9 to 5.
- The "possible" rows did not improve: 13 of them were answered "not enough
  data" (11 in run 5). This is the largest remaining problem.
