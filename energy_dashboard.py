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

def resample_data(df, period):
    if period == "Day":
        return df.resample('D').sum()
    elif period == "Week":
        return df.resample('W').sum()
    else:  # Month
        return df.resample('M').sum()

# Add plot styling function here
def update_plot_style(fig):
    fig.update_layout(
        font_family="sans-serif",
        title_font_size=20,
        margin=dict(l=50, r=20, t=80, b=20),
        legend=dict(
            borderwidth=1,
            font=dict(size=10)
        )
    )
    fig.update_xaxes(
        gridcolor='rgba(128,128,128,0.1)',
        linewidth=1,
        ticks="outside"
    )
    fig.update_yaxes(
        gridcolor='rgba(128,128,128,0.1)',
        linewidth=1,
        ticks="outside"
    )
    return fig

# Set page config
st.set_page_config(layout="wide", page_title="Energy Dashboard", initial_sidebar_state="expanded")

# Add sidebar navigation
with st.sidebar:
    st.title("Navigation")
    nav_selection = st.radio(
        "Go to",
        ["Raw Overview", 
         "Intra-Week Consumption",
         "Reactive Energy Usage",
         "Reactive Energy %age Usage"]
    )

st.title("Energy Consumption Dashboard")

# Load and process data
@st.cache_data
def load_data():
    data_path = 'tetarom_clean_merged_data.feather'
    tetarom_df = pd.read_feather(data_path)
    tetarom_df.columns = tetarom_df.columns.map(strip_unit_tup)
    return tetarom_df

tetarom_df = load_data()

