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

# Set page config
st.set_page_config(layout="wide", page_title="Energy Dashboard")

# Custom CSS for better aesthetics
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2 {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .filter-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

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
st.header("Raw Overview")

# Controls in a container above the plot
with st.container():
    col1, col2 = st.columns([1, 2])
    with col1:
        resample_period = st.selectbox(
            "Aggregation Period",
            ["Day", "Week", "Month"],
            index=1
        )
    with col2:
        # Get unique stations
        stations = tetarom_df.columns.get_level_values('location').unique()
        selected_stations = st.multiselect(
            "Filter Stations",
            options=stations,
            default=stations,  # By default, show all stations
            help="Select one or more stations to display"
        )

# Raw overview plot with resampling
flat_df = tetarom_df.copy()
flat_df.columns = [f"{col[0]} - {col[1]}" for col in tetarom_df.columns]

# Filter columns based on selected stations
if selected_stations:
    selected_cols = [col for col in flat_df.columns if any(station in col for station in selected_stations)]
    flat_df = flat_df[selected_cols]

# Apply resampling only for the overview plot
resampled_df = resample_data(flat_df, resample_period)

# Convert kWh to MWh
resampled_df = resampled_df / 1000  # Convert all values from kWh to MWh

# Convert values to MWh if they're large enough
def format_energy_value(value):
    if abs(value) >= 1000:
        return f"{value/1000:.1f} MWh"
    return f"{value:.1f} kWh"

fig1 = px.line(resampled_df, 
               title=f"Energy Consumption Overview ({resample_period}ly)",
               template="plotly_white")

fig1.update_layout(
    height=600,
    showlegend=True,
    xaxis_title="Time",
    yaxis_title="Energy Consumption (MWh)",
    hovermode='x unified',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor='rgba(255,255,255,0.8)'
    )
)

# Update y-axis to show values in MWh
fig1.update_yaxes(
    tickformat=".1f",
    ticksuffix=" MWh",
    gridcolor='rgba(128,128,128,0.1)', 
    zeroline=False
)

# Update hover template to show proper units
fig1.update_traces(
    hovertemplate="%{y:.1f} MWh<br>%{x}<extra></extra>"
)

fig1.update_xaxes(gridcolor='rgba(128,128,128,0.1)', zeroline=False)
st.plotly_chart(fig1, use_container_width=True)

# Station-specific analysis
st.header("Station Analysis")

# Station selector in a container above the plot
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    station = st.selectbox(
        "Select Station",
        tetarom_df.columns.get_level_values('location').unique()
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Filter data for selected station (using original non-resampled data)
df = tetarom_df.loc[:, pd.IndexSlice[:, station]].copy().droplevel('location', axis=1)
df['EA'] = df['EA+'] - df['EA-']
df = df[['EA', 'ER+', 'ER-']]

# Station consumption plot (no resampling)
fig2 = px.line(df,
               title=f"{station} Energy Consumption",  # Removed resampling period from title
               template="plotly_white")
fig2.update_layout(
    height=600,
    showlegend=True,
    xaxis_title="Time",
    yaxis_title="Energy",
    hovermode='x unified',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
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
st.plotly_chart(fig2, use_container_width=True)

# Reactive energy analysis (using same non-resampled data)
st.header("Reactive Energy Analysis")

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
fig3.add_hline(y=limit_x1, line_dash="dash", line_color="gray", name="Limit x1")
fig3.add_hline(y=limit_x3, line_dash="dash", line_color="black", name="Limit x3")

fig3.update_layout(
    title=f"{station} Reactive Energy Percentage",  # Removed resampling period from title
    height=600,
    hovermode='x unified',
    template="plotly_white",
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
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

st.plotly_chart(fig3, use_container_width=True)

# Intra-week consumption analysis
st.header("Intra-Week Consumption")

# Station selector for intra-week analysis
with st.container():
    intra_week_station = st.selectbox(
        "Select Station for Intra-Week Analysis",
        ["Statia Jucu 1", "Statia Jucu 2", "Total"],
        key="intra_week_selector"
    )

# Debug prints
st.write("Debugging information:")

# Prepare data for intra-week analysis
df = tetarom_df.copy()
if intra_week_station != "Total":
    df = df.loc[:, pd.IndexSlice[:, intra_week_station]].copy().droplevel('location', axis=1)
    df = df['EA+']  # Just using EA+ for consumption as a Series
else:
    # Calculate total across all stations
    df = df.loc[:, pd.IndexSlice['EA+', :]].copy()
    df = df.sum(axis=1)

st.write(f"Data shape after initial selection: {df.shape}")
st.write(f"First few values: {df.head()}")

# Create week-based index
df_week = pd.DataFrame(index=df.index)
df_week['value'] = df
df_week['week'] = df_week.index.to_period('W')
# Add day of week and time components
df_week['day_of_week'] = df_week.index.dayofweek  # Monday=0, Sunday=6
df_week['time_of_day'] = df_week.index.time
# Combine day and time for x-axis
df_week['time_in_week'] = pd.to_timedelta(df_week['day_of_week'], unit='D') + \
                         pd.to_timedelta(df_week['time_of_day'].astype(str))

# Pivot the data
weekly_pattern = df_week.pivot_table(
    values='value',
    index='time_in_week',
    columns='week',
    aggfunc='mean'
)

# Create the plot
fig4 = go.Figure()

# Add a line for each week
for column in weekly_pattern.columns:
    fig4.add_trace(
        go.Scatter(
            x=weekly_pattern.index.total_seconds()/3600/24,  # Convert to days
            y=weekly_pattern[column],
            name=column.strftime('%Y-%m-%d'),
            mode='lines',
            line=dict(width=1)
        )
    )

fig4.update_layout(
    title=f"Intra-Week Consumption Pattern - {intra_week_station}",
    height=600,
    xaxis_title="Day of Week",
    yaxis_title="Energy Consumption (kWh)",
    hovermode='x unified',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    legend=dict(
        title="Week Starting",
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

st.plotly_chart(fig4, use_container_width=True)