import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

# Helper functions
def strip_unit(a):
    if a.endswith('[kWh]'):
        a = a[:-5]
    elif a.endswith('[kVArh]'):
        a = a[:-7]
    return a
    
def strip_unit_tup(x):
    a, b = x
    a = strip_unit(a)
    return (a, b)

# Main app
st.set_page_config(layout="wide")
st.title("Energy Consumption Dashboard")

# Load and process data
@st.cache_data
def load_data():
    data_path = 'tetarom_clean_merged_data.feather'
    tetarom_df = pd.read_feather(data_path)
    tetarom_df.columns = tetarom_df.columns.map(strip_unit_tup)
    return tetarom_df

tetarom_df = load_data()

# Sidebar controls
st.sidebar.header("Controls")
resample_period = st.sidebar.selectbox(
    "Resample Period",
    ["Day", "Week", "Month"],
    index=1
)

# Raw overview plot
st.header("Raw Overview")

# Convert MultiIndex DataFrame to regular DataFrame with flattened column names
flat_df = tetarom_df.copy()
flat_df.columns = [f"{col[0]} - {col[1]}" for col in tetarom_df.columns]

fig1 = px.line(flat_df, 
               title="Energy Consumption Overview",
               template="plotly_white")
fig1.update_layout(
    height=600,
    showlegend=True,
    xaxis_title="Time",
    yaxis_title="Energy",
    hovermode='x unified'
)
st.plotly_chart(fig1, use_container_width=True)

# Station-specific analysis
st.header("Station Analysis")
station = st.selectbox("Select Station", tetarom_df.columns.get_level_values('location').unique())

# Filter data for selected station
df = tetarom_df.loc[:, pd.IndexSlice[:, station]].copy().droplevel('location', axis=1)
df['EA'] = df['EA+'] - df['EA-']
df = df[['EA', 'ER+', 'ER-']]

# Station consumption plot
fig2 = px.line(df,
               title=f"{station} Energy Consumption",
               template="plotly_white")
fig2.update_layout(
    height=600,
    showlegend=True,
    xaxis_title="Time",
    yaxis_title="Energy",
    hovermode='x unified'
)
st.plotly_chart(fig2, use_container_width=True)

# Reactive energy analysis
st.header("Reactive Energy Analysis")

# Calculate percentages
limit_x1 = 0.4843
limit_x3 = 1.1691

erpc = pd.DataFrame({
    'ER+ %age': df['ER+'] / df['EA'],
    'ER- %age': df['ER-'] / df['EA'],
    'EA': df['EA']
})

# Create subplot with dual y-axis
fig3 = make_subplots(specs=[[{"secondary_y": True}]])

# Add percentage lines
fig3.add_trace(
    go.Scatter(x=erpc.index, y=erpc['ER+ %age'], name="ER+ %age"),
    secondary_y=False
)
fig3.add_trace(
    go.Scatter(x=erpc.index, y=erpc['ER- %age'], name="ER- %age"),
    secondary_y=False
)

# Add EA line with lower opacity
fig3.add_trace(
    go.Scatter(x=erpc.index, y=erpc['EA'], name="EA", 
               line=dict(color='black', width=1), 
               opacity=0.1),
    secondary_y=True
)

# Add limit lines
fig3.add_hline(y=limit_x1, line_dash="dash", line_color="gray", name="Limit x1")
fig3.add_hline(y=limit_x3, line_dash="dash", line_color="black", name="Limit x3")

fig3.update_layout(
    title=f"{station} Reactive Energy Percentage",
    height=600,
    hovermode='x unified',
    template="plotly_white"
)

fig3.update_yaxes(title_text="Percentage", secondary_y=False)
fig3.update_yaxes(title_text="EA", secondary_y=True)

st.plotly_chart(fig3, use_container_width=True)