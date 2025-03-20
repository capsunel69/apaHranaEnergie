import pandas as pd
import streamlit as st

COLORS = {
    'EA+': '#1f77b4',     # blue
    'EA-': '#ff7f0e',     # orange
    'ER+': '#2ca02c',      # green
    'Total': '#d62728',     # red
    'ER-': '#9467bd',     # purple
    'EA': '#1f77b4'    # blue
}

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
    if period == "Day (6H)" or period == "6-hours":
        return df.resample('6h').sum()
    elif period == "Day":
        return df.resample('d').sum()
    elif period == "Week":
        return df.resample('W').sum()
    elif period == "Month":
        return df.resample('ME').sum()
    else:
        raise ValueError(f"Invalid period: {period}")

def update_plot_style(fig, color_map=COLORS):
    # Check if dark mode is enabled by checking the background color
    is_dark_mode = st.get_option("theme.backgroundColor") == "#0E1117"
    
    # Set legend background and text color based on theme
    # For dark mode: very dark background with 0.9 opacity, white text
    # For light mode: white background with 0.8 opacity, black text
    legend_bgcolor = 'rgba(15,15,15,0.9)' if is_dark_mode else 'rgba(255,255,255,0.8)'
    legend_font_color = '#FFFFFF' if is_dark_mode else '#000000'
    
    fig.update_layout(
        font_family="sans-serif",
        title_font_size=20,
        margin=dict(l=50, r=20, t=80, b=20),
        legend=dict(
            borderwidth=1,
            font=dict(
                size=10,
                color=legend_font_color
            ),
            title=dict(
                font=dict(
                    color=legend_font_color
                )
            ),
            bgcolor=legend_bgcolor
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='#2c3e50',
            activecolor='#1f77b4'
        ),
        modebar_remove=[
            'select2d', 
            'lasso2d', 
            'autoScale2d',
            'hoverCompareCartesian'
        ],
        modebar_orientation='v',
        modebar_add=['hoverclosest']
    )
    
    for trace in fig.data:
        if trace.name in color_map:
            trace.line.color = color_map[trace.name]
            if hasattr(trace, 'marker'):
                trace.marker.color = color_map[trace.name]
    
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

@st.cache_data
def load_data():
    data_path = 'data/tetarom_clean_merged_data.feather'
    try:
        tetarom_df = pd.read_feather(data_path)
        tetarom_df.columns = tetarom_df.columns.map(strip_unit_tup)
        return tetarom_df
    except FileNotFoundError:
        st.error(f"Data file not found: {data_path}")
        st.info("Please ensure the data file exists in the correct location.")
        return pd.DataFrame()  # Return empty DataFrame

@st.cache_data
def load_forecast_data():
    data_path = 'data/tetarom_ea_forecasts.feather'
    try:
        forecast_df = pd.read_feather(data_path)
        return forecast_df
    except FileNotFoundError:
        st.error(f"Forecast data file not found: {data_path}")
        st.info("Please ensure the forecast data file exists in the correct location.")
        return pd.DataFrame()  # Return empty DataFrame