import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="UK Grid Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
@st.cache_data
def load_data():
    conn = sqlite3.connect("data/energy.db")
    df = pd.read_sql("SELECT * FROM intensity", conn)
    dg = pd.read_sql("SELECT * FROM generation", conn)
    conn.close()
    df['time_from'] = pd.to_datetime(df['time_from'])
    dg['time_from'] = pd.to_datetime(dg['time_from'])
    return df, dg

df, dg = load_data()

# ─────────────────────────────────────────
# SIDEBAR — FILTERS
# ─────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Flag_of_the_United_Kingdom.svg/320px-Flag_of_the_United_Kingdom.svg.png", width=80)
st.sidebar.title("UK Grid Intelligence")
st.sidebar.caption("Data: api.carbonintensity.org.uk")
st.sidebar.markdown("---")

min_date = df['time_from'].dt.date.min()
max_date = df['time_from'].dt.date.max()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start, end = date_range
    df = df[(df['time_from'].dt.date >= start) & (df['time_from'].dt.date <= end)]
    dg = dg[(dg['time_from'].dt.date >= start) & (dg['time_from'].dt.date <= end)]

st.sidebar.markdown("---")
st.sidebar.markdown("**Intensity Guide**")
st.sidebar.markdown("🟢 Very Low  < 50")
st.sidebar.markdown("🟡 Low       50–100")
st.sidebar.markdown("🟠 Moderate  100–200")
st.sidebar.markdown("🔴 High      > 200")

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.title("⚡ UK Grid Carbon Intelligence")
st.caption(f"Showing {len(df)} half-hour intervals · {df['time_from'].dt.date.min()} to {df['time_from'].dt.date.max()}")
st.markdown("---")

# ─────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

avg = df['intensity_actual'].mean()
low = df['intensity_actual'].min()
high = df['intensity_actual'].max()
forecast_error = (df['intensity_actual'] - df['intensity_forecast']).abs().mean()

k1.metric("Avg Carbon Intensity", f"{avg:.0f} gCO₂/kWh")
k2.metric("Cleanest Period",      f"{low} gCO₂/kWh")
k3.metric("Dirtiest Period",      f"{high} gCO₂/kWh")
k4.metric("Forecast Accuracy",    f"±{forecast_error:.1f} gCO₂/kWh")

st.markdown("---")

# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈 Carbon Intensity", "🔋 Generation Mix", "📊 Daily Patterns"])

# ── TAB 1: CARBON INTENSITY ──────────────
with tab1:
    st.subheader("Forecast vs Actual Carbon Intensity")

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=df['time_from'], y=df['intensity_forecast'],
        name='Forecast', line=dict(color='#636EFA', dash='dash'), opacity=0.7
    ))
    fig1.add_trace(go.Scatter(
        x=df['time_from'], y=df['intensity_actual'],
        name='Actual', line=dict(color='#EF553B'), fill='tonexty',
        fillcolor='rgba(239,85,59,0.08)'
    ))
    fig1.update_layout(
        xaxis_title="Time", yaxis_title="gCO₂/kWh",
        legend=dict(orientation="h", y=1.1),
        height=420, margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Grid Status Distribution")
    index_counts = df['intensity_index'].value_counts().reset_index()
    index_counts.columns = ['Status', 'Count']
    colour_map = {'very low': '#2ecc71', 'low': '#f1c40f',
                  'moderate': '#e67e22', 'high': '#e74c3c', 'very high': '#8e44ad'}
    fig2 = px.bar(index_counts, x='Status', y='Count',
                  color='Status', color_discrete_map=colour_map,
                  title="How often was the grid at each intensity level?")
    fig2.update_layout(showlegend=False, height=320, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig2, use_container_width=True)

# ── TAB 2: GENERATION MIX ───────────────
with tab2:
    st.subheader("UK Generation Mix Over Time")

    fuel_cols = [c for c in dg.columns if c not in ['time_from', 'time_to']]
    colour_map_fuels = {
        'wind':    '#00b4d8', 'solar':   '#f9c74f', 'hydro':   '#43aa8b',
        'biomass': '#90be6d', 'nuclear': '#9b5de5', 'gas':     '#f8961e',
        'coal':    '#4a4e69', 'oil':     '#6d6875', 'imports': '#a8dadc',
        'other':   '#adb5bd', 'pumped_storage': '#3a86ff'
    }

    fig3 = go.Figure()
    priority = ['coal', 'oil', 'gas', 'nuclear', 'imports',
                'biomass', 'hydro', 'wind', 'solar', 'pumped_storage', 'other']
    for fuel in priority:
        if fuel in dg.columns:
            fig3.add_trace(go.Scatter(
                x=dg['time_from'], y=dg[fuel],
                name=fuel.capitalize(),
                stackgroup='one',
                line=dict(width=0),
                fillcolor=colour_map_fuels.get(fuel, '#adb5bd')
            ))
    fig3.update_layout(
        yaxis_title="% of generation", xaxis_title="Time",
        legend=dict(orientation="h", y=-0.2, x=0),
        height=450, margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Average Generation Mix (full period)")
    avg_mix = dg[fuel_cols].mean().reset_index()
    avg_mix.columns = ['Fuel', 'Avg %']
    avg_mix = avg_mix.sort_values('Avg %', ascending=False)
    fig4 = px.bar(avg_mix, x='Fuel', y='Avg %',
                  color='Fuel', color_discrete_map=colour_map_fuels)
    fig4.update_layout(showlegend=False, height=320,
                       margin=dict(l=0, r=0, t=10, b=0),
                       yaxis_title="Average % of mix")
    st.plotly_chart(fig4, use_container_width=True)

# ── TAB 3: DAILY PATTERNS ───────────────
with tab3:
    st.subheader("Average Carbon Intensity by Hour of Day")
    st.caption("Reveals peak demand patterns — when is the grid dirtiest?")

    df['hour'] = df['time_from'].dt.hour
    hourly = df.groupby('hour')['intensity_actual'].mean().reset_index()
    hourly.columns = ['Hour', 'Avg Intensity']

    fig5 = px.bar(hourly, x='Hour', y='Avg Intensity',
                  color='Avg Intensity',
                  color_continuous_scale='RdYlGn_r',
                  labels={'Hour': 'Hour of Day', 'Avg Intensity': 'gCO₂/kWh'})
    fig5.update_layout(height=380, margin=dict(l=0, r=0, t=10, b=0),
                       coloraxis_showscale=False)
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Daily Average Intensity")
    df['date'] = df['time_from'].dt.date
    daily = df.groupby('date')['intensity_actual'].mean().reset_index()
    daily.columns = ['Date', 'Avg Intensity']

    fig6 = px.line(daily, x='Date', y='Avg Intensity',
                   markers=True,
                   color_discrete_sequence=['#EF553B'])
    fig6.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0),
                       yaxis_title="gCO₂/kWh")
    st.plotly_chart(fig6, use_container_width=True)

# ─────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────
st.markdown("---")
st.caption("Built by Johns Toms · Data: National Grid ESO via api.carbonintensity.org.uk · Stack: Python, SQLite, Streamlit, Plotly")
