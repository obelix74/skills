#!/usr/bin/env python3
"""Retirement projection calculator. Standard library only.

Every command reads a profile JSON (see references/profile-schema.md) and writes
a JSON result to stdout. Money in the profile is in today's dollars unless a
field says otherwise; results report both nominal and today's-dollar ("real")
figures.

Commands:
  project    Deterministic year-by-year projection at the expected return/inflation.
  montecarlo Randomized returns and inflation; probability the money lasts.
  compare    Run several named scenarios (profile overrides) side by side.
  solve      Find the value of one input that hits a goal (earliest retirement
             age, required contribution, required portfolio, required return,
             or maximum sustainable spending).

Examples:
  python retirement_calc.py project profile.json --table table.csv
  python retirement_calc.py montecarlo profile.json --runs 5000
  python retirement_calc.py compare profile.json scenarios.json
  python retirement_calc.py solve profile.json --for retire_age --target 0.85
"""

import argparse
import copy
import csv
import json
import logging
import math
import random
import statistics
import sys

logger = logging.getLogger("retirement_calc")

DEFAULTS = {
    "end_age": 95,
    "annual_contribution": 0.0,
    "contribution_growth": 0.0,
    "expected_return": 0.06,
    "return_stdev": 0.12,
    "inflation": 0.025,
    "inflation_stdev": 0.01,
    "withdrawal_tax_rate": 0.15,
    "income_streams": [],
    "expenses": [],
    "spending_changes": [],
    "one_time": [],
}


def load_profile(path):
    with open(path) as f:
        raw = json.load(f)
    profile = copy.deepcopy(DEFAULTS)
    profile.update(raw)
    for key in ("current_age", "retire_age", "portfolio", "annual_spending"):
        if key not in profile:
            raise SystemExit(f"profile is missing required field '{key}'")
    if profile["retire_age"] < profile["current_age"]:
        profile["retire_age"] = profile["current_age"]
    return profile


def deep_merge(base, overrides):
    merged = copy.deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def _active(item, age):
    start = item.get("start_age", -1)
    end = item.get("end_age")
    return age >= start and (end is None or age < end)


def base_spending(profile, age):
    """Core spending in today's dollars, honoring spending_changes by age."""
    amount = profile["annual_spending"]
    for change in sorted(profile["spending_changes"], key=lambda c: c["age"]):
        if age >= change["age"]:
            amount = change["annual"]
    return amount


def simulate(profile, returns, inflations, keep_rows=False):
    """Run one path. returns/inflations are per-year rates, one per year of the horizon.

    Order within a year: add contribution (pre-retirement) or take withdrawal
    (retirement), apply one-time cash flows, then apply the year's return.
    Spending inflates at the general rate; each extra expense can carry its own
    inflation rate (for example healthcare).
    """
    years = profile["end_age"] - profile["current_age"]
    balance = float(profile["portfolio"])
    cpi = 1.0
    expense_index = [1.0] * len(profile["expenses"])
    rows = []
    depleted_age = None

    for i in range(years):
        age = profile["current_age"] + i
        start = balance
        retired = age >= profile["retire_age"]

        contribution = 0.0
        if not retired:
            contribution = profile["annual_contribution"] * (1 + profile["contribution_growth"]) ** i

        spending = 0.0
        if retired:
            spending = base_spending(profile, age) * cpi
        for j, exp in enumerate(profile["expenses"]):
            if _active(exp, age) and (retired or exp.get("pre_retirement", False)):
                spending += exp["annual"] * expense_index[j]

        income = 0.0
        for stream in profile["income_streams"]:
            if _active(stream, age):
                if stream.get("inflation_adjusted", True):
                    income += stream["annual"] * cpi
                else:
                    income += stream["annual"]

        shortfall = spending - income
        if shortfall > 0:
            withdrawal = shortfall / (1 - profile["withdrawal_tax_rate"])
        else:
            withdrawal = shortfall  # surplus income is reinvested

        one_time = sum(e["amount"] * cpi for e in profile["one_time"] if e["age"] == age)

        balance = balance + contribution - withdrawal + one_time
        if balance <= 0:
            if keep_rows:
                rows.append(_row(age, start, contribution, spending, income, withdrawal, one_time, 0.0, 0.0, cpi))
            depleted_age = age
            balance = 0.0
            break

        r = returns[i]
        balance *= 1 + r
        if keep_rows:
            rows.append(_row(age, start, contribution, spending, income, withdrawal, one_time, r, balance, cpi))

        cpi *= 1 + inflations[i]
        for j, exp in enumerate(profile["expenses"]):
            expense_index[j] *= 1 + exp.get("inflation", inflations[i])

    return {
        "depleted_age": depleted_age,
        "ending_balance": round(balance),
        "ending_balance_real": round(balance / cpi),
        "rows": rows,
    }


