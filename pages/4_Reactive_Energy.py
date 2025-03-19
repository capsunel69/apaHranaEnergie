import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from energy_dashboard import load_data, update_plot_style

st.title("Energy Analysis")

# Load data
tetarom_df = load_data()

# Station selector (single one for both plots)
station = st.selectbox(
    "Select Station",
    tetarom_df.columns.get_level_values('location').unique()
)

# Filter data for selected station
df = tetarom_df.loc[:, pd.IndexSlice[:, station]].copy().droplevel('location', axis=1)
df['EA'] = df['EA+'] - df['EA-']
df = df[['EA', 'ER+', 'ER-']]

# First plot - Reactive Energy Usage
st.header("Reactive Energy Usage")
fig1 = px.line(df,
               title=f"{station} Energy Usage",
               template="plotly_white")

fig1.update_layout(
    height=500,
    xaxis_title="Time",
    yaxis_title="Energy",
    hovermode='x unified'
)
fig1 = update_plot_style(fig1)
# Calculate percentages
erpc = pd.DataFrame({
    'ER+ %age': df['ER+'] / df['EA'],
    'ER- %age': df['ER-'] / df['EA'],
    'EA': df['EA']
})

fig2 = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig2.add_trace(
    go.Scatter(x=erpc.index, y=erpc['ER+ %age'], name="ER+ %age", line=dict(width=2)),
    secondary_y=False
)
fig2.add_trace(
    go.Scatter(x=erpc.index, y=erpc['ER- %age'], name="ER- %age", line=dict(width=2)),
    secondary_y=False
)
fig2.add_trace(
    go.Scatter(x=erpc.index, y=erpc['EA'], name="EA", 
               line=dict(color='black', width=1), 
               opacity=0.1),
    secondary_y=True
)

# Add limit lines
limit_x1 = 0.4843
limit_x3 = 1.1691
fig2.add_hline(y=limit_x1, line_dash="dash", line_color="gray", name="Limit x1")
fig2.add_hline(y=limit_x3, line_dash="dash", line_color="black", name="Limit x3")

fig2.update_layout(
    height=500,
    hovermode='x unified',
    title=f"{station} Reactive Energy %age Usage"
)

fig2.update_yaxes(title_text="Percentage", secondary_y=False)
fig2.update_yaxes(title_text="EA", secondary_y=True)

fig2 = update_plot_style(fig2)

# Synchronize x-axes
fig1.update_layout(xaxis=dict(matches='x'))
fig2.update_layout(xaxis=dict(matches='x'))

# Display plots
st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True) 