# 📋 Production Change Request (CR) - CHG0092104

| Field | Details |
| :--- | :--- |
| **Change Request ID** | `CHG0092104` |
| **Change Type** | **Standard / Normal** |
| **Risk Level** | **Low** |
| **Impact** | Low (Backward-compatible additive column & view refresh) |
| **Requested By** | Lead Data Analyst (Commercial & EV Operations) |
| **Approval Board** | Data Governance & Change Advisory Board (CAB) |
| **Implementation Window** | 2026-05-02 02:00 - 03:00 UTC |

---

## 1. Business Purpose & Description of Change
To support the European Union and Nordic government EV incentive policies, this change adds `ev_subsidy_tier` to `dim_geography` and enriches `vw_commercial_ev_transition` with net government subsidy impact.

---

## 2. Technical Implementation Plan
1. **Schema DDL Update:** Add column `ev_subsidy_tier VARCHAR(20) NOT NULL` to table `dim_geography`.
2. **Data Pipeline Update:** Update `src/data_generator.py` and `db_loader.py` to populate subsidy tiers based on country policy.
3. **View Recreation:** Execute `sql/02_analytical_views.sql` to refresh `vw_commercial_ev_transition`.
4. **Automated Verification:** Run `src/data_quality_checks.py` in staging environment.

---

## 3. Pre-Deployment Test Evidence
* **Unit Tests:** Executed 11/11 passing tests in GitHub Actions runner.
* **Query Performance Impact:** Explaining `vw_commercial_ev_transition` showed index seek on `geo_id` with 0ms performance regression.
* **Row Count Verification:** `dim_geography` row count preserved exactly at 7 master markets.

---

## 4. Backout & Rollback Plan
If unexpected query degradation or schema incompatibility occurs:
1. Execute Rollback DDL:
   ```sql
   ALTER TABLE dim_geography DROP COLUMN ev_subsidy_tier;
   SOURCE sql/02_analytical_views_v1.sql;
   ```
2. Revert Git commit on `main` branch to commit `#b8f3e21`.
3. Trigger Power BI dataset refresh to restore previous schema cache.

---

## 5. Post-Deployment Verification
* Confirm `SELECT DISTINCT ev_subsidy_tier FROM dim_geography;` returns `{'High', 'Moderate', 'None'}`.
* Verify Power BI report refreshes without visual broken state icons.
