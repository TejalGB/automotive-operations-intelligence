# 🚨 Incident Root Cause Analysis (RCA) - INC0841203

| Field | Details |
| :--- | :--- |
| **Incident ID** | `INC0841203` |
| **Priority** | **P3 - Medium** |
| **Service Affected** | Commercial KPI Reporting & DAX Discount Leakage Measure |
| **Reported By** | Global Head of Direct-to-Consumer & Care Subscriptions |
| **Assigned To** | Lead Data Analyst |
| **Incident Status** | **Resolved & Closed** |
| **Resolution Time** | 3 Hours |

---

## 1. Summary & Problem Statement
Following the rollout of the *"Nordic Mobility"* subscription pilot program across Amsterdam and Stockholm, the commercial executive KPI **"Discount Leakage %"** spiked unnaturally from an expected $3.8\%$ to $17.9\%$, triggering an alert from Commercial Operations.

---

## 2. Root Cause
Subscription vehicles are provisioned with an upfront invoice price of `0.00` in the sales order ledger because revenue is recognized as recurring monthly operational fees rather than a one-time capital sale.

The original Power BI DAX formula calculated Discount Leakage as:
$$\text{Discount Leakage \%} = \frac{\sum (\text{MSRP} - \text{Sale Price})}{\sum \text{MSRP}}$$

Because `Sale Price` was `0`, the DAX formula treated the full €53,500 MSRP of every subscription vehicle as a $100\%$ dealer discount.

---

## 3. Solution & Corrective Actions

1. **Updated DAX Measure:**  
   Filtered out `sale_channel = 'Care_Subscription'` from traditional dealer discount calculations:
   ```dax
   Discount Leakage % = 
   DIVIDE(
       CALCULATE(
           SUM(fct_vehicle_sales[dealer_discount_local]) * SELECTEDVALUE(dim_exchange_rates[exchange_rate_to_eur], 1.0),
           fct_vehicle_sales[sale_channel] IN {"Dealer_Wholesale", "Online_D2C"}
       ),
       CALCULATE(
           SUM(dim_vehicles[base_msrp_eur]),
           fct_vehicle_sales[sale_channel] IN {"Dealer_Wholesale", "Online_D2C"}
       ),
       0
   )
   ```

2. **Added Staging Table Documentation:**  
   Updated the enterprise data dictionary to clarify that subscription vehicle lifecycle revenue is tracked in recurring MRR marts rather than transactional retail sales discount marts.

3. **Automated Assertion:**  
   Added test case in `src/data_quality_checks.py` verifying that subscription vehicles carry `dealer_discount_local = 0.00`.
