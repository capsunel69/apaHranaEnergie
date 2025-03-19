import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from energy_dashboard import load_data, update_plot_style

st.title("Energy Analysis")

# Load data
tetarom_df = load_data()

# Create tabs for the two visualizations
tab1, tab2 = st.tabs(["Reactive Energy Usage", "Reactive Energy Percentage"])

with tab1:
    st.header("Reactive Energy Usage")

    # Station selector
    station = st.selectbox(
        "Select Station",
        tetarom_df.columns.get_level_values('location').unique(),
        key="station_selector1"
    )

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
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title=dict(
            text=f"{station} Energy Consumption",
            y=0.98,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        margin=dict(l=50, r=20, t=80, b=20),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255,255,255,0.8)'
        )
    )
    
    fig2 = update_plot_style(fig2)
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.header("Reactive Energy Percentage")

    # Station selector
    station = st.selectbox(
        "Select Station",
        tetarom_df.columns.get_level_values('location').unique(),
        key="station_selector2"
    )

    # Filter data for selected station
    df = tetarom_df.loc[:, pd.IndexSlice[:, station]].copy().droplevel('location', axis=1)
    df['EA'] = df['EA+'] - df['EA-']
    df = df[['EA', 'ER+', 'ER-']]

    # Calculate percentages
    erpc = pd.DataFrame({
        'ER+ %age': df['ER+'] / df['EA'],
        'ER- %age': df['ER-'] / df['EA'],
        'EA': df['EA']
    })

    # Create subplot with dual y-axis
    fig3 = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig3.add_trace(
        go.Scatter(x=erpc.index, y=erpc['ER+ %age'], name="ER+ %age", line=dict(width=2)),
        secondary_y=False
    )
    fig3.add_trace(
        go.Scatter(x=erpc.index, y=erpc['ER- %age'], name="ER- %age", line=dict(width=2)),
        secondary_y=False
    )
    fig3.add_trace(
        go.Scatter(x=erpc.index, y=erpc['EA'], name="EA", 
                   line=dict(color='black', width=1), 
                   opacity=0.1),
        secondary_y=True
    )

    # Add limit lines
    limit_x1 = 0.4843
    limit_x3 = 1.1691
    fig3.add_hline(y=limit_x1, line_dash="dash", line_color="red", name="Limit x1")
    fig3.add_hline(y=limit_x3, line_dash="dash", line_color="black", name="Limit x3")

    fig3.update_layout(
        title=dict(
            text=f"{station} Reactive Energy Percentage",
            y=0.98,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        height=600,
        hovermode='x unified',
        template="plotly_white",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=20, t=80, b=20),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255,255,255,0.8)'
        )
    )

    fig3.update_yaxes(title_text="Percentage", secondary_y=False)
    fig3.update_yaxes(title_text="EA", secondary_y=True)

    fig3 = update_plot_style(fig3)
    st.plotly_chart(fig3, use_container_width=True) 