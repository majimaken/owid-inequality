import streamlit as st
import pandas as pd
import altair as alt
import os

# --- Global Configuration ---
st.set_page_config(
    page_title="OWID Inequality & Poverty Explorer",
    layout="wide" 
)

# --- 1. Define Local Data Path ---
# Using the relative path for better portability and robustness
LOCAL_DATA_PATH = 'data/pov_dataset.csv' 


# --- 2. Data Loading and Caching ---
@st.cache_data
def load_local_data(file_path):
    """Loads the full OWID poverty dataset from a local CSV file and renames key columns."""
    
    if not os.path.exists(file_path):
        st.error(f"Error: Local file not found at {file_path}")
        return pd.DataFrame() 
        
    try:
        df_full = pd.read_csv(file_path)
        
        # Rename essential columns based on the structure of the PIP dataset
        df_full.rename(columns={
            'country': 'Country',
            'year': 'Year',
            'gini': 'Gini_Coefficient',
            'headcount_ratio_international_povline': 'Poverty_Rate_2_15_Dollar'
        }, inplace=True)
        
        return df_full
        
    except Exception as e:
        st.error(f"An unexpected error occurred during data loading: {e}")
        return pd.DataFrame() 

# Loading the full dataset
df_poverty_data = load_local_data(LOCAL_DATA_PATH)

# Check if data loading was successful
if df_poverty_data.empty:
    st.stop() # Stop the app if data is not loaded

# --- 3. Sidebar Filters for Data Granularity (CORRECTED) ---

st.sidebar.header("Data Granularity Filters")

# Create list of unique values for selectboxes
reporting_options = df_poverty_data['reporting_level'].unique().tolist()
welfare_options = df_poverty_data['welfare_type'].unique().tolist()

# Selectbox for Reporting Level (Default: 'national')
selected_reporting = st.sidebar.selectbox(
    "Select Reporting Level:",
    options=reporting_options,
    index=reporting_options.index('national') if 'national' in reporting_options else 0 
)

# NEU: Multiselect für Welfare Type
# Voreingestellt sind nun beide gängigen Optionen, falls vorhanden.
default_welfare = [w for w in ['consumption', 'income'] if w in welfare_options]

selected_welfare = st.sidebar.multiselect(
    "Select Welfare Type:",
    options=welfare_options,
    default=default_welfare
)

# Apply primary filtering to the raw data
# Die Filter-Logik muss nun .isin() verwenden, da selected_welfare eine Liste ist
df_filtered = df_poverty_data[
    (df_poverty_data['reporting_level'] == selected_reporting) & 
    (df_poverty_data['welfare_type'].isin(selected_welfare)) # HIER IST DIE KORREKTUR
].copy() 

# Remove rows where the Gini coefficient is NaN after filtering (cleaner visualization)
df_filtered.dropna(subset=['Gini_Coefficient'], inplace=True)


# --- 4. Main Content and Visualisation ---

st.title("📊 Global Inequality & Poverty Trends")
st.markdown(f"""
    The current view displays data based on **Reporting Level: {selected_reporting}** and 
    **Welfare Type: {selected_welfare}**. Use the sidebar to change the granularity.
""")

# --- A. Time Series Visualization (Trend) ---

st.subheader("1. Inequality Trend (Gini Coefficient) by Country")

country_list = df_filtered['Country'].unique().tolist()

if not country_list:
    st.warning("No data available for the selected granularity filters.")
else:
    # Information about available countries
    st.info(f"The analysis uses data for **{len(country_list)}** available countries based on the current filters.")
    
    # 1. Alphabetical sorting for better visibility in the dropdown
    country_list.sort() 
    
    # 2. Improved logic for default selection
    DEFAULT_COUNTRIES = ['Germany', 'United States', 'Brazil']
    default_selection = [c for c in DEFAULT_COUNTRIES if c in country_list]
    if not default_selection:
        default_selection = country_list[:3] 

    selected_countries = st.multiselect(
        "Choose one or more Countries for Time Series Analysis:",
        options=country_list,
        default=default_selection
    )

    if selected_countries:
        df_chart = df_filtered[df_filtered['Country'].isin(selected_countries)]
        
        # Altair chart creation
        chart = alt.Chart(df_chart).mark_line(point=True).encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Gini_Coefficient:Q', title='Gini Coefficient (0=Perfect Equality)'),
            color='Country:N', 
            tooltip=['Country', 'Year', 'Gini_Coefficient']
        ).properties(
            title="Gini Coefficient Trend Over Time"
        ).interactive() 
        
        st.altair_chart(chart, use_container_width=True)
        
        
        with st.expander("Show list of all available countries"):
            st.write(", ".join(country_list))


# --- B. Ranking Visualization (Comparison) ---

st.subheader("2. Latest Gini Coefficient Ranking")

# Find the latest available year for each country in the filtered data
df_latest = df_filtered.loc[df_filtered.groupby('Country')['Year'].idxmax()]

# Sort by Gini Coefficient (Highest Gini means highest inequality -> top of the chart)
df_latest_sorted = df_latest.sort_values(by='Gini_Coefficient', ascending=False)

# Allow the user to select the top N countries
top_n = st.slider("Show Top/Bottom Countries in Ranking:", min_value=5, max_value=len(df_latest_sorted), value=20)
df_rank_display = pd.concat([df_latest_sorted.head(top_n // 2), df_latest_sorted.tail(top_n // 2)])
df_rank_display = df_rank_display.sort_values(by='Gini_Coefficient', ascending=False)

# Bar chart creation
rank_chart = alt.Chart(df_rank_display).mark_bar().encode(
    x=alt.X('Gini_Coefficient:Q', title='Gini Coefficient (Latest Year)'),
    # Use Country as Y axis, and sort it by the Gini value
    y=alt.Y('Country:N', sort=alt.EncodingSortField(field="Gini_Coefficient", op="mean", order='descending')),
    # Color the bars based on the Gini value
    color=alt.Color('Gini_Coefficient:Q', scale=alt.Scale(range='heatmap'), legend=None),
    tooltip=['Country', 'Year', 'Gini_Coefficient']
).properties(
    title=f"Inequality Ranking (Top/Bottom {top_n} Countries, Latest Data)"
).interactive()

st.altair_chart(rank_chart, use_container_width=True)


# --- 5. Raw Data Preview (Optional, in Expander) --- 

with st.expander("Show Filtered Raw Data (First 100 Rows)"):
    st.subheader("Filtered Data Preview")
    st.dataframe(df_filtered.head(100), use_container_width=True)