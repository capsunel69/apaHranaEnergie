import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
from energy_dashboard.utils import update_plot_style, load_forecast_data, load_data

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
    
    # Load historical data and calculate EA
    historical_df = load_data()  # Load from tetarom_clean_merged_data
    
    # Filter historical data from Nov 1st until the start of forecast
    historical_df = historical_df[
        (historical_df.index >= '2024-11-01') & 
        (historical_df.index < df.index[0])  # Stop where forecast begins
    ]
    
    # Calculate EA for the selected station
    # Note: The columns are structured as (measurement_type, station_name)
    try:
        ea_plus = historical_df[('EA+', station_name)]
        ea_minus = historical_df[('EA-', station_name)]
        historical_ea = ea_plus - ea_minus

        fig = go.Figure()

        # Add historical EA values
        fig.add_trace(
            go.Scatter(
                x=historical_df.index,
                y=historical_ea,
                name='Historical EA',
                line=dict(color='blue')
            )
        )

        # Add forecast
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[station_name, 'yhat'],
                name='$\\hat{y}$ (Forecast)',
                line=dict(color='red', dash='dash')
            )
        )

        # Add confidence bands
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[station_name, 'yhat_upper'],
                fill=None,
                mode='lines',
                line_color='rgba(0,100,80,0)',
                showlegend=False
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[station_name, 'yhat_lower'],
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
    
    except KeyError as e:
        st.error(f"Could not find the required columns for {station_name}. Available columns: {historical_df.columns.tolist()}")
        return None

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
