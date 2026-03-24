"""
Banking SQL Portfolio — Interactive Demo
Run: python run_demo.py
"""
import sqlite3
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()
DB = "banking.db"

SQL_DIR = "sql"


def get_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def run_sql_file(conn, filename):
    path = os.path.join(SQL_DIR, filename)
    with open(path, encoding="utf-8") as f:
        conn.executescript(f.read())


def query(conn, sql):
    cursor = conn.execute(sql)
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description] if cursor.description else []
    return cols, rows


def show_table(title, cols, rows, max_rows=10):
    table = Table(title=title, show_header=True,
                  header_style="bold cyan", border_style="dim")
    for col in cols:
        table.add_column(col, overflow="fold")
    for row in list(rows)[:max_rows]:
        table.add_row(*[str(v) if v is not None else "NULL" for v in row])
    if len(rows) > max_rows:
        table.add_row(*["..." for _ in cols])
    console.print(table)
    console.print()


def setup_database():
    if os.path.exists(DB):
        os.remove(DB)
    conn = get_connection()
    console.print(Panel("[bold green]Setting up database...[/]"))
    run_sql_file(conn, "01_schema.sql")
    console.print("[green]✓[/] Schema created")
    run_sql_file(conn, "02_seed_data.sql")
    console.print("[green]✓[/] Sample data inserted")
    conn.commit()
    console.print()
    return conn


def main():
    console.print(Panel(
        Text("Banking SQL Portfolio", style="bold white"),
        subtitle="30 production queries — Finance & Insurance",
        border_style="blue"
    ))

    conn = setup_database()

    # Q1: Client balances
    cols, rows = query(conn, """
        SELECT c.first_name||' '||c.last_name AS client,
               c.city, COUNT(a.id) AS accounts,
               SUM(a.balance) AS total_balance
        FROM clients c JOIN accounts a ON c.id=a.client_id
        WHERE a.is_active=1
        GROUP BY c.id ORDER BY total_balance DESC
    """)
    show_table("Q1 — Client Total Balances", cols, rows)

    # Q2: Net cash flow
    cols, rows = query(conn, """
        SELECT c.first_name||' '||c.last_name AS client,
            SUM(CASE WHEN t.tx_type='DEPOSIT'    THEN  t.amount
                     WHEN t.tx_type='WITHDRAWAL' THEN -t.amount
                     ELSE 0 END) AS net_flow
        FROM clients c
        JOIN accounts a ON c.id=a.client_id
        JOIN transactions t
          ON a.id IN (t.from_account_id, t.to_account_id)
        WHERE t.status='COMPLETED'
        GROUP BY c.id ORDER BY net_flow DESC
    """)
    show_table("Q2 — Net Cash Flow per Client", cols, rows)

    # Q3: AML structuring detection
    cols, rows = query(conn, """
        SELECT a.account_no,
               c.first_name||' '||c.last_name AS client,
               DATE(t.tx_date) AS tx_date,
               COUNT(t.id) AS tx_count,
               SUM(t.amount) AS total_daily
        FROM transactions t
        JOIN accounts a ON a.id = t.from_account_id
        JOIN clients c  ON c.id = a.client_id
        WHERE t.tx_type='WITHDRAWAL'
          AND t.amount BETWEEN 8500 AND 9999.99
        GROUP BY a.id, DATE(t.tx_date)
        HAVING COUNT(t.id) >= 2
    """)
    show_table("Q3 — AML: Structuring Detection", cols, rows)

    # Q4: S/P Loss ratio
    cols, rows = query(conn, """
        SELECT p.policy_type,
               c.first_name||' '||c.last_name AS client,
               p.annual_premium,
               COALESCE(SUM(CASE WHEN cl.status IN ('APPROVED','PAID')
                    THEN cl.approved_amount ELSE 0 END),0) AS claims_paid,
               ROUND(COALESCE(SUM(CASE WHEN cl.status IN ('APPROVED','PAID')
                    THEN cl.approved_amount ELSE 0 END),0)
                    /p.annual_premium*100,2) AS sp_ratio_pct
        FROM policies p
        JOIN clients c ON p.client_id=c.id
        LEFT JOIN claims cl ON cl.policy_id=p.id
        WHERE p.is_active=1
        GROUP BY p.id ORDER BY sp_ratio_pct DESC
    """)
    show_table("Q4 — S/P Loss Ratio (Claims/Premiums)", cols, rows)

    # Q5: Customer 360 CTE
    cols, rows = query(conn, """
        WITH acc AS (
            SELECT client_id, COUNT(*) n, SUM(balance) bal
            FROM accounts WHERE is_active=1 GROUP BY client_id
        ),
        pol AS (
            SELECT client_id, COUNT(*) n, SUM(annual_premium) prem
            FROM policies WHERE is_active=1 GROUP BY client_id
        )
        SELECT c.first_name||' '||c.last_name AS client,
               c.city,
               COALESCE(a.bal,0)  AS bank_balance,
               COALESCE(p.n,0)    AS policies,
               COALESCE(p.prem,0) AS annual_premiums,
               rs.score           AS risk_score,
               rs.risk_level
        FROM clients c
        LEFT JOIN acc a  ON a.client_id=c.id
        LEFT JOIN pol p  ON p.client_id=c.id
        LEFT JOIN risk_scores rs ON rs.client_id=c.id
        ORDER BY bank_balance DESC
    """)
    show_table("Q5 — Customer 360 View (CTE)", cols, rows)

    # Q6: Executive dashboard
    cols, rows = query(conn, """
        SELECT 'TOTAL CLIENTS' AS metric, CAST(COUNT(*) AS TEXT) AS value
        FROM clients
        UNION ALL
        SELECT 'ACTIVE ACCOUNTS', CAST(COUNT(*) AS TEXT)
        FROM accounts WHERE is_active=1
        UNION ALL
        SELECT 'ACTIVE POLICIES', CAST(COUNT(*) AS TEXT)
        FROM policies WHERE is_active=1
        UNION ALL
        SELECT 'TOTAL DEPOSITS (EUR)', CAST(ROUND(SUM(balance),2) AS TEXT)
        FROM accounts WHERE is_active=1
        UNION ALL
        SELECT 'TOTAL PREMIUMS/YEAR', CAST(ROUND(SUM(annual_premium),2) AS TEXT)
        FROM policies WHERE is_active=1
        UNION ALL
        SELECT 'PENDING CLAIMS', CAST(COUNT(*) AS TEXT)
        FROM claims WHERE status='SUBMITTED'
    """)
    show_table("Q6 — Executive Dashboard", cols, rows)

    conn.close()
    console.print(Panel(
        "[bold green]All queries ran successfully![/]\n"
        "Open [cyan]sql/03_queries.sql[/] to see all 18 queries with comments.",
        border_style="green"
    ))


if __name__ == "__main__":
    main()