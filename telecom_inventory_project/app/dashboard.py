import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Telecom Inventory Dashboard", layout="wide")

st.title("AI-Powered Telecom Inventory Dashboard")
st.info("West region shows both the highest shortage and highest excess, indicating inventory allocation inefficiency across sites.")
st.write("Analyze shortages, excess inventory, cost drivers, and critical sites.")

@st.cache_data
def load_data():
    df = pd.read_excel("data/telecom_inventory.xlsx")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("File not found. Put telecom_inventory.xlsx inside the data folder.")
    st.stop()

st.sidebar.header("Filters")

selected_regions = st.sidebar.multiselect(
    "Select Region(s)",
    options=sorted(df["Region"].dropna().unique()),
    default=sorted(df["Region"].dropna().unique())
)

selected_equipment = st.sidebar.multiselect(
    "Select Equipment Type(s)",
    options=sorted(df["Equipment_Type"].dropna().unique()),
    default=sorted(df["Equipment_Type"].dropna().unique())
)

lead_time_threshold = st.sidebar.slider(
    "Critical lead time threshold",
    min_value=1,
    max_value=20,
    value=10
)

filtered_df = df[
    (df["Region"].isin(selected_regions)) &
    (df["Equipment_Type"].isin(selected_equipment))
].copy()

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

shortage_by_region = filtered_df.groupby("Region")["Clean_Shortage"].sum().sort_values(ascending=False)
excess_by_region = filtered_df.groupby("Region")["Clean_Excess"].sum().sort_values(ascending=False)
cost_by_equipment = filtered_df.groupby("Equipment_Type")["Total_Order_Cost"].sum().sort_values(ascending=False)
critical_sites_df = filtered_df[
    (filtered_df["Clean_Shortage"] > 0) &
    (filtered_df["Lead_Time_Days"] > lead_time_threshold)
]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Shortage", f"{int(filtered_df['Clean_Shortage'].sum()):,}")
col2.metric("Total Excess", f"{int(filtered_df['Clean_Excess'].sum()):,}")
col3.metric("Inventory Order Cost", f"{int(filtered_df['Total_Order_Cost'].sum()):,}")
col4.metric("Critical Sites", f"{int(critical_sites_df.shape[0]):,}")

st.subheader("Regional and Cost Analysis")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("**Shortage by Region**")
    fig1, ax1 = plt.subplots(figsize=(7, 4))
    shortage_by_region.plot(kind="bar", ax=ax1)
    ax1.set_title("Total Shortage by Region")
    ax1.set_xlabel("Region")
    ax1.set_ylabel("Shortage Units")
    st.pyplot(fig1)

with chart_col2:
    st.markdown("**Excess by Region**")
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    excess_by_region.plot(kind="bar", ax=ax2)
    ax2.set_title("Total Excess by Region")
    ax2.set_xlabel("Region")
    ax2.set_ylabel("Excess Units")
    st.pyplot(fig2)

st.markdown("**Cost by Equipment Type**")
fig3, ax3 = plt.subplots(figsize=(7, 4))
cost_by_equipment.plot(kind="bar", ax=ax3)
ax3.set_title("Inventory Order Cost by Equipment Type")
ax3.set_xlabel("Equipment Type")
ax3.set_ylabel("Total Cost")
st.pyplot(fig3)

st.subheader("Automated Business Insights and Recommendations")

insight = f"""
1. {shortage_by_region.index[0]} region has the highest shortage of {int(shortage_by_region.iloc[0]):,} units, indicating a major demand-supply mismatch.
2. {excess_by_region.index[0]} region also has the highest excess inventory of {int(excess_by_region.iloc[0]):,} units, suggesting inefficient stock allocation across sites.
3. {cost_by_equipment.index[0]} is the most expensive equipment category with a total order cost of {int(cost_by_equipment.iloc[0]):,}, making it the biggest contributor to inventory spend.
4. There are {critical_sites_df.shape[0]:,} critical sites with both shortage and lead times above {lead_time_threshold} days, increasing the risk of operational delays.
5. Recommendation: Improve site-level inventory balancing, prioritize replenishment for critical sites, and optimize high-cost equipment ordering.
"""

st.text(insight)

st.subheader("Critical Sites")
st.dataframe(
    critical_sites_df[
        [
            "Site_ID",
            "Region",
            "Equipment_Type",
            "Required_Qty",
            "Available_Qty",
            "Ordered_Qty",
            "Lead_Time_Days",
            "Clean_Shortage",
            "Total_Order_Cost"
        ]
    ].sort_values(by=["Clean_Shortage", "Lead_Time_Days"], ascending=[False, False]),
    use_container_width=True
)

st.subheader("Filtered Raw Data")
st.dataframe(filtered_df, use_container_width=True)