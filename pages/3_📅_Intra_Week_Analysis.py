import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from energy_dashboard import load_data, update_plot_style

# Set page config
st.set_page_config(
    layout="wide",
    page_title="Intra-Week Analysis",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in from the home page to access this content.")
    st.stop()

st.title("Intra-Week Consumption")

# Controls for intra-week analysis
with st.container():
    col1, col2 = st.columns([1, 2])
    with col1:
        intra_week_station = st.segmented_control(
            "Select Station",
            options=["Statia Jucu 1", "Statia Jucu 2", "Total"],
            default="Statia Jucu 1"  # Set default to first station
        )
    with col2:
        aggregation_period = st.segmented_control(
            "View By",
            options=["Week", "Month"],
            default="Week"
        )

# Add loading indicator
with st.spinner('Loading and processing data...'):
    # Load data
    tetarom_df = load_data()
    
    # Prepare data for intra-week analysis
    df = tetarom_df.copy()
    if intra_week_station != "Total":
        df = df.loc[:, pd.IndexSlice[:, intra_week_station]].copy().droplevel('location', axis=1)
        df = df['EA+']  # Just using EA+ for consumption as a Series
    else:
        # Calculate total across all stations
        df = df.loc[:, pd.IndexSlice['EA+', :]].copy()
        df = df.sum(axis=1)

    # Create week-based index
    df_week = pd.DataFrame(index=df.index)
    df_week['value'] = df
    df_week['month'] = df_week.index.to_period('M')
    df_week['week'] = df_week.index.to_period('W')
    df_week['day_of_week'] = df_week.index.dayofweek
    df_week['time_of_day'] = df_week.index.time
    df_week['time_in_week'] = pd.to_timedelta(df_week['day_of_week'], unit='D') + \
                             pd.to_timedelta(df_week['time_of_day'].astype(str))

    # Group by selected period
    group_col = 'month' if aggregation_period == "Month" else 'week'

    # Pivot the data
    pattern = df_week.pivot_table(
        values='value',
        index='time_in_week',
        columns=group_col,
        aggfunc='mean'
    )

    # Create and update the plot
    fig4 = go.Figure()
    
    # Calculate color intensities based on chronological order
    n_periods = len(pattern.columns)

    # Add a line for each period in reverse order
    for idx, column in enumerate(reversed(pattern.columns)):
        opacity = 1 - (0.92 * idx / (n_periods - 1))
        fig4.add_trace(
            go.Scatter(
                x=pattern.index.total_seconds()/3600/24,
                y=pattern[column],
                name=column.strftime('%Y-%m') if aggregation_period == "Month" else column.strftime('%Y-%m-%d'),
                mode='lines',
                line=dict(
                    width=1.5,
                    color=f'rgba(31, 119, 180, {opacity})',
                    shape='spline',
                    smoothing=0.3
                ),
                hovertemplate='%{y:.1f} kWh<br>%{text}<extra></extra>',
                text=[column.strftime('%Y-%m') if aggregation_period == "Month" else column.strftime('%Y-%m-%d')] * len(pattern.index)
            )
        )

    # Update layout and styling
    fig4.update_layout(
        title=dict(
            text=f"Intra-Week Consumption Pattern - {intra_week_station}",
            y=0.98,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        height=600,
        xaxis_title="Day of Week",
        yaxis_title="Energy Consumption (kWh)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=20, t=80, b=20),
        legend=dict(
            title=f"{aggregation_period}",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1,
            font=dict(size=8)
        ),
        showlegend=True
    )

    # Update axes
    fig4.update_xaxes(
        gridcolor='rgba(128,128,128,0.1)',
        zeroline=False,
        ticktext=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        tickvals=[0, 1, 2, 3, 4, 5, 6],
        tickmode='array',
        tickangle=0,
        showgrid=True
    )

    fig4.update_yaxes(
        gridcolor='rgba(128,128,128,0.1)',
        zeroline=False,
        ticksuffix=" kWh",
        showgrid=True
    )

    # Apply the styling
    fig4 = update_plot_style(fig4)

    # Display the plot
    st.plotly_chart(fig4, use_container_width=True) 