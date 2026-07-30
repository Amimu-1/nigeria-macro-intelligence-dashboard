# Nigeria Macroeconomic Intelligence Dashboard

**An end-to-end macroeconomic analytics platform built on real CBN and NBS data — engineered for policy analysis, economic research, and evidence-based decision-making.**

[!\[Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[!\[SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://www.sqlite.org/)
\[!\[Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen.svg)]()
[!\[License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

Nigeria's macroeconomic data is publicly available — but it is scattered, inconsistently formatted, and rarely analyzed rigorously in one place. This project builds a production-grade pipeline that ingests real Central Bank of Nigeria (CBN) and National Bureau of Statistics (NBS) data, cleans it to analysis-ready standards, structures it in a relational database, and surfaces policy-relevant insights — the kind of work expected at institutions like the CBN, World Bank, PenCom, and ECOWAS.

This is not a toy dataset exercise. Every number in this project traces back to an official, verifiable public source.

## What Makes This Different

* **Real government data, not sample datasets** — sourced directly from CBN's rate exports and NBS's Nigeria Data Portal
* **Cross-source validation** — CBN and NBS both report inflation; this project surfaces and investigates where they diverge (e.g., a 2025 CPI rebasing to 2024=100 creates a measurable gap between sources — exactly the kind of nuance a policy analyst should catch, not smooth over)
* **Proper data engineering, not spreadsheet hacking** — reproducible Python ETL, a documented relational schema, and version-controlled cleaning logic for every source
* **Built by someone who works with data professionally** — combining a Data Analyst background with hands-on quality assurance leadership experience and postgraduate study in Public Policy and Administration

## Architecture

```
Raw Data (CBN, NBS)
        ↓
Python Ingestion \\\& Inspection  (src/ingestion/)
        ↓
Source-Specific Cleaning       (src/cleaning/)
        ↓
SQLite Star Schema Database    (src/database/)
        ↓
Analytical Queries \\\& Insights  (src/analysis/)
        ↓
Power BI Dashboard  +  Policy Brief  (in progress)
```

**Database design:** a `dim\\\_date` dimension table joined to per-source fact tables (`fact\\\_cbn\\\_inflation`, `fact\\\_nbs\\\_cpi`, with more indicators being added), enabling clean time-series joins across every economic indicator in the project.

## Tech Stack

|Layer|Tools|
|-|-|
|Ingestion \& Cleaning|Python, Pandas, openpyxl, python-calamine|
|Database|SQLite (star schema)|
|Analysis|SQL (CTEs, joins across fact tables)|
|Visualization|Power BI *(in progress)*|
|Testing|pytest *(planned)*|

## Current Status

This project is under active development, built incrementally and transparently:

* \[x] Environment and repository setup
* \[x] CBN inflation data — ingested, cleaned, validated (2015–2025, monthly)
* \[x] NBS CPI data — ingested, cleaned, validated (2015–2025, monthly)
* \[x] SQLite star schema database with joined fact tables
* \[x] Exchange rate data (2015-2026, monthly, merged across historical and NFEM regimes)
* \[ ] Foreign reserves data
* \[ ] Interest rates (MPR) \& money supply (M1/M2/M3)
* \[ ] Banking sector health metrics
* \[ ] 8+ advanced analytical SQL queries (post-subsidy impact, correlation analysis, sector health)
* \[ ] 4-page Power BI dashboard
* \[ ] Policy brief with evidence-based recommendations

## Sample Finding

Cross-referencing CBN and NBS headline inflation for November 2025 reveals a **2.9 percentage point gap** (17.33% vs. 14.45%) — likely attributable to NBS's 2025 CPI rebasing to a 2024=100 base year. This kind of source discrepancy has real implications for policy communication and public trust in official statistics, and will be explored further in the forthcoming policy brief.

## Getting Started

```bash
# Clone the repository
git clone https://github.com/Amimu-1/nigeria-macro-intelligence-dashboard.git
cd nigeria-macro-intelligence-dashboard

# Set up the environment
python -m venv venv
venv\\\\Scripts\\\\activate      # Windows
pip install -r requirements.txt

# Run the pipeline
python src/cleaning/clean\\\_cbn\\\_inflation.py
python src/cleaning/clean\\\_nbs\\\_cpi.py
python src/database/build\\\_database.py

# Explore the data
python src/analysis/test\\\_query.py
```

## Data Sources

* [CBN Data \& Statistics](https://www.cbn.gov.ng/rates/)
* [Nigeria Data Portal (NBS)](https://nigeria.opendataforafrica.org/)

## About the Author

**Aminu Momodu Audu** — Data Analyst based in Abuja, Nigeria, with a background combining quantitative analytics and public policy. Formerly a Data Analyst Intern at Bluestock Fintech, where he built a 92-company financial intelligence platform with 50+ KPIs and 320 passing tests. Currently pursuing an MPPA at Bayero University Kano, bringing a policy lens to data work most technical portfolios lack.

* GitHub: [github.com/Amimu-1](https://github.com/Amimu-1)
* LinkedIn: [linkedin.com/in/aminu-momodu-audu-040359406](https://linkedin.com/in/aminu-momodu-audu-040359406)

\---

*This project is actively maintained. Star or watch the repo to follow its progress toward a complete macroeconomic intelligence platform.*

