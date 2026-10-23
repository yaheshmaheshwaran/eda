# 🌍 Global CO2 Emissions & Climate Change — EDA Project

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.x-green?logo=pandas)](https://pandas.pydata.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> **Exploratory Data Analysis of Global CO₂ Emissions (1950–2022)**  
> A comprehensive visual investigation into how the world's carbon footprint has evolved over seven decades.

---

## 📌 Project Overview

This project performs a thorough **Exploratory Data Analysis (EDA)** on the *Our World in Data — CO₂ and Greenhouse Gas Emissions* dataset. The analysis uncovers trends in global CO₂ emissions, identifies the world's largest emitters, explores per-capita fairness, and examines the relationship between economic growth and carbon output.

---

## 🗂️ Repository Structure

```
co2-emissions-eda/
│
├── data/
│   └── owid-co2-data.csv          # Dataset (auto-downloaded on first run)
│
├── visualizations/                # All 10 generated plots (PNG, 150 dpi)
│   ├── 01_global_co2_trend.png
│   ├── 02_top10_emitters_2022.png
│   ├── 03_per_capita_top15.png
│   ├── 04_emissions_by_source.png
│   ├── 05_share_global_co2.png
│   ├── 06_correlation_heatmap.png
│   ├── 07_gdp_vs_co2.png
│   ├── 08_cumulative_co2_pie.png
│   ├── 09_china_india_comparison.png
│   └── 10_decade_heatmap.png
│
├── report/
│   └── CO2_EDA_Report.pdf         # Full project report
│
├── co2_eda_analysis.py            # Main EDA script
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 📊 Dataset

| Property | Value |
|----------|-------|
| **Source** | [Our World in Data](https://ourworldindata.org/co2-and-greenhouse-gas-emissions) |
| **GitHub** | [owid/co2-data](https://github.com/owid/co2-data) |
| **File** | `owid-co2-data.csv` |
| **Rows** | ~50,000 |
| **Columns** | 79 |
| **Coverage** | 200+ countries, 1750–2022 |

The dataset is **automatically downloaded** on the first run. No manual setup required.

---

## 📈 Visualizations Included

| # | Plot | Description |
|---|------|-------------|
| 1 | **Global CO₂ Trend** | Line + area chart showing world CO₂ 1950–2022 with key policy milestones |
| 2 | **Top 10 Emitters (2022)** | Horizontal bar chart — absolute total emissions |
| 3 | **Per-Capita Top 15** | Bar chart — emissions per person (fairness perspective) |
| 4 | **Emissions by Source** | Stacked area chart — Coal, Oil, Gas, Cement, Flaring |
| 5 | **Global Share Trends** | Multi-line chart — Top 5 countries' share of global CO₂ |
| 6 | **Correlation Heatmap** | Lower-triangle heatmap of all key variables |
| 7 | **GDP vs CO₂ Scatter** | Bubble chart — economic development vs carbon footprint |
| 8 | **Cumulative CO₂ Pie** | Historical responsibility by country (since industrial era) |
| 9 | **China vs India** | Side-by-side area charts — fastest-growing emitters |
| 10 | **Decade Heatmap** | Grid heatmap — top 15 countries across 7 decades |

---

## 🔍 Key Findings

1. **Global CO₂ grew by ~420%** from 1950 to 2022 (8.5 Gt → 37 Gt)
2. **China** is now the largest single-country emitter (~31% of global)
3. **Qatar & UAE** top the per-capita charts despite small populations
4. **Coal** remains the dominant source, responsible for ~40% of energy CO₂
5. **USA** holds the highest *cumulative* (historical) emissions burden (~25%)
6. China's CO₂ output surged **15×** since 1950 due to rapid industrialisation
7. India's per-capita emissions (~2 t) are well below the global average (~4.7 t)
8. GDP per capita and CO₂ per capita correlate strongly (**R² ≈ 0.55**)
9. Post-2015, global growth rate is decelerating due to renewable energy uptake
10. Cement and flaring are emerging as fast-growing minor emission sources

---

## 🚀 How to Run

### Prerequisites
- Python 3.9 or above
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/co2-emissions-eda.git
cd co2-emissions-eda

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the EDA Script

```bash
python co2_eda_analysis.py
```

The script will:
1. **Auto-download** the dataset (first run only, ~5 MB)
2. **Clean & preprocess** the data
3. **Generate all 10 visualizations** → saved to `visualizations/`
4. **Print key statistics** and findings to the console

---

## 🛠️ Tech Stack

| Library | Purpose |
|---------|---------|
| `pandas` | Data loading, cleaning, manipulation |
| `numpy` | Numerical operations |
| `matplotlib` | Base plotting engine |
| `seaborn` | Statistical visualizations (heatmaps) |
| `scipy` | Regression analysis |

---

## 📄 Report

The full project report (PDF) is available in the `report/` directory.  
It covers: Introduction, Dataset Description, Methodology, EDA with all visualizations, Key Findings, and Conclusion.

---

## 👤 Author

**[Your Name]**  
Course: EDA & Visualization  
Submission Date: October 2026

---

## 📜 License

This project is open-source under the [MIT License](LICENSE).  
Dataset © Our World in Data (CC BY 4.0)
