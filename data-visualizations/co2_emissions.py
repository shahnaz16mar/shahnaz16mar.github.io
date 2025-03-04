import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


base_url = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Indicator_2_Carbon_Emission_per_unit_of_Output/FeatureServer/0/query"

# Parameters for API request
params = {
    "outFields": "*",
    "where": "1=1",
    "f": "geojson",
    "resultRecordCount": 1000,  # Number of records per request
    "resultOffset": 0,  # Start from the first record
}

all_properties = []

while True:
    # Request data
    response = requests.get(base_url, params=params, timeout=30).json()

    # Extract "properties"
    features = response.get("features", [])
    if not features:
        break  # Stop when no more data is returned

    all_properties.extend([feature["properties"] for feature in features])

    # Update offset for next batch
    params["resultOffset"] += params["resultRecordCount"]

# Convert to DataFrame
df = pd.DataFrame(all_properties)

data = df.drop(
    [
        "ISO2",
        "CTS_Code",
        "CTS_Name",
        "CTS_Full_Descriptor",
        "ObjectId",
        "Scale",
    ],
    axis=1,
)

final_data = data.melt(
    id_vars=["ISO3", "Country", "Indicator", "Unit", "Source", "Industry"],
    var_name="Year",
    value_name="value",
)

final_data["Year"] = final_data["Year"].str[1:].astype(int)

# ------------------------------------------------------------------------------------
# Sidebar information


st.sidebar.markdown("### Additional Information")
st.sidebar.markdown("**Source:** https://climatedata.imf.org/")
st.sidebar.markdown(
    "[Click here to view the table](https://climatedata.imf.org/datasets/7cec1228bfbe4a5e876ca5a5abedd64f_0/about)"
)

st.sidebar.header("Filters")

selected_country = st.sidebar.multiselect(
    "Country",
    options=final_data["ISO3"].unique(),
    default=["USA", "CHN"],
)

selected_indicator = st.sidebar.selectbox(
    "Indicator",
    options=final_data["Indicator"].unique(),
    index=len(final_data["Indicator"].unique()) - 1,
)

selected_year = st.sidebar.selectbox(
    "Year",
    options=final_data["Year"].unique(),
    index=len(final_data["Year"].unique()) - 1,
)


# -----------------------------------------------------------------------------------------------

# Line Chart for CO2 Emissions Over Time

trend_data = final_data.loc[final_data["ISO3"].isin(selected_country)]
trend_data = trend_data.loc[trend_data["Indicator"] == selected_indicator]
trend_data = trend_data.groupby(["ISO3", "Year"], as_index=False)["value"].sum()


fig1, ax1 = plt.subplots(figsize=(10, 6))

trend_chart = sns.lineplot(
    x="Year",
    y="value",
    hue="ISO3",
    data=trend_data,
    marker="o",
    markersize=8,
    linewidth=2.5,
    palette="pastel",
    # color="royalblue",
    # label="CO2 Emissions",
    ax=ax1,
)
ax1.set_title(
    f"{selected_indicator} Over Time by {selected_country}",
    fontsize=14,
    fontweight="bold",
)
ax1.set_ylabel(f"{selected_indicator}")
ax1.set_xlabel("Year", fontsize=12)

ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)

st.pyplot(fig1)

st.divider()

# ----------------------------------------------------------------------------------------------


selected_year_data = final_data.loc[final_data["Year"] == selected_year]
selected_year_data = selected_year_data.loc[
    final_data["Indicator"] == selected_indicator
]
selected_year_data_bar = selected_year_data.groupby("ISO3", as_index=False)[
    "value"
].sum()
selected_year_data_bar_sorted = selected_year_data_bar.sort_values(
    "value", ascending=False
).iloc[:10, :]

plt.style.use("seaborn-darkgrid")

fig2, ax2 = plt.subplots(figsize=(10, 6))

colors = sns.color_palette("pastel", len(selected_year_data_bar_sorted))

bar_chart = ax2.bar(
    data=selected_year_data_bar_sorted,
    x="ISO3",
    height="value",
    color=colors,
    edgecolor="black",
)

for bar in bar_chart:
    yval = bar.get_height()
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        yval,
        f"{yval:,.0f}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )

ax2.set_title(
    f"Top 10 Countries in {selected_year}: {selected_indicator}",
    fontsize=14,
    fontweight="bold",
    pad=15,
)

ax2.set_xlabel("Country (ISO3 Code)", fontsize=12)
ax2.set_ylabel("CO Emissions (Metric Tons)", fontsize=12)

ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)

st.pyplot(fig2)

st.divider()

# -----------------------------------------------------------------------------------

selected_year_data = final_data.loc[final_data["Year"] == selected_year]
selected_year_data = selected_year_data.loc[
    final_data["Indicator"] == selected_indicator
]
data_pie = selected_year_data.groupby("Industry", as_index=False)["value"].sum()
data_pie_sorted = data_pie.sort_values("value", ascending=False).iloc[:10, :]

fig3, ax3 = plt.subplots(figsize=(11, 7))

pie_chart = ax3.pie(
    data=data_pie_sorted,
    labels="Industry",
    x="value",
    autopct="%1.1f%%",
    colors=sns.color_palette("pastel", len(data_pie_sorted)),
    startangle=140,
    wedgeprops={"edgecolor": "black"},
)

ax3.set_title(
    f"{selected_indicator} by Industry in {selected_year} for {selected_country}",
    fontsize=14,
    fontweight="bold",
    pad=15,
)

st.pyplot(fig3)

# ----------------------------------------------------------------------------------------------
