import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import plotly.express as px
import plotly.graph_objects as go
import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Sales Forecaster",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PREMIUM DESIGN ---
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0f111a;
        color: #e0e6ed;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00e5ff !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #1a1d2d;
    }
    
    /* Cards/Metric containers */
    div[data-testid="metric-container"] {
        background-color: #1e2235;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #2d334a;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    div[data-testid="metric-container"] label {
        color: #8fa0bd !important;
    }
    
    div[data-testid="metric-container"] div {
        color: #00e5ff !important;
    }
</style>
""", unsafe_allow_html=True)

# --- APP HEADER ---
st.markdown("<h1>📈 AI-Powered Business Sales Forecasting & Demand Prediction</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #8fa0bd; font-size: 1.1rem;'>Analyze historical data and predict future demand with machine learning.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- DATA LOADING & CACHING ---
@st.cache_data
def load_data():
    # Load the specific file provided by the user
    df = pd.read_csv("updated_home_appliances_sales_dataset (1).csv")
    # Convert Date to datetime format
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
    # Drop rows with invalid dates
    df = df.dropna(subset=['Date'])
    # Sort by date
    df = df.sort_values('Date')
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("⚙️ System Controls")

# Filtering options
selected_product = st.sidebar.selectbox("Select Product Category", ["All"] + list(df['Product'].unique()))
selected_region = st.sidebar.selectbox("Select Region", ["All"] + list(df['Region'].unique()))

# Forecasting options
st.sidebar.markdown("---")
st.sidebar.header("🔮 Forecasting Horizon")
forecast_days = st.sidebar.slider("Days to Predict", min_value=7, max_value=90, value=30, step=1)

# --- FILTER DATA ---
filtered_df = df.copy()
if selected_product != "All":
    filtered_df = filtered_df[filtered_df['Product'] == selected_product]
if selected_region != "All":
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]

# Aggregate sales by Date
daily_sales = filtered_df.groupby('Date').agg({
    'Sales': 'sum',
    'no of units sold': 'sum'
}).reset_index()

if daily_sales.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# --- METRICS DASHBOARD ---
col1, col2, col3, col4 = st.columns(4)
total_revenue = daily_sales['Sales'].sum()
total_units = daily_sales['no of units sold'].sum()
avg_daily_sales = daily_sales['Sales'].mean()

with col1:
    st.metric("Total Historical Revenue", f"${total_revenue:,.0f}")
with col2:
    st.metric("Total Units Sold", f"{total_units:,.0f}")
with col3:
    st.metric("Avg Daily Revenue", f"${avg_daily_sales:,.0f}")
with col4:
    st.metric("Data Points (Days)", len(daily_sales))

st.markdown("<br>", unsafe_allow_html=True)

# --- HISTORICAL DATA VISUALIZATION ---
st.subheader("📊 Historical Sales Trend")

fig_hist = px.line(daily_sales, x='Date', y='Sales', 
                   title=f"Actual Sales Over Time",
                   color_discrete_sequence=['#00e5ff'],
                   template="plotly_dark")
fig_hist.update_layout(
    plot_bgcolor='#1a1d2d',
    paper_bgcolor='#0f111a',
    xaxis_title="Date",
    yaxis_title="Total Sales ($)",
    hovermode="x unified"
)
st.plotly_chart(fig_hist, use_container_width=True)

# --- MACHINE LEARNING MODEL ---
st.markdown("---")
st.subheader("🧠 AI Demand Prediction")

with st.spinner("Training Artificial Intelligence Model..."):
    # Feature Engineering for Time Series
    # We will use Date features to train a Random Forest Regressor
    ml_data = daily_sales.copy()
    ml_data['Year'] = ml_data['Date'].dt.year
    ml_data['Month'] = ml_data['Date'].dt.month
    ml_data['Day'] = ml_data['Date'].dt.day
    ml_data['DayOfWeek'] = ml_data['Date'].dt.dayofweek
    ml_data['DayOfYear'] = ml_data['Date'].dt.dayofyear
    
    # Define features and target
    X = ml_data[['Year', 'Month', 'Day', 'DayOfWeek', 'DayOfYear']]
    y = ml_data['Sales']
    
    # Train the Model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Generate Future Dates
    last_date = ml_data['Date'].max()
    future_dates = [last_date + datetime.timedelta(days=i) for i in range(1, forecast_days + 1)]
    
    future_df = pd.DataFrame({'Date': future_dates})
    future_df['Year'] = future_df['Date'].dt.year
    future_df['Month'] = future_df['Date'].dt.month
    future_df['Day'] = future_df['Date'].dt.day
    future_df['DayOfWeek'] = future_df['Date'].dt.dayofweek
    future_df['DayOfYear'] = future_df['Date'].dt.dayofyear
    
    # Predict
    future_X = future_df[['Year', 'Month', 'Day', 'DayOfWeek', 'DayOfYear']]
    future_predictions = model.predict(future_X)
    future_df['Predicted_Sales'] = future_predictions
    
    # Calculate expected future revenue
    expected_future_revenue = future_df['Predicted_Sales'].sum()

# Display prediction metrics
pred_col1, pred_col2 = st.columns(2)
with pred_col1:
    st.info(f"**Predicted Total Revenue (Next {forecast_days} days):** ${expected_future_revenue:,.0f}")
with pred_col2:
    st.success(f"**AI Engine Status:** Trained successfully on {len(ml_data)} data points.")

# --- FORECAST VISUALIZATION ---
# Combine historical and future data for plotting
plot_hist = daily_sales[['Date', 'Sales']].copy()
plot_hist['Type'] = 'Historical'

plot_future = future_df[['Date', 'Predicted_Sales']].copy()
plot_future.rename(columns={'Predicted_Sales': 'Sales'}, inplace=True)
plot_future['Type'] = 'Forecast (AI Predicted)'

combined_df = pd.concat([plot_hist, plot_future])

# Plotly Graph showing Historical + Forecast
fig_pred = go.Figure()

# Add Historical Line
fig_pred.add_trace(go.Scatter(
    x=plot_hist['Date'], 
    y=plot_hist['Sales'],
    mode='lines',
    name='Historical Sales',
    line=dict(color='#00e5ff', width=2)
))

# Add Forecast Line
fig_pred.add_trace(go.Scatter(
    x=plot_future['Date'], 
    y=plot_future['Sales'],
    mode='lines',
    name=f'AI Forecast ({forecast_days} Days)',
    line=dict(color='#ff0055', width=2, dash='dot')
))

fig_pred.update_layout(
    title=f"Sales Forecast for Next {forecast_days} Days",
    template="plotly_dark",
    plot_bgcolor='#1a1d2d',
    paper_bgcolor='#0f111a',
    xaxis_title="Date",
    yaxis_title="Sales ($)",
    hovermode="x unified",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)

st.plotly_chart(fig_pred, use_container_width=True)

# --- DATA EXPORT ---
st.markdown("---")
st.subheader("📥 Export Predictions")
st.markdown("Download the AI-generated forecast data for your business reports.")

csv_export = future_df[['Date', 'Predicted_Sales']].to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Forecast as CSV",
    data=csv_export,
    file_name=f'ai_sales_forecast_{forecast_days}_days.csv',
    mime='text/csv',
)
