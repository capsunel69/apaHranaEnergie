import pandas as pd
import streamlit as st

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

def update_plot_style(fig):
    fig.update_layout(
        font_family="sans-serif",
        title_font_size=20,
        margin=dict(l=50, r=20, t=80, b=20),
        legend=dict(
            borderwidth=1,
            font=dict(size=10)
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
    data_path = 'tetarom_clean_merged_data.feather'
    tetarom_df = pd.read_feather(data_path)
    tetarom_df.columns = tetarom_df.columns.map(strip_unit_tup)
    return tetarom_df 