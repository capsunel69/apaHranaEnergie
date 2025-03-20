import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
from energy_dashboard.utils import update_plot_style, load_forecast_data

# Set page config (matching the main dashboard style)
st.set_page_config(
    layout="wide",
    page_title="EA Forecasts",
    initial_sidebar_state="expanded",
    page_icon="📈"
)

# Create the visualization
def create_forecast_plot(df, station):
    station_map = {
        'Station 1': 'Statia Jucu 1',
        'Station 2': 'Statia Jucu 2',
        'All': 'All'
    }
    station_name = station_map[station]
    
    # Get the values for the selected station
    y_values = df[station_name, 'y'] if ('y' in df[station_name]) else None
    yhat_values = df[station_name, 'yhat']
    yhat_lower = df[station_name, 'yhat_lower']
    yhat_upper = df[station_name, 'yhat_upper']

    fig = go.Figure()

    # Add historical values if they exist
    if y_values is not None:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=y_values,
                name='Historical Values',
                line=dict(color='blue')
            )
        )

    # Add forecast
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=yhat_values,
            name='$\\hat{y}$ (Forecast)',
            line=dict(color='red', dash='dash')
        )
    )

    # Add confidence bands
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=yhat_upper,
            fill=None,
            mode='lines',
            line_color='rgba(0,100,80,0)',
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=yhat_lower,
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,100,80,0)',
            name='Confidence Interval',
            fillcolor='rgba(0,100,80,0.2)'
        )
    )

    # Update plot style using the utility function
    fig = update_plot_style(fig)
    
    fig.update_layout(
        title=f'Energy Consumption Forecast - {station}',
        xaxis_title='Date',
        yaxis_title='Energy Consumption',
        height=600,
        showlegend=True,
        hovermode='x unified'
    )

    return fig

def main():
    st.title("📈 Energy Consumption Forecasts")
    
    # Load data
    df = load_forecast_data()
    
    # Station selector
    station = st.selectbox(
        "Select Station",
        options=['Station 1', 'Station 2', 'All'],
        index=0
    )
    
    # Create and display the forecast plot
    fig = create_forecast_plot(df, station)
    st.plotly_chart(fig, use_container_width=True)

    # Add some explanatory text
    st.markdown("""
    ### About this forecast
    - Blue line shows historical values (if available)
    - Red dashed line shows the forecast ($\\hat{y}$)
    - Shaded area represents the confidence interval (lower and upper bounds)
    """)

if __name__ == "__main__":
    main()
