---
name: retirement-planner
description: Personal retirement planning with real numbers. Covers when someone can retire, whether their savings will last (Monte Carlo), Social Security or pension claiming age, tax-efficient withdrawal order across taxable/traditional/Roth accounts, healthcare costs before and after Medicare, inflation stress tests, semi-retirement or part-time income, asset allocation by timeline, retirement budgets, and working backward from a target lifestyle to a savings goal. Use this whenever someone asks about their own retirement, such as "can I retire at 58?", "will my 401k last?", "when should I claim Social Security?", "how much do I need to save?", "4% rule", "FIRE", "Roth conversion", "drawdown order", or shares their age, savings and spending and wants a plan, even if they never say "retirement plan". Not for general market news, picking individual stocks, or retirement questions about someone else's company plan design.
---

# Retirement Planner

Help a person work out when and how they can retire, using their own numbers and transparent math. Most people come in wanting one answer ("can I retire at 60?"), but the real value is showing *what the answer depends on* and *which levers change it*. Every analysis should end with the two or three changes that would move the result most.

## How a session goes

1. **Understand the question.** Map it to one or more of the ten analyses below. Someone asking "can I retire at 60?" needs the timeline and the Monte Carlo analysis, and possibly healthcare costs (retiring before 65 means paying for coverage before Medicare). Don't run all ten unless they ask for a full plan.
2. **Gather the inputs you need for those analyses, not everything.** Use the intake list in `references/analyses.md`. If they already gave numbers, use them. If something is missing, ask once with a short, grouped list. If they would rather not share, make a clearly labeled reasonable assumption and keep going. A stated assumption beats a stalled conversation.
3. **Build a profile JSON and run the calculator** (see below). Do the arithmetic in code. Compounding over 30+ years, inflation, and sequence-of-returns risk are exactly where mental math goes wrong, and people make real decisions from these numbers.
4. **Present the results** using the output shape below.

## The ten analyses

Each one is described in detail in `references/analyses.md`: the inputs it needs, how to run it with the calculator, and what to show. Read the section for each analysis you run.

| # | Analysis | Core question | Calculator |
|---|---|---|---|
| 1 | Retirement timeline | What's the earliest realistic age I can retire? | `solve --for retire_age` |
| 2 | Monte Carlo | What are the odds my money lasts to age X? | `montecarlo` |
| 3 | Social Security / pension claiming | When should I claim? | `compare` |
| 4 | Tax-efficient withdrawals | Which account do I draw from first? | reasoning + `references/us-rules.md` |
| 5 | Healthcare costs | How much extra do I need for healthcare? | `expenses` with own inflation, `compare` |
| 6 | Inflation stress test | What if inflation runs at 4%, 6% or 8%? | `compare` |
| 7 | Part-time / semi-retirement | How much does part-time income help? | `income_streams`, `compare` |
| 8 | Asset allocation | Conservative vs balanced vs aggressive? | `compare` on return/volatility |
| 9 | Retirement budget | What will I actually spend? | budget table, then feed `annual_spending` |
| 10 | Reverse plan | What do I need to save to fund lifestyle X? | `solve --for portfolio / annual_contribution / expected_return` |

## The calculator

`scripts/retirement_calc.py` is a standard-library Python script. Write the person's profile to a JSON file (schema in `references/profile-schema.md`), then run:

```bash
python scripts/retirement_calc.py project    profile.json [--table years.csv]
python scripts/retirement_calc.py montecarlo profile.json [--runs 5000]
python scripts/retirement_calc.py compare    profile.json scenarios.json
python scripts/retirement_calc.py solve      profile.json --for retire_age [--target 0.85]
```

`solve --for` accepts `retire_age`, `annual_contribution`, `portfolio`, `expected_return`, or `annual_spending` (the maximum sustainable spending). By default it targets an 85% Monte Carlo success rate. Use `--mode deterministic` for a "just barely lasts on the average path" answer.

Facts about the model that change how you explain results:
- Spending and most amounts are in **today's dollars**. Results include nominal and today's-dollar (`_real`) values. Lead with today's dollars because people can picture them.
- `expected_return` is the average annual return. The deterministic `project` path compounds at the geometric equivalent (mean minus half the variance), so it tracks the Monte Carlo median instead of overstating growth.
- Withdrawals are grossed up by `withdrawal_tax_rate` to cover taxes. This is a blended estimate, not a tax return. Analysis 4 is where taxes get real attention.
- `compare` runs all scenarios on the same random market paths, so differences between scenarios come from the change, not from luck.

If Python is unavailable, do the math step by step in a visible table and say the result is approximate.

## Assumptions to default to (and state)

When the person doesn't specify, use these and list them in the output:
- Plan to age 95 (to be conservative about longevity). Use 100 if they mention family longevity.
- Returns: see the allocation table in `references/analyses.md` (balanced 60/40 is about 6% average with 10% volatility).
- Inflation 2.5% general, 5% for healthcare.
- Withdrawal tax rate 15% blended. Adjust it for large traditional-account balances or high-tax states.
- Success target 85% for Monte Carlo. Below 75% is fragile, and above 95% usually means they are oversaving or could retire sooner.

Country: the rules reference covers the US (Social Security, Medicare, IRA/401k/Roth, RMDs). For anyone elsewhere, the calculator still works. Swap in their state pension, tax-advantaged accounts, and healthcare system, and say which local rules you're unsure of instead of importing US ones.

## Output shape

Keep it scannable. A typical answer:

```
## Bottom line
One or two sentences answering the question directly, with the key number.

## Your numbers
A short table of the inputs used. Mark anything assumed with "(assumed)".

## Results
The analysis-specific table or comparison (see references/analyses.md).

## What moves the needle
The 2–3 levers with the biggest effect, each quantified
("retiring 2 years later raises success from 71% to 88%").

## Watch-outs
Real risks specific to them (sequence risk in the first five years, the gap before
Medicare, concentration in employer stock, and so on). Skip generic warnings.
```

End with one line noting these are planning estimates, not personalized financial, tax or legal advice, and that a fee-only fiduciary planner or CPA can confirm big, irreversible decisions such as claiming age, Roth conversions, or annuity purchases. Say it once, plainly, and don't hedge every sentence. Over-hedged answers are less useful and no safer.

## Tone

Be direct and numerate. People asking this are often anxious. A clear "you're on track, and here's the one thing to watch" helps more than a wall of caveats. If the plan doesn't work, say so plainly and move to the levers.
