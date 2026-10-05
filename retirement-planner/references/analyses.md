# The Ten Analyses

Read the section for each analysis you're running. Each one lists the inputs it needs, how to run it, and what to show the person.

## Contents
- Intake checklist
- Default return assumptions by allocation
- 1. Retirement timeline
- 2. Monte Carlo
- 3. Social Security / pension claiming
- 4. Tax-efficient withdrawals
- 5. Healthcare costs
- 6. Inflation stress test
- 7. Part-time / semi-retirement
- 8. Asset allocation
- 9. Retirement budget
- 10. Reverse retirement plan

---

## Intake checklist

Ask only for what the chosen analyses need. Group the questions and ask them once.

**Core (needed for nearly everything):** current age, target retirement age (or "as early as possible"), total invested savings, annual savings contributions, expected annual spending in retirement (or current spending), Social Security or pension estimate and start age.

**Often useful:** split of savings across taxable, traditional (401k/IRA) and Roth accounts. Rough stock/bond mix. Spouse's age and benefits. Home equity and mortgage payoff date. Expected big one-time costs or windfalls (college, inheritance, home sale). State of residence. Health or longevity considerations.

If they only know current spending, a common starting point is 80–100% of pre-retirement spending, minus savings contributions and work costs, plus healthcare. Say this is an estimate and offer Analysis 9 to refine it.

## Default return assumptions by allocation

These are illustrative long-run nominal planning figures, not forecasts. Use them when the person has no view of their own, and say they're assumptions.

| Allocation | Stocks / bonds | `expected_return` | `return_stdev` |
|---|---|---|---|
| Conservative | 30 / 70 | 0.045 | 0.07 |
| Balanced | 60 / 40 | 0.06 | 0.10 |
| Growth | 75 / 25 | 0.065 | 0.13 |
| Aggressive | 90 / 10 | 0.075 | 0.15 |
| Cash-like | 0 / 0 (T-bills) | 0.03 | 0.01 |

---

## 1. Retirement timeline

**Question:** What's the earliest realistic age I can retire, and what would make it earlier?

**Run:**
- `solve --for retire_age` (85% target). Also try 75% and 95% to show the range from "aggressive" to "very safe".
- `project` at that age with `--table` to show the year-by-year path.
- Levers: `compare` with scenarios that save more (+$10k/yr), spend less (−10%), or work part-time for a few years. Then re-solve to show how many years each lever buys.

**Show:** earliest age at 75% / 85% / 95% confidence, a compact milestone table (retirement, Social Security start, Medicare at 65, age 80, age 95), and the lever ranking in years gained.

## 2. Monte Carlo

**Question:** What's the probability my portfolio lasts until age X?

**Run:** `montecarlo` with 5,000+ runs. If they want strong and weak scenarios, report the p5/p25/p50/p75/p95 ending balances in today's dollars, plus the median depletion age among failed runs.

**Show:** success probability, the percentile table, and a plain-English reading: "in the worst 1 in 20 markets, money runs out around 84; in a typical market you leave about $X". Explain sequence risk briefly. Bad returns in the first five years of retirement do outsized damage, which is why a flexible spending plan or a cash buffer matters.

Calibrate the language: ≥90% means very likely sustainable, possibly oversaving. 75–90% is reasonable if they can trim spending in bad years. Below 75% means fragile, so show the levers.

## 3. Social Security / pension claiming

**Question:** When should I claim, and how does that affect lifetime income, taxes and portfolio withdrawals?

**Inputs:** benefit estimate at full retirement age (from ssa.gov/myaccount), birth year, spouse's details, health/longevity outlook, pension options (lump sum vs annuity, survivor percentage).

**Run:** `compare` with one scenario per claiming age (for example 62, 67, 70). Adjust both `start_age` and `annual` using the adjustment factors in `references/us-rules.md`. Also compute cumulative lifetime benefits by age to find the break-even age. A small inline Python calculation is fine for that.

