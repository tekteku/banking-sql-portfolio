# Banking SQL Portfolio

> 30 production-quality SQL queries for banking and insurance analytics.
> Built to demonstrate SQL depth for finance sector interviews.

## What this shows

| Concept | Query |
|---------|-------|
| Conditional aggregation | Deposits vs withdrawals per client |
| Window function | Running account balance (bank statement) |
| Anti-join | Dormant accounts with no transactions |
| AML detection | Structuring pattern (near-threshold withdrawals) |
| S/P Loss ratio | Core insurance KPI: claims / premiums |
| CTE | Customer 360 view across all tables |
| UNION ALL | Executive dashboard in one query |
| RANK() OVER | Client ranking by balance within country |

## Schema

6 tables: `clients`, `accounts`, `transactions`, `policies`, `claims`, `risk_scores`

## Run locally
```bash
pip install rich
python run_demo.py
```

## Interview answer

*"I built a SQL portfolio with 30 queries covering the key concepts
tested in banking and insurance interviews: window functions for running
balances, CTEs for multi-step aggregations, conditional aggregation for
deposit/withdrawal splits, and an AML structuring detection query that
flags clients making multiple transactions just below the 10,000 EUR
reporting threshold — a classic money-laundering pattern."*