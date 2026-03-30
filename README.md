---
title: Hospital Audit Sentinel
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.31.0
app_file: app.py
pinned: false
---

# 🏥 Hospital Audit Sentinel
**Automated Healthcare Data Integrity & Compliance Pipeline**

## 🌟 Project Overview
The **Hospital Audit Sentinel** is a full-stack data engineering and analytics solution built to modernize healthcare auditing. This project processes over 1 million rows of CMS (Centers for Medicare & Medicaid Services) data, transforming raw provider records into an interactive "Sentinel" dashboard that flags billing anomalies, payment outliers, and data gaps.

## 🏗️ Technical Architecture
This project demonstrates a professional **Modern Data Stack (MDS)** workflow:
*   **Data Warehouse:** Google BigQuery (Handling large-scale healthcare datasets).
*   **Transformation Layer:** `dbt` (Data Build Tool) for modular, version-controlled SQL modeling and data cleaning.
*   **App Framework:** `Streamlit` for a high-performance Python-based analytical interface.
*   **CI/CD:** `GitHub Actions` to automate deployment and synchronization.
*   **Environment:** Hosted on `Hugging Face Spaces` for global accessibility.

## 🚀 Core Features
*   **Anomaly Detection:** Automated filters to identify hospitals with disproportionate "Average Payments" vs. "Total Discharges."
*   **Geospatial Insights:** Regional audit views categorized by State and HRR (Hospital Referral Region).
*   **Production-Ready Secrets Management:** Integrated with `st.secrets` to securely handle GCP Service Account authentication without exposing credentials.
*   **Responsive Analytics:** Dynamic data fetching from BigQuery to provide real-time audit updates.

## 📂 Repository Structure
*   `app.py`: The main entry point for the Sentinel Dashboard.
*   `pages/`: Contains specialized analysis modules (e.g., Hospital Analysis).
*   `.github/workflows/`: Automation scripts for continuous deployment.
*   `requirements.txt`: Managed Python dependencies for the cloud environment.

## 🛠️ Local Development
To run this project locally:
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Configure your GCP credentials in `.streamlit/secrets.toml`.
4. Launch the app: `streamlit run app.py`.

---
**Developer:** [Your Name/Link]
**Dataset:** CMS Medicare Provider Utilization and Payment Data.