**Show:** a table with claiming age, annual benefit (today's $), break-even age vs claiming at 62, portfolio success %, and median ending balance. For couples, point out that the higher earner's delay also raises the survivor benefit. That is often the deciding factor.

Pensions: compare the lump sum with the annuity by treating the annuity as an `income_streams` entry (`inflation_adjusted: false` if it has no COLA) against adding the lump sum to `portfolio`.

## 4. Tax-efficient withdrawals

**Question:** Which account should I draw from first, and why?

This is mostly reasoning, not simulation. Read `references/us-rules.md`. Then:
- Lay out the "gap years" between retirement and Social Security/RMDs. Low-income years are the chance to fill low tax brackets with traditional withdrawals or Roth conversions.
- Give an ordered plan by life phase (for example: ages 60–66 use taxable plus partial Roth conversions up to the top of a chosen bracket; ages 67–74 add Social Security and draw traditional; age 75+ take RMDs first, Roth last and for legacy).
- Flag interactions: ACA subsidy cliffs pre-65 (MAGI), Medicare IRMAA surcharges (based on income two years earlier), taxation of Social Security, the 0% long-term capital gains bracket, and the widow(er)'s tax penalty when one spouse dies and filing status changes.
- Look up the current year's bracket thresholds rather than relying on memory, or state which year's figures you're using.

**Show:** a phase-by-phase table (ages, source of spending, conversions, rough marginal bracket) and the reasoning in a few bullets. If balances are large, run `compare` with different `withdrawal_tax_rate` values to show what better sequencing is worth.

## 5. Healthcare costs

**Question:** How will healthcare affect my plan from age X to Y?

**Run:** add `expenses` entries with their own `inflation`:
- Pre-65 coverage (if retiring early): ACA marketplace or COBRA premiums plus out-of-pocket costs, from retirement to 65. Unsubsidized premiums can be substantial, so ask for a quote or state a rough per-person figure as an assumption.
- 65+: Medicare Part B/D premiums, a Medigap or Advantage plan, and out-of-pocket costs.
- Optional late-life long-term care: a lump or multi-year cost starting in the mid-80s.

Then `compare` with healthcare inflation at 4%, 5.5% and 7%.

**Show:** annual healthcare cost at key ages (today's $), the success % under each healthcare inflation scenario, and the extra savings needed to restore the target. Get that with `solve --for portfolio` under the high-cost scenario, minus their current portfolio.

## 6. Inflation stress test

**Question:** How do prolonged 2/4/6/8% inflation scenarios change purchasing power and portfolio longevity?

**Run:** `compare` with `inflation` overrides of 0.02, 0.04, 0.06 and 0.08. High inflation rarely comes alone. For the 6% and 8% cases, also try a version where `expected_return` rises partially (say +2 points) to reflect higher nominal yields, and show both. Remember non-COLA pensions (`inflation_adjusted: false`) lose real value quickly in these scenarios.

**Show:** a table with inflation rate, success %, depletion age (deterministic), median ending real balance, and what $1 of today's spending costs in nominal dollars at 75 and 90. Name the inflation hedges relevant to them (Social Security COLA, TIPS/I-bonds, equities over long periods, a fixed-rate mortgage).

## 7. Part-time / semi-retirement

**Question:** If I stop full-time work at age A and earn $X/yr part-time for N years, how does that change things?

**Run:** add an `income_streams` entry `{start_age: A, end_age: A+N, annual: X}`, set `retire_age: A`, and stop contributions. `compare` against full retirement at A and at the later full-time date. Also `solve --for portfolio` in each case to show how much the required nest egg drops.

**Show:** required savings with and without part-time income, success % for each, and the "bridge" effect. Even modest income in the first five to ten years cuts sequence risk sharply, because it shrinks withdrawals when the portfolio is most vulnerable.

## 8. Asset allocation

**Question:** Compare conservative, balanced and aggressive allocations for my timeline and risk tolerance.

**Run:** `compare` with the allocation presets above (override `expected_return` and `return_stdev`). Optionally add a glide path, approximated by running the aggressive preset pre-retirement and the balanced preset in retirement as two separate runs and explaining the blend.

**Show:** a table with allocation, success %, p5 (bad case) and p50 ending balances. Explain the trade-off honestly: more stocks usually raise the median and the success rate over long horizons but widen the bad tail and make drawdowns harder to live with. The right allocation is the one they won't abandon in a 30–40% crash. Don't recommend specific funds or securities.

## 9. Retirement budget

**Question:** Build a realistic retirement budget from current expenses.

**Steps:** take current spending by category (ask for a rough breakdown, or offer typical shares) and adjust each category for retirement:
- **Essential:** housing (does the mortgage end?), utilities, food, insurance, transportation, taxes.
- **Discretionary:** dining, hobbies, gifts.
- **Healthcare:** see Analysis 5. It usually rises.
- **Travel:** often front-loaded in early retirement.
- **Housing:** maintenance at about 1–2% of home value per year, and possible downsizing.
- **Unexpected:** a 5–10% buffer for cars, roofs and family support.

Spending usually follows a "go-go / slow-go / no-go" shape. Model it with `spending_changes` (for example −10% at 75 and −10% at 85, while healthcare rises separately).

**Show:** a category table with current $, retirement $ (today's), and essential/discretionary flag. Then total annual income needed, the gap after Social Security/pension, and the portfolio withdrawal rate that implies. Feed the result into Analysis 1 or 2.

## 10. Reverse retirement plan

**Question:** I want to retire at age A, spend $S/yr in today's dollars, and have money last to age X. What do I need?

**Run (each one with `retire_age: A`, `annual_spending: S`, `end_age: X`):**
- `solve --for portfolio` with `current_age` set to A and `annual_contribution` 0, which gives the nest egg needed at retirement (nominal at that point, so also convert to today's dollars).
- `solve --for annual_contribution` from their actual current situation, which gives the required yearly savings.
- `solve --for expected_return` with current contributions, which gives the return needed. If the required return is above about 8%, say plainly that it relies on taking more risk than is usually prudent, and show the other levers instead.

**Show:** the three targets side by side, a sanity check against the 4% rule (S minus guaranteed income, divided by 0.04), and the combination of levers that closes the gap realistically (for example: save $8k more per year, retire one year later, and trim spending 5%).