def _row(age, start, contribution, spending, income, withdrawal, one_time, r, end, cpi):
    return {
        "age": age,
        "start_balance": round(start),
        "contribution": round(contribution),
        "spending": round(spending),
        "guaranteed_income": round(income),
        "portfolio_withdrawal": round(max(withdrawal, 0)),
        "one_time": round(one_time),
        "return": round(r, 4),
        "end_balance": round(end),
        "end_balance_real": round(end / cpi),
    }


def deterministic(profile, keep_rows=False):
    """Steady-path projection using the compounded (geometric) return, mu - sd^2/2,
    so it tracks the Monte Carlo median rather than overstating growth."""
    years = profile["end_age"] - profile["current_age"]
    growth = profile["expected_return"] - profile["return_stdev"] ** 2 / 2
    return simulate(
        profile,
        [growth] * years,
        [profile["inflation"]] * years,
        keep_rows=keep_rows,
    )


def draw_paths(profile, runs, seed):
    """Pre-draw random paths so different scenarios can share them (common random numbers)."""
    rng = random.Random(seed)
    years = profile["end_age"] - profile["current_age"]
    paths = []
    for _ in range(runs):
        rets = [rng.gauss(0, 1) for _ in range(years)]
        infl = [rng.gauss(0, 1) for _ in range(years)]
        paths.append((rets, infl))
    return paths


def monte_carlo(profile, runs=5000, seed=42, paths=None):
    if paths is None:
        paths = draw_paths(profile, runs, seed)
    mu, sd = profile["expected_return"], profile["return_stdev"]
    imu, isd = profile["inflation"], profile["inflation_stdev"]
    results = []
    for z_ret, z_inf in paths:
        rets = [max(-0.95, mu + sd * z) for z in z_ret]
        infl = [imu + isd * z for z in z_inf]
        results.append(simulate(profile, rets, infl))

    n = len(results)
    successes = sum(1 for r in results if r["depleted_age"] is None)
    endings = sorted(r["ending_balance_real"] for r in results)
    depletions = sorted(r["depleted_age"] for r in results if r["depleted_age"] is not None)

    def pct(data, p):
        if not data:
            return None
        k = min(len(data) - 1, max(0, int(round(p / 100 * (len(data) - 1)))))
        return data[k]

    return {
        "runs": n,
        "success_probability": round(successes / n, 4),
        "ending_balance_real_percentiles": {
            "p5": pct(endings, 5),
            "p25": pct(endings, 25),
            "p50": pct(endings, 50),
            "p75": pct(endings, 75),
            "p95": pct(endings, 95),
        },
        "failed_runs": n - successes,
        "depletion_age_when_failed": {
            "earliest": depletions[0] if depletions else None,
            "median": int(statistics.median(depletions)) if depletions else None,
        },
    }


def summarize(profile, runs, seed, paths=None):
    det = deterministic(profile)
    mc = monte_carlo(profile, runs, seed, paths)
    return {
        "deterministic": {
            "lasts_to_end_age": det["depleted_age"] is None,
            "depleted_age": det["depleted_age"],
            "ending_balance": det["ending_balance"],
            "ending_balance_real": det["ending_balance_real"],
        },
        "monte_carlo": mc,
    }


def assumptions(profile):
    keys = ["current_age", "retire_age", "end_age", "expected_return", "return_stdev",
            "inflation", "inflation_stdev", "withdrawal_tax_rate"]
    return {k: profile[k] for k in keys}


# ---------- solve ----------

SOLVABLE = {
    # field: (low, high, integer?, success increases as value goes up?)
    "retire_age": (None, None, True, True),
    "annual_contribution": (0, 1_000_000, False, True),
    "portfolio": (0, 50_000_000, False, True),
    "expected_return": (-0.02, 0.15, False, True),
    "annual_spending": (0, 2_000_000, False, False),
}


