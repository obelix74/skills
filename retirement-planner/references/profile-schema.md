# Profile JSON schema

Amounts are annual and in **today's dollars** unless noted. Ages are integers. Only the first four fields are required. Everything else has a default.

```json
{
  "current_age": 52,
  "retire_age": 62,
  "portfolio": 850000,
  "annual_spending": 75000,

  "end_age": 95,
  "annual_contribution": 30000,
  "contribution_growth": 0.03,
  "expected_return": 0.06,
  "return_stdev": 0.10,
  "inflation": 0.025,
  "inflation_stdev": 0.01,
  "withdrawal_tax_rate": 0.15,

  "income_streams": [
    {"name": "Social Security", "start_age": 67, "annual": 34000},
    {"name": "Spouse SS", "start_age": 67, "annual": 18000},
    {"name": "Pension (no COLA)", "start_age": 65, "annual": 12000, "inflation_adjusted": false},
    {"name": "Part-time consulting", "start_age": 62, "end_age": 66, "annual": 25000}
  ],

  "expenses": [
    {"name": "ACA premiums + OOP", "start_age": 62, "end_age": 65, "annual": 18000, "inflation": 0.055},
    {"name": "Medicare + Medigap + OOP", "start_age": 65, "annual": 9000, "inflation": 0.05},
    {"name": "College", "start_age": 52, "end_age": 56, "annual": 30000, "pre_retirement": true}
  ],

  "spending_changes": [
    {"age": 75, "annual": 67000},
    {"age": 85, "annual": 60000}
  ],

  "one_time": [
    {"age": 66, "amount": 150000},
    {"age": 70, "amount": -40000}
  ]
}
```

| Field | Default | Meaning |
|---|---|---|
| `current_age` | required | Age now |
| `retire_age` | required | Age when contributions stop and spending withdrawals begin |
| `portfolio` | required | Total invested savings now |
| `annual_spending` | required | Core retirement spending, today's $, excluding items in `expenses` |
| `end_age` | 95 | Plan horizon. The simulation runs through age `end_age - 1` |
| `annual_contribution` | 0 | Savings per year until retirement (nominal in year 1) |
| `contribution_growth` | 0 | Yearly growth of contributions, such as raises |
| `expected_return` | 0.06 | Average (arithmetic) nominal annual return |
| `return_stdev` | 0.12 | Annual volatility of returns |
| `inflation` / `inflation_stdev` | 0.025 / 0.01 | General inflation mean and volatility |
| `withdrawal_tax_rate` | 0.15 | Blended tax on portfolio withdrawals. Withdrawals are grossed up to cover it |
| `income_streams[]` | [] | Guaranteed or earned income. Active for `start_age <= age < end_age` (`end_age` optional). `inflation_adjusted` defaults to true. If false, `annual` is a fixed nominal amount |
| `expenses[]` | [] | Extra spending with its own `inflation` (defaults to general). Only applies in retirement unless `pre_retirement: true` |
| `spending_changes[]` | [] | From `age` onward, core spending becomes `annual` (today's $) |
| `one_time[]` | [] | Lump sums at an age, in today's $. Positive is an inflow (inheritance, home sale), negative is an outflow (car, roof, gift) |

## Scenarios file (for `compare`)

A list of named overrides, deep-merged onto the profile. Lists such as `income_streams` are replaced whole, not merged, so include every stream in the override.

```json
[
  {"name": "Claim SS at 70", "overrides": {"income_streams": [
    {"name": "Social Security", "start_age": 70, "annual": 42160},
    {"name": "Spouse SS", "start_age": 67, "annual": 18000},
    {"name": "Pension (no COLA)", "start_age": 65, "annual": 12000, "inflation_adjusted": false},
    {"name": "Part-time consulting", "start_age": 62, "end_age": 66, "annual": 25000}
  ]}},
  {"name": "6% inflation", "overrides": {"inflation": 0.06}},
  {"name": "Aggressive 90/10", "overrides": {"expected_return": 0.075, "return_stdev": 0.15}}
]
```
