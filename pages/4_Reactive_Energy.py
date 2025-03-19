import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from energy_dashboard import load_data, update_plot_style

# Set page config
st.set_page_config(
    layout="wide",
    page_title="Reactive Energy",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

st.title("Energy Analysis")

# Load data
tetarom_df = load_data()

# Define limits
limit_x1 = 0.4843  # 48.43%
limit_x3 = 1.1691  # 116.91%

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
    hovermode='x unified',
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
)
fig1 = update_plot_style(fig1)
# Calculate percentages
erpc = pd.DataFrame({
    'ER+ %age': df['ER+'] / df['EA'],
    'ER- %age': df['ER-'] / df['EA'],
    'EA': df['EA']
})

fig2 = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces for fig2
# Split the data into above and below limit for ER+ %age
mask_above = erpc['ER+ %age'] > limit_x1
fig2.add_trace(
    go.Scatter(x=erpc[~mask_above].index, y=erpc[~mask_above]['ER+ %age'], 
               name="ER+ %age (Normal)", line=dict(width=2, color='blue')),
    secondary_y=False
)
fig2.add_trace(
    go.Scatter(x=erpc[mask_above].index, y=erpc[mask_above]['ER+ %age'], 
               name="ER+ %age (Above Limit)", line=dict(width=2, color='red')),
    secondary_y=False
)

# Split the data for ER- %age
mask_above_negative = erpc['ER- %age'] > limit_x1
fig2.add_trace(
    go.Scatter(x=erpc[~mask_above_negative].index, y=erpc[~mask_above_negative]['ER- %age'], 
               name="ER- %age (Normal)", line=dict(width=2, color='green')),
    secondary_y=False
)
fig2.add_trace(
    go.Scatter(x=erpc[mask_above_negative].index, y=erpc[mask_above_negative]['ER- %age'], 
               name="ER- %age (Above Limit)", line=dict(width=2, color='red')),
    secondary_y=False
)

fig2.add_trace(
    go.Scatter(x=erpc.index, y=erpc['EA'], name="EA", 
               line=dict(color='black', width=1), 
               opacity=0.1),
    secondary_y=True
)

# Add limit lines with names in legend
fig2.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        name="Limit x1 (0.4843)",
        line=dict(color="red", dash="dash"),
        showlegend=True,
        legendgroup="limits"
    )
)
fig2.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        name="Limit x3 (1.1691)",
        line=dict(color="black", dash="dash"),
        showlegend=True,
        legendgroup="limits"
    )
)

# Add the actual limit lines (without legend entries)
fig2.add_hline(y=limit_x1, line_dash="dash", line_color="red", showlegend=False)
fig2.add_hline(y=limit_x3, line_dash="dash", line_color="black", showlegend=False)

fig2.update_layout(
    height=500,
    hovermode='x unified',
    title=f"{station} Reactive Energy %age Usage",
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        title_text="Data Series"
    )
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