# Raw overview section
if nav_selection == "Raw Overview":
    st.header("Raw Overview")

    # Controls in a container above the plot
    with st.container():
        resample_period = st.selectbox(
            "Aggregation Period",
            ["Day", "Week", "Month"],
            index=1
        )

    # Convert MultiIndex DataFrame to regular DataFrame with flattened column names
    flat_df = tetarom_df.copy()
    flat_df.columns = [f"{col[0]} - {col[1]}" for col in tetarom_df.columns]

    # Apply resampling
    resampled_df = resample_data(flat_df, resample_period)

    # Add unit selection
    with st.container():
        unit = st.selectbox(
            "Unit",
            ["kWh", "MWh"],
            index=1
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
            line=dict(color=station_colors[station], width=2),
            legendgroup=f'group_{station}'
        ))
        
        # EA- dashed line (same color as EA+)
        fig1.add_trace(go.Scatter(
            x=resampled_df.index,
            y=resampled_df[f'EA- - {station}'],
            name=f'EA- - {station}',
            line=dict(color=station_colors[station], width=2, dash='dash'),
            legendgroup=f'group_{station}'
        ))
        
        # ER+ dotted line (lighter version of station color)
        fig1.add_trace(go.Scatter(
            x=resampled_df.index,
            y=resampled_df[f'ER+ - {station}'],
            name=f'ER+ - {station}',
            line=dict(color=station_colors[station], width=1.5, dash='dot'),
            opacity=0.7,
            legendgroup=f'group_{station}'
        ))
        
        # ER- dash-dot line (lighter version of station color)
        fig1.add_trace(go.Scatter(
            x=resampled_df.index,
            y=resampled_df[f'ER- - {station}'],
            name=f'ER- - {station}',
            line=dict(color=station_colors[station], width=1.5, dash='dashdot'),
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

    # Apply the styling to each figure
    # For fig1:
    fig1 = update_plot_style(fig1)

    st.plotly_chart(fig1, use_container_width=True)

# Intra-week consumption section
elif nav_selection == "Intra-Week Consumption":
    st.header("Intra-Week Consumption")

    # Controls for intra-week analysis
    with st.container():
        col1, col2 = st.columns([1, 2])
        with col1:
            intra_week_station = st.selectbox(
                "Select Station",
                ["Statia Jucu 1", "Statia Jucu 2", "Total"],
                key="intra_week_selector"
            )
        with col2:
            aggregation_period = st.selectbox(
                "View By",
                ["Week", "Month"],
                key="aggregation_selector"
            )

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

    # Create the plot
    fig4 = go.Figure()

    # Add a line for each period
    for column in pattern.columns:
        fig4.add_trace(
            go.Scatter(
                x=pattern.index.total_seconds()/3600/24,
                y=pattern[column],
                name=column.strftime('%Y-%m') if aggregation_period == "Month" else column.strftime('%Y-%m-%d'),
                mode='lines',
                line=dict(width=1)
            )
        )

    fig4.update_layout(
        title=dict(
            text=f"Intra-Week Consumption Pattern - {intra_week_station} (by {aggregation_period})",
            y=0.98,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        height=600,
        xaxis_title="Day of Week",
        yaxis_title="Energy Consumption (kWh)",
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=50, r=20, t=80, b=20),
        legend=dict(
            title=f"{aggregation_period}",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255,255,255,0.8)',
            font=dict(size=8)
        ),
        showlegend=True
    )

    # Update x-axis to show day names
    fig4.update_xaxes(
        gridcolor='rgba(128,128,128,0.1)',
        zeroline=False,
        ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        tickvals=[0, 1, 2, 3, 4, 5, 6],
        tickmode='array'
    )

    fig4.update_yaxes(
        gridcolor='rgba(128,128,128,0.1)',
        zeroline=False,
        ticksuffix=" kWh"
    )

    # Apply the styling to fig4
    fig4 = update_plot_style(fig4)

    st.plotly_chart(fig4, use_container_width=True)

# Reactive Energy Usage section
elif nav_selection == "Reactive Energy Usage":
    st.header("Reactive Energy Usage")

    # Station selector
    station = st.selectbox(
        "Select Station",
        tetarom_df.columns.get_level_values('location').unique()
    )

    # Filter data for selected station (using original non-resampled data)
    df = tetarom_df.loc[:, pd.IndexSlice[:, station]].copy().droplevel('location', axis=1)
    df['EA'] = df['EA+'] - df['EA-']
    df = df[['EA', 'ER+', 'ER-']]

    # Station consumption plot (no resampling)
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
    fig2.update_xaxes(gridcolor='rgba(128,128,128,0.1)', zeroline=False)
    fig2.update_yaxes(gridcolor='rgba(128,128,128,0.1)', zeroline=False)

    # Apply the styling to fig2
    fig2 = update_plot_style(fig2)

    st.plotly_chart(fig2, use_container_width=True)

# Reactive Energy %age Usage section
else:  # nav_selection == "Reactive Energy %age Usage"
    st.header("Reactive Energy %age Usage")

    # Station selector (same as in Reactive Energy Usage section)
    station = st.selectbox(
        "Select Station",
        tetarom_df.columns.get_level_values('location').unique()
    )

    # Filter data for selected station
    df = tetarom_df.loc[:, pd.IndexSlice[:, station]].copy().droplevel('location', axis=1)
    df['EA'] = df['EA+'] - df['EA-']
    df = df[['EA', 'ER+', 'ER-']]

    # Calculate percentages using non-resampled data
    erpc = pd.DataFrame({
        'ER+ %age': df['ER+'] / df['EA'],
        'ER- %age': df['ER-'] / df['EA'],
        'EA': df['EA']
    })

    # Create subplot with dual y-axis
    fig3 = make_subplots(specs=[[{"secondary_y": True}]])

    # Add percentage lines
    fig3.add_trace(
        go.Scatter(x=erpc.index, y=erpc['ER+ %age'], name="ER+ %age", line=dict(width=2)),
        secondary_y=False
    )
    fig3.add_trace(
        go.Scatter(x=erpc.index, y=erpc['ER- %age'], name="ER- %age", line=dict(width=2)),
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
    limit_x1 = 0.4843
    limit_x3 = 1.1691
    fig3.add_hline(y=limit_x1, 
                   line_dash="dash", 
                   line_color="red",
                   name="Limit x1")
    fig3.add_hline(y=limit_x3, 
                   line_dash="dash", 
                   line_color="black", 
                   name="Limit x3")

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

    fig3.update_xaxes(gridcolor='rgba(128,128,128,0.1)', zeroline=False)
    fig3.update_yaxes(gridcolor='rgba(128,128,128,0.1)', zeroline=False)
    fig3.update_yaxes(title_text="Percentage", secondary_y=False)
    fig3.update_yaxes(title_text="EA", secondary_y=True)

    # Apply the styling to fig3
    fig3 = update_plot_style(fig3)

    st.plotly_chart(fig3, use_container_width=True)