import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from energy_dashboard import strip_unit_tup, resample_data, update_plot_style, load_data

# Set page config
st.set_page_config(
    layout="wide",
    page_title="Raw Overview",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in from the home page to access this content.")
    st.stop()

# Create placeholder for the title
title_placeholder = st.empty()
title_placeholder.title("Data Overview")

# Create placeholder for the main content
main_placeholder = st.empty()

with st.spinner('Loading and processing data...'):
    # Load data
    tetarom_df = load_data()

    # Convert MultiIndex DataFrame to regular DataFrame with flattened column names
    flat_df = tetarom_df.copy()
    flat_df.columns = [f"{col[0]} - {col[1]}" for col in tetarom_df.columns]

    # Prepare all the data and create the figure
    with main_placeholder.container():
        # Controls in a container above the plot

        col1, col2 = st.columns([1, 2])

        with col1:
            resample_period = st.segmented_control(
                "Aggregation Period",
                options=["6-hours", "Day", "Week", "Month"],
                default="6-hours",
                label_visibility="hidden"
            )

        # Apply resampling

        resampled_df = resample_data(flat_df, resample_period)

        # Add unit selection
        with col2:
            unit = st.segmented_control(
                "Unit",
                options=["kWh", "MWh"],
                default="MWh",
                label_visibility="hidden"
            )

    # Convert to MWh only if selected
    if unit == "MWh":
        resampled_df = resampled_df / 1000

    # Create figure with custom colors
    fig1 = go.Figure()

    # Color scheme for stations
    station_colors = {
        'Statia Jucu 1': '#1f77b4',  # blue
        'Statia Jucu 2': '#2ca02c',  # green
    }

    # Add traces with consistent colors
    for station in ['Statia Jucu 1', 'Statia Jucu 2']:
        # EA+ solid line
        fig1.add_trace(go.Scatter(
            x=resampled_df.index,
            y=resampled_df[f'EA+ - {station}'],
            name=f'EA+ - {station}',
            mode='lines+markers',
            marker=dict(
                color=station_colors[station],
                size=1
            ),
            line=dict(
                color=station_colors[station],
                shape='linear'
            ),
            connectgaps=False,
            legendgroup=f'group_{station}'
        ))
        
        # EA- dashed line
        fig1.add_trace(go.Scatter(
            x=resampled_df.index,
            y=resampled_df[f'EA- - {station}'],
            name=f'EA- - {station}',
            mode='lines+markers',
            marker=dict(
                color=station_colors[station],
                size=1,
                symbol='x'
            ),
            line=dict(
                color=station_colors[station],
                dash='dash',
                shape='linear'
            ),
            connectgaps=False,
            legendgroup=f'group_{station}'
        ))
        
        # ER+ dotted line
        fig1.add_trace(go.Scatter(
            x=resampled_df.index,
            y=resampled_df[f'ER+ - {station}'],
            name=f'ER+ - {station}',
            mode='lines+markers',
            marker=dict(
                color=station_colors[station],
                size=1,
                symbol='diamond'
            ),
            line=dict(
                color=station_colors[station],
                dash='dot',
                shape='linear'
            ),
            connectgaps=False,
            opacity=0.7,
            legendgroup=f'group_{station}'
        ))
        
        # ER- dash-dot line
        fig1.add_trace(go.Scatter(
            x=resampled_df.index,
            y=resampled_df[f'ER- - {station}'],
            name=f'ER- - {station}',
            mode='lines+markers',
            marker=dict(
                color=station_colors[station],
                size=1,
                symbol='triangle-up'
            ),
            line=dict(
                color=station_colors[station],
                dash='dashdot',
                shape='linear'
            ),
            connectgaps=False,
            opacity=0.7,
            legendgroup=f'group_{station}'
        ))

    fig1.update_layout(
        height=600,
        showlegend=True,
        xaxis_title="Time",
        yaxis_title=f"Energy Consumption ({unit})",
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title=dict(
            text=f"Energy Consumption Overview ({resample_period}ly)",
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
            bgcolor='rgba(255,255,255,0.8)',
            groupclick="toggleitem"
        ),
        xaxis=dict(
            type="date"
        )
    )

    # Update axes formatting
    fig1.update_yaxes(
        gridcolor='rgba(128,128,128,0.1)',
        zeroline=False,
        tickformat=",.1f",
        ticksuffix=f" {unit}"
    )

    fig1.update_xaxes(gridcolor='rgba(128,128,128,0.1)', zeroline=False)

    # Update hover template
    fig1.update_traces(
        hovertemplate="%{y:,.1f} " + unit + "<br>%{x}<extra></extra>"
    )

    # Apply the styling
    fig1 = update_plot_style(fig1)

    st.plotly_chart(fig1, use_container_width=True) 