def solve(profile, field, target, runs, seed, mode):
    """Bisect on one field until success probability (or deterministic survival) meets target."""
    if field not in SOLVABLE:
        raise SystemExit(f"--for must be one of {sorted(SOLVABLE)}")
    lo, hi, integer, increasing = SOLVABLE[field]
    paths = draw_paths(profile, runs, seed) if mode == "montecarlo" else None

    def score(value):
        trial = copy.deepcopy(profile)
        trial[field] = int(value) if integer else value
        if mode == "montecarlo":
            return monte_carlo(trial, runs, seed, paths)["success_probability"]
        return 1.0 if deterministic(trial)["depleted_age"] is None else 0.0

    if field == "retire_age":
        for age in range(profile["current_age"], profile["end_age"]):
            s = score(age)
            if s >= target:
                return {"field": field, "value": age, "score": s}
        return {"field": field, "value": None, "note": "target not reachable before end_age"}

    ok = (lambda s: s >= target)
    if increasing:
        if not ok(score(hi)):
            return {"field": field, "value": None, "note": f"target not reachable even at {hi}"}
        if ok(score(lo)):
            return {"field": field, "value": lo, "score": score(lo), "note": "already meets target at the minimum"}
    else:
        if not ok(score(lo)):
            return {"field": field, "value": None, "note": f"target not reachable even at {lo}"}

    for _ in range(40):
        mid = (lo + hi) / 2
        good = ok(score(mid))
        if increasing:
            hi, lo = (mid, lo) if good else (hi, mid)
        else:
            lo, hi = (mid, hi) if good else (lo, mid)
    value = hi if increasing else lo
    if field == "expected_return":
        value = math.ceil(value * 10000) / 10000
    else:
        value = math.ceil(value) if increasing else math.floor(value)
    return {"field": field, "value": value, "score": score(value)}


# ---------- CLI ----------

def emit(obj):
    json.dump(obj, sys.stdout, indent=2)
    sys.stdout.write("\n")


def main():
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s", stream=sys.stderr)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("project")
    p.add_argument("profile")
    p.add_argument("--table", help="write the year-by-year table to this CSV path")

    m = sub.add_parser("montecarlo")
    m.add_argument("profile")
    m.add_argument("--runs", type=int, default=5000)
    m.add_argument("--seed", type=int, default=42)

    c = sub.add_parser("compare")
    c.add_argument("profile")
    c.add_argument("scenarios", help='JSON list: [{"name": "...", "overrides": {...}}, ...]')
    c.add_argument("--runs", type=int, default=3000)
    c.add_argument("--seed", type=int, default=42)

    s = sub.add_parser("solve")
    s.add_argument("profile")
    s.add_argument("--for", dest="field", required=True)
    s.add_argument("--target", type=float, default=0.85,
                   help="required Monte Carlo success probability (ignored in deterministic mode)")
    s.add_argument("--mode", choices=["montecarlo", "deterministic"], default="montecarlo")
    s.add_argument("--runs", type=int, default=2000)
    s.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()
    profile = load_profile(args.profile)

    if args.cmd == "project":
        result = deterministic(profile, keep_rows=True)
        if args.table and result["rows"]:
            with open(args.table, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(result["rows"][0].keys()))
                writer.writeheader()
                writer.writerows(result["rows"])
            logger.info("wrote %s", args.table)
        emit({"assumptions": assumptions(profile), **result})

    elif args.cmd == "montecarlo":
        emit({"assumptions": assumptions(profile), **summarize(profile, args.runs, args.seed)})

    elif args.cmd == "compare":
        with open(args.scenarios) as f:
            scenarios = json.load(f)
        paths = draw_paths(profile, args.runs, args.seed)
        out = [{"name": "baseline", **summarize(profile, args.runs, args.seed, paths)}]
        for sc in scenarios:
            trial = deep_merge(profile, sc.get("overrides", {}))
            if trial["end_age"] != profile["end_age"] or trial["current_age"] != profile["current_age"]:
                trial_paths = None
            else:
                trial_paths = paths
            out.append({"name": sc["name"], "overrides": sc.get("overrides", {}),
                        **summarize(trial, args.runs, args.seed, trial_paths)})
        emit({"assumptions": assumptions(profile), "scenarios": out})

    elif args.cmd == "solve":
        emit({"assumptions": assumptions(profile), "mode": args.mode, "target": args.target,
              **solve(profile, args.field, args.target, args.runs, args.seed, args.mode)})


if __name__ == "__main__":
    main()
