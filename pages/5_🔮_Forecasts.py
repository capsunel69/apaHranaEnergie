import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
from energy_dashboard.utils import update_plot_style, load_forecast_data, load_data


# Set page config (matching the main dashboard style)
st.set_page_config(
    layout="wide",
    page_title="Forecasts",
    initial_sidebar_state="expanded",
    page_icon="📈"
)

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in from the home page to access this content.")
    st.stop()

# Create the visualization
def create_forecast_plot(df, station):
    station_name = station
    
    # Load historical data and calculate EA
    historical_df = load_data()  # Load from tetarom_clean_merged_data
    
    # Filter historical data from Nov 1st until the start of forecast
    historical_df = historical_df[
        (historical_df.index >= '2024-11-01') & 
        (historical_df.index <= df.index[0])
    ]
    
    try:
        # Calculate EA based on station selection
        if station_name == 'All':
            ea_plus_1 = historical_df[('EA+', 'Statia Jucu 1')]
            ea_minus_1 = historical_df[('EA-', 'Statia Jucu 1')]
            ea_plus_2 = historical_df[('EA+', 'Statia Jucu 2')]
            ea_minus_2 = historical_df[('EA-', 'Statia Jucu 2')]
            historical_ea = (ea_plus_1 - ea_minus_1) + (ea_plus_2 - ea_minus_2)
        else:
            ea_plus = historical_df[('EA+', station_name)]
            ea_minus = historical_df[('EA-', station_name)]
            historical_ea = ea_plus - ea_minus

        fig = go.Figure()

        # Add historical EA values
        fig.add_trace(
            go.Scatter(
                x=historical_df.index,
                y=historical_ea,
                name='y',
                line=dict(color='blue')
            )
        )

        # Add confidence interval (shaded area only)
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[(station_name, 'yhat_upper')],
                name='Confidence Interval',
                line=dict(color='rgba(0,0,0,0)'),  # Invisible line
                showlegend=False
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[(station_name, 'yhat_lower')],
                name='Confidence Interval',
                line=dict(color='rgba(0,0,0,0)'),  # Invisible line
                fill='tonexty',  # Fill between this trace and the previous one
                fillcolor='rgba(68, 68, 68, 0.1)',
                showlegend=True
            )
        )

        # Add forecast line
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[(station_name, 'yhat')],
                name='ŷ',
                line=dict(color='orange'),
                mode='lines'
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
            hovermode='x unified',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255,255,255,0.8)',
                title=dict(
                    text='EA Values',
                    side='top'
                )
            ),
            xaxis=dict(
                type="date"
            )
        )

        # Update hover template
        fig.update_traces(
            hovertemplate="%{y:,.1f}<br>%{x}<extra></extra>"
        )

        return fig
    
    except KeyError as e:
        st.error(f"Could not find the required columns for {station_name}. Available columns: {df.columns.tolist()}")
        return None

def main():
    st.title("📈 Energy Consumption Forecasts")
    
    # Load data
    df = load_forecast_data()
    
    # Updated station selector with direct station names
    station = st.segmented_control(
        "Select Station",
        options=['Statia Jucu 1', 'Statia Jucu 2', 'All'],
        default='Statia Jucu 1',
        label_visibility='hidden'
    )
    
    # Create and display the forecast plot
    fig = create_forecast_plot(df, station)
    st.plotly_chart(fig, use_container_width=True)

    # Add some explanatory text
    st.markdown("""
### The model

$\\hat{y}(t) = g(t) + s(t) + h(t) + \\epsilon_t$

We use a decomposable time series model with three main model components:  
- $g(t)$ is the logistic trend function which models non-periodic changes in the value of the time series.
- $s(t)$ fourier-based seasonality which models periodic changes (daily, weekly, yearly).
- $h(t)$ represents the effects of holidays which occur on potentially irregular schedules over
one or more days.
    - *Not done yet. Pending custom holiday schedule*.
- $\\epsilon_t$ represents any idiosyncratic changes which are not accommodated by the model.
    """)

if __name__ == "__main__":
    main()
