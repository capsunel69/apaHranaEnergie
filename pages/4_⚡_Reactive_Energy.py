import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from energy_dashboard.utils import load_data, update_plot_style, COLORS

# Set page config
st.set_page_config(
    layout="wide",
    page_title="Energy Analysis",
    initial_sidebar_state="expanded",
    page_icon="⚡"
)

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please log in from the home page to access this content.")
    st.stop()

# Load data outside spinner to make it available for the whole session
@st.cache_data
def get_data():
    return load_data()

tetarom_df = get_data()

# Define limits
limit_x1 = 0.4843  # 48.43%
limit_x3 = 1.1691  # 116.91%

# Station selector (single one for both plots)
station = st.segmented_control(
    "Select Station",
    options=tetarom_df.columns.get_level_values('location').unique(),
    default=tetarom_df.columns.get_level_values('location').unique()[0]  # Set default to first station
)

# Wrap the data processing and visualization in the spinner
with st.spinner('Loading and processing data...'):
    # Filter data for selected station
    df = tetarom_df.loc[:, pd.IndexSlice[:, station]].copy().droplevel('location', axis=1)
    df['EA'] = df['EA+'] - df['EA-']
    df = df[['EA', 'ER+', 'ER-']]

    # First plot - Reactive Energy Usage
    st.header("Reactive Energy Usage")
    fig1 = px.line(df,
                   title=f"{station} Energy Usage",
                   template="plotly_white")

    fig1.update_layout(
        height=500,
        xaxis_title="Time",
        yaxis_title="Energy",
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        xaxis=dict(
            rangeslider=dict(
                visible=True,
                yaxis=dict(rangemode="auto")
            ),
            type="date"
        )
    )

    # Add traces to the rangeslider
    for column in df.columns:
        fig1.add_trace(
            go.Scatter(
                x=df.index,
                y=df[column],
                name=column,
                showlegend=False,
                xaxis='x',
                yaxis='y2'
            )
        )

    fig1 = update_plot_style(fig1)
    # Calculate percentages
    erpc = pd.DataFrame({
        'ER+ %age': df['ER+'] / df['EA'],
        'ER- %age': df['ER-'] / df['EA'],
        'EA': df['EA']
    })

    fig2 = make_subplots(specs=[[{"secondary_y": True}]])

    def find_intersection_point(x1, y1, x2, y2, limit):
        """Find the point where the line crosses the limit"""
        if pd.isna(y1) or pd.isna(y2):  # Handle NaN values
            return None
        
        if (y1 > limit and y2 < limit) or (y1 < limit and y2 > limit):
            # Linear interpolation to find exact crossing point
            try:
                dx = (x2 - x1).total_seconds()
                dy = y2 - y1
                slope = dy / dx
                dx_intersection = (limit - y1) / slope
                x_intersection = x1 + pd.Timedelta(seconds=float(dx_intersection))
                return x_intersection, limit
            except (ValueError, TypeError):
                return None
        return None

    # ER+ line with color segments based on limit
    erp_segments = []
    erp_dates = []
    erp_colors = []
    current_segment = []
    current_dates = []

    for i in range(len(erpc.index) - 1):
        date = erpc.index[i]
        next_date = erpc.index[i + 1]
        value = erpc['ER+ %age'].iloc[i]
        next_value = erpc['ER+ %age'].iloc[i + 1]
        
        if pd.isna(value) or pd.isna(next_value):
            if current_segment:
                erp_segments.append(current_segment)
                erp_dates.append(current_dates)
                erp_colors.append('red' if current_segment[-1] > limit_x1 else COLORS['ER+'])
                current_segment = []
                current_dates = []
            continue
        
        if not current_segment:
            current_segment.append(value)
            current_dates.append(date)
        
        intersection = find_intersection_point(date, value, next_date, next_value, limit_x1)
        
        if intersection:
            # Add the intersection point to current segment and start new segment
            current_segment.append(limit_x1)
            current_dates.append(intersection[0])
            erp_segments.append(current_segment)
            erp_dates.append(current_dates)
            erp_colors.append('red' if value > limit_x1 else COLORS['ER+'])
            
            # Start new segment from intersection point
            current_segment = [limit_x1, next_value]
            current_dates = [intersection[0], next_date]
        else:
            current_segment.append(next_value)
            current_dates.append(next_date)

    if current_segment:
        erp_segments.append(current_segment)
        erp_dates.append(current_dates)
        erp_colors.append('red' if current_segment[-1] > limit_x1 else COLORS['ER+'])

    # Add traces for ER+
    for segment, dates, color in zip(erp_segments, erp_dates, erp_colors):
        fig2.add_trace(
            go.Scatter(
                x=dates,
                y=segment,
                name="ER+ %age",
                line=dict(width=2, color=color),
                mode='lines',
                showlegend=(color == COLORS['ER+']),
                connectgaps=False
            ),
            secondary_y=False
        )

    # ER- line with color segments (similar logic)
    ern_segments = []
    ern_dates = []
    ern_colors = []
    current_segment = []
    current_dates = []

    for i in range(len(erpc.index) - 1):
        date = erpc.index[i]
        next_date = erpc.index[i + 1]
        value = erpc['ER- %age'].iloc[i]
        next_value = erpc['ER- %age'].iloc[i + 1]
        
        if pd.isna(value) or pd.isna(next_value):
            if current_segment:
                ern_segments.append(current_segment)
                ern_dates.append(current_dates)
                ern_colors.append('red' if current_segment[-1] > limit_x1 else COLORS['ER-'])
                current_segment = []
                current_dates = []
            continue
        
        if not current_segment:
            current_segment.append(value)
            current_dates.append(date)
        
        intersection = find_intersection_point(date, value, next_date, next_value, limit_x1)
        
        if intersection:
            # Add the intersection point to current segment and start new segment
            current_segment.append(limit_x1)
            current_dates.append(intersection[0])
            ern_segments.append(current_segment)
            ern_dates.append(current_dates)
            ern_colors.append('red' if value > limit_x1 else COLORS['ER-'])
            
            # Start new segment from intersection point
            current_segment = [limit_x1, next_value]
            current_dates = [intersection[0], next_date]
        else:
            current_segment.append(next_value)
            current_dates.append(next_date)

    if current_segment:
        ern_segments.append(current_segment)
        ern_dates.append(current_dates)
        ern_colors.append('red' if current_segment[-1] > limit_x1 else COLORS['ER-'])

    # Add traces for ER-
    for segment, dates, color in zip(ern_segments, ern_dates, ern_colors):
        fig2.add_trace(
            go.Scatter(
                x=dates,
                y=segment,
                name="ER- %age",
                line=dict(width=2, color=color),
                mode='lines',
                showlegend=(color == COLORS['ER-']),
                connectgaps=False
            ),
            secondary_y=False
        )

    # Add EA trace
    fig2.add_trace(
        go.Scatter(x=erpc.index, y=erpc['EA'], name="EA", 
                   line=dict(color=COLORS['EA'], width=1), 
                   opacity=0.1),
        secondary_y=True
    )

    # Add limit lines with names in legend
    fig2.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            name="Limit x1 (0.4843)",
            line=dict(color="red", dash="dash"),
            showlegend=True,
            legendgroup="limits"
        )
    )
    fig2.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            name="Limit x3 (1.1691)",
            line=dict(color="black", dash="dash"),
            showlegend=True,
            legendgroup="limits"
        )
    )

    # Add the actual limit lines (without legend entries)
    fig2.add_hline(y=limit_x1, line_dash="dash", line_color="red", showlegend=False)
    fig2.add_hline(y=limit_x3, line_dash="dash", line_color="black", showlegend=False)

    fig2.update_layout(
        height=500,
        hovermode='x unified',
        title=f"{station} Reactive Energy %age Usage",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            title_text="Data Series"
        ),
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date"
        )
    )

    fig2.update_yaxes(title_text="Percentage", secondary_y=False)
    fig2.update_yaxes(title_text="EA", secondary_y=True)

    fig2 = update_plot_style(fig2)

    # Replace date_input with slider
    min_date = pd.Timestamp(df.index.min().normalize().date())  # normalize() sets time to midnight
    max_date = pd.Timestamp(df.index.max().normalize().date())
    date_range = st.select_slider(
        "Select Date Range",
        options=[d.strftime('%Y-%m-%d') for d in pd.date_range(min_date, max_date, freq='D')],
        value=(min_date.strftime('%Y-%m-%d'), max_date.strftime('%Y-%m-%d'))
    )

    # Update both figures with the same x-axis range
    if len(date_range) == 2:  # Only update when both dates are selected
        fig1.update_layout(
            xaxis=dict(
                range=[f"{date_range[0]} 00:00:00", f"{date_range[1]} 23:59:59"]
            )
        )

        fig2.update_layout(
            xaxis=dict(
                range=[f"{date_range[0]} 00:00:00", f"{date_range[1]} 23:59:59"]
            )
        )

    # Display plots
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True) 