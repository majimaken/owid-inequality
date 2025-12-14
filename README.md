# 🌍 Global Inequality and Poverty Explorer (Streamlit App)

## Overview
This repository hosts the Streamlit application **Global Inequality and Poverty Explorer**. The application is designed for interactive analysis and visualization of global poverty and inequality data, primarily sourced from the World Bank's Poverty and Inequality Platform (PIP) dataset.

The dashboard allows users to filter high-granularity data (different reporting levels and welfare types) and visualize trends over time.

### Core Features:
* **Interactive Sidebar Filters:** Granular filtering by `reporting_level` (e.g., national) and `welfare_type` (consumption vs. income) to clean and standardize the dataset view.
* **Global Entry Point:** A Choropleth Map (World Map) visualizes the latest available **Gini Coefficient** as the primary visual anchor upon loading.
* **Time Series Analysis:** Interactive line charts (Altair) to track the Gini Coefficient trend over time for selected countries.
* **Ranking View:** A bar chart displays a clear ranking of countries based on the most recent Gini Coefficient value.

## Installation and Setup

### 1. Clone the Repository and Prepare the Environment
```bash
# Clone the repository
git clone https://github.com/majimaken/owid-inequality.git
cd owid-inequality

# --- 1. Create a new virtual environment ---
# This command creates a new, isolated Python environment named '.venv'
python3 -m venv .venv 

# --- 2. Activate the environment ---
.\.venv\Scripts\Activate

# --- 3. Install dependencies ---
# Ensure all necessary libraries are installed inside the activated environment
pip install -r requirements.txt
