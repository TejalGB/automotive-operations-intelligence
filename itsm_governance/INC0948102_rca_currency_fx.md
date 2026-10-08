# 🚨 Incident Root Cause Analysis (RCA) - INC0948102

| Field | Details |
| :--- | :--- |
| **Incident ID** | `INC0948102` |
| **Priority** | **P2 - High** |
| **Service Affected** | Commercial Sales Mart (`fct_vehicle_sales`) & Executive Power BI Report |
| **Reported By** | Commercial Finance Lead (UK & Americas Sales Hub) |
| **Assigned To** | Data Analytics & Operations Team |
| **Incident Status** | **Resolved & Closed** |
| **Resolution SLA Target** | 4 Hours (Actual Resolution: 2h 15m) |

---

## 1. Executive Summary & Business Impact
On 2026-04-14 at 08:30 AM CET, the Commercial Finance Director flagged that the **Power BI Global Executive Dashboard** reported severe negative gross margins ($-45\%$ to $-65\%$) across all Q1 deliveries in the United Kingdom and North America. 

This incorrect metric distorted global Q1 commercial reporting presented to the Executive Leadership Team, triggering a P2 incident.

---

## 2. Timeline of Events

* **08:30 CET:** Incident `INC0948102` logged in ServiceNow by Commercial Finance.
* **08:45 CET:** Incident triaged by Analytics On-Call. Severity confirmed as P2 due to C-Suite report visibility.
* **09:15 CET:** Root Cause isolated to the currency extraction pipeline from SAP SD.
* **09:50 CET:** SQL transformation fix authored in branch `fix/INC0948102-fx-normalization`.
* **10:15 CET:** Automated CI assertions verified in GitHub Actions; unit test added to prevent regression.
* **10:35 CET:** Emergency Change Request `CHG0091024` approved; hotfix deployed to production MySQL database.
* **10:45 CET:** Power BI dataset refreshed; Commercial Finance verified accurate positive margins ($22.4\%$ for UK, $19.8\%$ for US). Incident resolved.

---

## 3. Root Cause Analysis (5 Whys)

1. **Why did the dashboard show negative gross margins?**  
   Because factory unit costs (denominated in EUR) exceeded the recorded sales revenue for UK and US deliveries.
2. **Why was sales revenue lower than factory cost?**  
   Because UK vehicle prices (e.g., £35,000 GBP) and US prices (e.g., \$42,000 USD) were being directly compared against EUR factory costs (€31,200) without currency conversion.
3. **Why were UK and US sales not converted to EUR?**  
   The initial staging model assumed all global SAP invoices arrived pre-converted in EUR base currency.
4. **Why did the data pipeline not catch this?**  
   There was no automated assertion test checking that `net_revenue_eur >= factory_cost_eur * 0.70`.
5. **Root Cause:**  
   Lack of an automated exchange rate transformation layer (`dim_exchange_rates`) in the Star Schema staging pipeline and missing financial sanity assertions.

---

## 4. Corrective Actions & Implementation

### A. SQL Transformation Fix
Joined `fct_vehicle_sales` with `dim_exchange_rates` to calculate normalized EUR revenue and margins:
```sql
-- Transformation logic implemented in 01_schema_ddl.sql / stg_sales
s.net_revenue_eur = s.net_sale_price_local * s.fx_rate_to_eur;
s.gross_profit_eur = s.net_revenue_eur - s.factory_cost_eur;
s.gross_margin_pct = (s.gross_profit_eur / s.net_revenue_eur) * 100;
```

### B. Automated Regression Assertion (Data Quality CI)
Added a permanent test in `src/data_quality_checks.py`:
```python
def test_currency_normalization(self):
    margin_valid = (self.fct_sales["gross_margin_pct"] >= -5.0).all()
    self._assert(
        margin_valid,
        "Currency Normalization & Margin Sanity (INC0948102)",
        "Unnormalized FX or extreme negative margin anomalies found."
    )
```

---

## 5. Sign-Off & Approvals
* **Analytics Engineer:** Gowin (Lead Data Analyst)
* **Finance Approver:** Commercial Finance Director (UK & Americas)
* **ITSM Incident Manager:** Closed with Root Cause Code: `DATA_PIPELINE_TRANSFORMATION_LOGIC`
