# Google Pay Personal Spend Analysis
### An end-to-end data engineering and personal finance analytics project

An end-to-end data pipeline built on 4+ years of personal Google Pay transaction data, transforming raw, unstructured HTML exports into a structured database and interactive Power BI dashboard to uncover personal spending patterns and identify savings opportunities.

**Timeline:** January 2022 – May 2026  
**Total Transactions Analyzed:** 2,800+  
**Tools Used:** Python, BeautifulSoup, Pandas, DuckDB, Power BI

---

## Table of Contents
1. [Problem Statement](#problem-statement)
2. [Project Architecture](#project-architecture)
3. [ETL Pipeline](#etl-pipeline)
4. [Dashboard Features](#dashboard-features)
5. [DAX Measures and KPIs](#dax-measures-and-kpis)
6. [Key Findings](#key-findings)
7. [Tech Stack](#tech-stack)
---

## Problem Statement

As a college student managing independent finances over 4+ years, I wanted to understand where my money was actually going and whether my spending habits were improving or worsening over time.

The challenge: Google Pay only provides transaction data as an unstructured HTML file, with no built-in analytics. There was no way to answer questions like:

- How much of my spending is discretionary vs necessary?
- Which merchants am I spending the most on?
- Do I spend more on weekends than weekdays?

This project builds the entire analytics stack from scratch from raw HTML to an interactive dashboard to answer these questions with data.

---

## Project Architecture

```
Google Pay HTML Export
        ↓
   parse.py          ← Extract transactions from unstructured HTML
        ↓
 transform.py        ← Clean, standardize, and enrich data
        ↓
   load.py           ← Load into DuckDB database
        ↓
transactions.csv     ← Manual category annotation in Excel
        ↓
  Power BI           ← Interactive dashboard with drillthrough
```
---

## ETL Pipeline

### Stage 1 — Extract (`parse.py`)
- Reads the raw Google Pay HTML file using **BeautifulSoup**.
- Uses **regex** to extract transaction amount, merchant name, datetime, transaction ID, and status from each transaction card.
- Transaction ID (from the Details section of each card) is used as the **primary key** to prevent duplicates.
- Outputs a list of structured dictionaries, one per transaction.

**Key design decision:** Using the transaction ID as primary key rather than deduplicating by datetime + amount, which would incorrectly drop legitimate same-day same-amount transactions to different merchants.

### Stage 2 — Transform (`transform.py`)
- Parses and standardizes datetime format, removing unicode characters (narrow no-break space `\u202f`) introduced by the HTML export.
- Extracts derived columns: `date`, `month`, `year`, `day_of_week`, `is_weekend`, `time_of_day`.
- Standardizes merchant names using a **merchant alias dictionary** 
  — consolidating variants like "Zomato", "Zomato Ltd", "Zomato Online Order" into a single canonical name.
- Drops rows with null datetime values (unparseable transactions).
- Removes duplicate transactions using transaction ID.

**Time of day classification:**
| Label | Hours |
|---|---|
| Morning | 5:00 AM – 11:59 AM |
| Afternoon | 12:00 PM – 4:59 PM |
| Evening | 5:00 PM – 8:59 PM |
| Night | 9:00 PM – 4:59 AM |

### Stage 3 — Load (`load.py`)
- Connects to a local **DuckDB** database.
- Drops and recreates the transactions table on each run (ensuring clean reloads when new data is added).
- Loads the transformed DataFrame directly into DuckDB using DuckDB's native Pandas integration.
- Exports final enriched CSV for Power BI consumption.

### Stage 3.5 — Manual Enrichment
- The exported CSV is opened in Excel
- A `category` column is manually annotated per transaction, classifying spend into: Meals, Food Delivery, Restaurant, Fast Food, Snacks, Dessert, Groceries, Groceries Delivery, Travel, Entertainment, Medical, Miscellaneous, Personal Transfer, Metro Tickets, Subscription, Laundry.
- The annotated CSV is then reloaded into DuckDB via `load.py`.

---

## Dashboard Features

The Power BI dashboard consists of two views — an Overview page 
and a Year Detail drillthrough page.

### Overview Page — "Spend Insights"
The entry point to the dashboard answers the broad question: 
*"What does my spending look like overall?"*

- **4 KPI Cards:** Total spend (all time), average monthly spend, total transactions, and average transaction value, giving an immediate headline summary of the
  entire dataset
- **Yearly Spend Trend with YoY% overlay:** A combo chart showing total spend per year as bars and year-over-year % change as a line with labeled data points
  reveals both spending volume and rate of change in a single visual. The 120% jump from 2022 to 2023 and the subsequent deceleration are immediately visible.
- **Category Treemap:** Proportional view of spending distribution across all categories block size represents total spend, making the dominance of Food Delivery
  and Restaurant instantly apparent.
- **Discretionary vs Necessary Spend Pie Chart:** Shows the overall split between necessary spending (Meals, Groceries, Metro, Medical) and discretionary spending   (everything else) as proportions of total spend providing a single, clear answer to the question "how much of my budget was a choice?"

### Year Detail — Drillthrough Page — "Monthly Spend Patterns"
Right-clicking any year bar on the Overview trend chart drills through to this dedicated page, automatically filtered to the selected year. Answers: *"What did this specific year look like in depth?"*

- **4 KPI Cards:** Total spend for the year, transaction count, average daily spend, and YoY change % vs the prior year the YoY card uses conditional formatting     to show positive growth and negative growth distinctly.
- **Monthly Spending Trend:** Line chart showing month-by-month fluctuation within the selected year reveals seasonal patterns and spending spikes not visible in    the yearly overview.
- **Day of Week × Time of Day Heatmap:** A color-scaled matrix showing average daily spend broken down by day of week (rows) and time of day (columns) where         darker cells indicate higher average spend, making behavioral patterns immediately readable without parsing numbers.
- **Average Daily Spend by Day of Week:** Bar chart providing ranking of spending by day complements the heatmap with a simpler, one-dimensional view.
- **Spend Bucket Composition by Month:** Stacked bar chart categorizing each month's spend into three buckets Necessary, Discretionary Food, and Discretionary       Lifestyle showing how the composition of spending shifted month by month within the year.

**How to use drillthrough:** On the Overview page, right-click 
any year bar on the trend chart → Drillthrough → Year Detail

---

## DAX Measures and KPIs

### Avg Daily Spend
```dax
Avg Daily Spend = 
DIVIDE(
    SUM(transactions[amount]),
    DISTINCTCOUNT(transactions[date])
)
```
Calculates average spend per day rather than per transaction gives a fair comparison across time periods with different numbers of active days. Use`DISTINCTCOUNT` on date to count unique days with transactions rather than total transaction count.

### Avg Monthly Spend
```dax
Avg Monthly Spend = 
DIVIDE(
    SUM(transactions[amount]),
    DISTINCTCOUNT(transactions[month])
)
```
Total spend divided by number of distinct months with transactions gives the typical monthly expenditure for the filtered period.

### YoY Change %
```dax
Prior Year Spend = 
CALCULATE(
    SUM(transactions[amount]),
    transactions[year] = SELECTEDVALUE(transactions[year]) - 1
)

YoY Change % = 
DIVIDE(
    SUM(transactions[amount]) - [Prior Year Spend],
    [Prior Year Spend]
)
```
Uses `SELECTEDVALUE` to identify the current year in filter context works within the Year Detail drillthrough page where a single year is always selected. Compares current year total against the prior year to produce a signed percentage change.

### Necessary Spend and Discretionary Spend
```dax
Necessary Spend = 
CALCULATE(
    SUM(transactions[amount]),
    transactions[category] IN {"Meals", "Metro Tickets", 
                               "Groceries", "Medical"}
)

Discretionary Spend = 
CALCULATE(
    SUM(transactions[amount]),
    transactions[category] IN {"Food Delivery", "Restaurant", 
                               "Fast Food", "Snacks", "Dessert", 
                               "Entertainment", "Miscellaneous"}
)
```
Uses `CALCULATE` to override the current filter context and restrict the sum to only the specified categories the core mechanism enabling the necessary vs discretionary split across all visuals.

### Category % of Total
```dax
Category % of Total = 
DIVIDE(
    SUM(transactions[amount]),
    CALCULATE(SUM(transactions[amount]), ALL(transactions))
)
```
`ALL(transactions)` removes all active filters to compute the 
grand total, then divides the currently filtered sum by it — 
dynamically computing each category's share of total spend 
regardless of what filters are active.

## Key Findings

1. **Spending grew 120% from 2022 to 2023**: The largest single-year jump in the dataset. Growth then decelerated to 25% (2024) and 6% (2025), suggesting a           natural plateau.

2. **Food Delivery is the single largest spending category**: Dominating the category treemap and consistently ranking as the top expense across all years.

3. **Weekend nights drive the highest spending concentration**: The Day of Week × Time of Day heatmap shows weekend night slots as the darkest cells across           multiple years, suggesting social and leisure spending clusters specifically in this window.

4. **Necessary spend accounts for 57.24% of total budget**: With discretionary spend making up the remaining 42.76%, as shown in the Overview pie chart.

5. **2026 shows a -58% YoY change**: However this reflects a partial year (January–May only) rather than a genuine spending decline.
---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.13 | Core pipeline language |
| BeautifulSoup4 | HTML parsing and data extraction |
| Pandas | Data cleaning and transformation |
| DuckDB | Lightweight analytical database |
| Power BI Desktop | Interactive dashboard and visualization |
| DAX | Calculated measures and KPIs in Power BI |
| Git / GitHub | Version control and portfolio hosting |

---

*Note: Raw transaction data is not included in this repository to protect financial privacy. The pipeline scripts are fully reproducible with any Google Pay HTML export.*
