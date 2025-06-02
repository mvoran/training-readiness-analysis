# Training Insights Dashboard — Project Charter & Delivery Plan

**Document Info**  
Author: Mike Voran  
Version: 1.0  
Date: 2025‑05‑30  


### Revision History
| Date | Version | Summary |
|------|---------|---------|
| 2025‑05‑30 | 1.0 | Initial public draft |


> **Vision**: Seamlessly fuse data from Hevy, TrainingPeaks, and (optionally) Apple Health to surface actionable insights on training readiness, workload, and progression — all in a single, low‑maintenance dashboard.

---

## 1. Project Charter

| Item | Definition |
|------|------------|
| **Objective** | Combine multiple independent data sources into an always‑fresh dashboard that answers **“Am I training enough, too much, or just right?”** |
| **In Scope** | • ETL jobs for **Hevy** & **TrainingPeaks** (Apple Health optional)<br>• Central analytics store (**DuckDB** file in GCS *or* MotherDuck)<br>• BI layer selected via bake‑off (Looker Studio, Metabase, Superset)<br>• First five KPIs chosen during Discovery (e.g., CTL/ATL, weekly tonnage, compliance %) |
| **Out of Scope** | Machine‑learning predictions, nutrition guidance, or mobile‑app development |
| **Stakeholders** | **Product Owner** — You (primary user)<br>**Engineer** — You / contractor<br>**Advisor** — Coach (optional) |
| **Success Metric** | Dashboard auto‑updates daily, loads in < 3 s, and is consulted ≥ 3× per week for training decisions |
| **Budget Guard‑rail** | Run‑cost ≤ US $15 per month |

---

## 2. High‑Level Project Plan

| Phase | Major Tasks | Milestone |
|-------|-------------|-----------|
| **0 — Discovery & Tool Evaluation** | 0A Metric storm & ranking<br>0B BI bake‑off (Looker Studio vs Metabase vs Superset)<br>0C Decision & charter sign‑off | **M0** — Signed charter with BI choice & top KPIs |
| **1 — Dashboard POC** | Build mock dashboard in chosen BI tool fed by CSVs | **M1** — Stakeholder‑approved prototype |
| **2 — Analytics Store Design** | Design DuckDB schema; load CSVs; validate query speed | **M2** — Schema + KPIs run < 1 s locally |
| **3 — Pipeline Foundations** | GCS bucket, GitHub repo, CI skeleton, secrets | **M3** — CI passes with empty ETL scaffold |
| **4 — Incremental ETL Delivery** | 4a Hevy job → Parquet → DuckDB<br>4b TrainingPeaks job<br>4c Apple Health (if approved) | **M4a/b/c** — Nightly files land in `raw/` bucket |
| **5 — End‑to‑End Slice** | Automated refresh writes DuckDB; BI swaps to live data | **M5** — Dashboard shows yesterday’s workouts automatically |
| **6 — Hardening & Ops** | Data‑quality tests, cost checks, alerting, docs | **M6** — Go‑live readiness review passed |
| **7 — Launch & Handoff** | Final walkthrough & documentation | **M7 / DONE** — Dashboard in daily use |

*Indicative timeline*: two one‑week sprints for Phase 0, then roughly one phase per week → **~8 weeks** to production.

---

## 3. Definition of Done

* A single GitHub Action refreshes all sources nightly.  
* Fresh data stored in GCS and materialised into DuckDB/MotherDuck **without manual steps**.  
* Dashboard loads in < 3 s and reflects previous day’s data.  
* ETL failures alert within 15 min.  
* Run‑cost ≤ US $15 per month.  
* Onboarding doc enables a new engineer to fix or extend the stack in ≤ 1 day.  

---

## 4. Decision Gates (Done vs Kill)

| Gate | Continue / DONE if… | Kill / Pivot if… |
|------|---------------------|------------------|
| **Charter (M0)** | Chosen BI tool meets UX & budget; top KPIs agreed | No BI candidate satisfies must‑have features within budget |
| **Mock Dashboard (M1)** | Prototype feels useful; KPIs actionable | Stakeholders deem dashboard unhelpful |
| **Vertical Slice (M5)** | Real data flows end‑to‑end reliably | APIs too brittle or ETL effort > value |
| **Ops Readiness (M6)** | Cost & SLOs inside guard‑rails | Storage/query cost explodes or maintenance burden too high |

---

## 5. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| API rate limits (Hevy / TP) | **Medium** | Cache responses; incremental syncs |
| Apple Health requires iOS dev | **Medium** | Make AH optional at charter stage |
| KPI churn after launch | **High** | Flexible schema; derive metrics not columns |
| Budget drift | **Low‑Med** | Monthly cost report in CI; alert at $12 mo |

---

## 6. Next‑Step Checklist (Week 1)

1. **Metric Storm** – 90‑min workshop to brainstorm & rank KPIs.  
2. **BI Bake‑off** – Half‑day to replicate 2‑3 charts in Looker, Metabase, Superset using a sample CSV.  
3. **Comparison Matrix & Charter Sign‑Off** – Choose tool, lock first KPIs (**M0**).  

---

*Ready to kick off?* Just say the word and we’ll draft the Week 1 workshop agenda.