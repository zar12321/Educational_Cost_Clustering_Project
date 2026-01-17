# dashboard_app.py
import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from sqlalchemy import create_engine
from urllib.parse import quote_plus

load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="EduCost",
    layout="wide",
    page_icon="🎓"
)

# ================================================
# SUPABASE DATABASE CONNECTION SETUP
# ================================================
SUPABASE_DB_HOST = os.getenv("SUPABASE_DB_HOST", "aws-1-ap-south-1.pooler.supabase.com")
SUPABASE_DB_PORT = os.getenv("SUPABASE_DB_PORT", "5432")
SUPABASE_DB_NAME = os.getenv("SUPABASE_DB_NAME", "postgres")
SUPABASE_DB_USER = os.getenv("SUPABASE_DB_USER", "postgres.qeoluyijzkvwbmggphlk")
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", "ZarSupAZup03*_")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qeoluyijzkvwbmggphlk.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_dAH6-aWikrtc2FrQ9Kiidg_EVyt9jZb")

# Escape special characters in password for URL
escaped_password = quote_plus(SUPABASE_DB_PASSWORD)

ENGINE_URL = (
    f"postgresql+psycopg://"
    f"{SUPABASE_DB_USER}:{escaped_password}"
    f"@{SUPABASE_DB_HOST}:{SUPABASE_DB_PORT}/{SUPABASE_DB_NAME}"
)

try:
    engine = create_engine(
        ENGINE_URL,
        pool_pre_ping=True,
        connect_args={"sslmode": "require"},
    )
except Exception as e:
    st.error(f"❌ Database connection error: {e}")
    st.info("Please check your Supabase credentials in Streamlit Secrets")
    engine = None

# ================================================
# DATA LOADING FUNCTION WITH CACHING
# ================================================
@st.cache_data(ttl=300)
def load_data():
    if engine is None:
        st.error("Database engine is not initialized. Cannot load data.")
        return pd.DataFrame()

    try:
        query = """
        SELECT 
            g.*,
            e.continent,
            e.field,
            c.cluster_label,
            c.cluster_name
        FROM study_cost_gold g
        LEFT JOIN study_cost_enriched e
            ON g.id = e.id
        LEFT JOIN study_cost_clustered c
            ON g.id = c.id;
        """
        df = pd.read_sql(query, engine)

        df = df.rename(columns={
            "cluster_label": "Cluster_Label",
            "cluster_name": "cluster_name",
        })
        return df

    except Exception as e:
        st.error(f"❌ Error loading data from Supabase: {e}")
        return pd.DataFrame()

        
        # Fallback: Try alternative table names (case-sensitive variations)
        try:
            st.info("⚠️ Trying alternative table names...")
            query = """
            SELECT g.*,
                   c.cluster_label,
                   c.cluster_name
            FROM "study_cost_gold" g
            LEFT JOIN "study_cost_clustered" c
              ON g.id = c.id;
            """
            df = pd.read_sql(query, engine)
            
            df = df.rename(columns={
                'cluster_label': 'Cluster_Label',
                'cluster_name': 'cluster_name'
            })
            
            st.success(f"✅ Successfully loaded {len(df)} records using quoted table names")
            return df
            
        except Exception as e2:
            st.error(f"❌ Alternative query also failed: {str(e2)}")
            
            # List available tables for debugging
            try:
                tables_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
                """
                tables = pd.read_sql(tables_query, engine)
                st.info(f"📋 Available tables in database: {list(tables['table_name'])}")
            except:
                pass
            
            return pd.DataFrame()

# Load the data
df = load_data()

# Check if data was loaded successfully
if df.empty:
    st.error("""
    ❌ No data loaded from database. Possible issues:
    1. Check your Supabase credentials in the .env file
    2. Verify that the tables 'study_cost_gold' and 'study_cost_clustered' exist
    3. Check your internet connection
    4. Verify that the Supabase project is running
    """)
    st.stop()

# ================================================
# CUSTOM CSS FOR ENHANCED STYLING
# ================================================
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        font-size: 7.5rem;
        color: #1E3A8A;
        margin-bottom: 1rem;
        padding-top: 1rem;
        text-align: center;
    }
    
    /* Sub-header styling */
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E5E7EB;
    }
    
    /* Metric card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        margin-top: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F3F4F6;
        border-radius: 5px 5px 0px 0px;
        gap: 1px;
        padding: 12px 20px;
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4F46E5;
        color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

        .program-card {
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3498DB;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        background: #F9FAFB;
        color: #1F2937; /* Default light mode text color */
    }
    
    /* DARK MODE - Background lebih gelap (hitam) */
    [data-theme="dark"] .program-card {
        background: #0F172A !important; /* Warna hitam biru tua - lebih gelap */
        color: #E2E8F0 !important; /* Abu-abu sangat terang (hampir putih) */
        border-left-color: #3498DB !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); /* Bayangan lebih gelap */
    }
    
    /* Pastikan semua teks dalam kartu terlihat di dark mode */
    [data-theme="dark"] .program-card h4,
    [data-theme="dark"] .program-card p,
    [data-theme="dark"] .program-card strong {
        color: #E2E8F0 !important; /* Warna teks konsisten */
    }
    
    /* Warna khusus untuk teks cluster di dark mode - harus tetap terlihat */
    [data-theme="dark"] .program-card span[style*="color: #10B981"] {
        color: #10B981 !important; /* Hijau untuk Cheap - tetap cerah */
    }
    
    [data-theme="dark"] .program-card span[style*="color: #F59E0B"] {
        color: #F59E0B !important; /* Oranye untuk Medium - tetap cerah */
    }
    
    [data-theme="dark"] .program-card span[style*="color: #EF4444"] {
        color: #EF4444 !important; /* Merah untuk Expensive - tetap cerah */
    }
    
    /* Specific fix for program A card (blue border) */
    .program-card[style*="border-color: #3498DB"] {
        border-left-color: #3498DB !important;
    }
    
    /* Specific fix for program B card (orange border) */
    .program-card[style*="border-color: #F39C12"] {
        border-left-color: #F39C12 !important;
    }
    
    /* Filter section styling */
    .filter-section {
        padding: 15px;
        background-color: #F9FAFB;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #E5E7EB;
    }
    
    /* Section title styling */
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 15px;
    }
    
    /* KPI container styling */
    .kpi-container {
        margin-bottom: 2rem;
        background: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Cluster card styling */
    .cluster-card {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: white;
        transition: transform 0.3s ease;
    }
    
    .cluster-card:hover {
        transform: translateY(-5px);
    }
    
    /* Center text utility */
    .center-text {
        text-align: center;
    }
    
    /* Warning message styling */
    .warning-message {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
</style><style>
    /* Main header styling */
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        margin-bottom: 1rem;
        padding-top: 1rem;
        text-align: center;
    }
    
    /* Sub-header styling */
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #E5E7EB;
    }
    
    /* Metric card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* ========== TAB HEADER FIX - INI YANG DIPERBAIKI ========== */
    /* Tab container */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        margin-top: 1rem;
    }
    
    /* Inactive tabs in LIGHT MODE */
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F3F4F6 !important; /* Light gray */
        border-radius: 5px 5px 0px 0px;
        gap: 1px;
        padding: 12px 20px;
        font-weight: 600;
        margin-bottom: 5px;
        color: #1F2937 !important; /* Dark text for light mode */
        border: 1px solid #E5E7EB !important;
    }
    
    /* Inactive tabs in DARK MODE */
    [data-theme="dark"] .stTabs [data-baseweb="tab"] {
        background-color: #374151 !important; /* Dark gray */
        color: #FFFFFF !important; /* White text for dark mode */
        border: 1px solid #4B5563 !important;
    }
    
    /* Active tab (selected) - SAME FOR BOTH MODES */
    .stTabs [aria-selected="true"] {
        background-color: #4F46E5 !important; /* Blue */
        color: white !important; /* White text */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #4F46E5 !important;
    }
    
    /* Hover effect for inactive tabs */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #E5E7EB !important;
    }
    
    [data-theme="dark"] .stTabs [data-baseweb="tab"]:hover {
        background-color: #4B5563 !important;
    }
    
    /* Program card styling */
    .program-card {
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        background: #F9FAFB;
    }
    
    /* Filter section styling */
    .filter-section {
        padding: 15px;
        background-color: #F9FAFB;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #E5E7EB;
    }
    
    /* Section title styling */
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 15px;
    }
    
    /* KPI container styling */
    .kpi-container {
        margin-bottom: 2rem;
        background: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Cluster card styling */
    .cluster-card {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: white;
        transition: transform 0.3s ease;
    }
    
    .cluster-card:hover {
        transform: translateY(-5px);
    }
    
    /* Center text utility */
    .center-text {
        text-align: center;
    }
    
    /* Warning message styling */
    .warning-message {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ================================================
# SIDEBAR FILTERS SECTION
# ================================================
st.sidebar.title("Dashboard Filters")
st.sidebar.markdown("---")

# Initialize session state for cascade filters
if 'cascade_filters' not in st.session_state:
    st.session_state.cascade_filters = {
        'continent': None,
        'country': None,
        'university': None
    }

# continent filter
st.sidebar.markdown("### 🌍 Select Continent")
continent_options = sorted([x for x in df["continent"].dropna().unique()])
selected_continent = st.sidebar.selectbox(
    "Choose a Continent",
    [""] + continent_options,
    key="sidebar_continent",
    index=0
)

# country filter - depends on selected continent
st.sidebar.markdown("### 🏳️ Select Country")
if selected_continent:
    country_options = sorted(df[df["continent"] == selected_continent]["country"].dropna().unique())
else:
    country_options = sorted([x for x in df["country"].dropna().unique()])

selected_country = st.sidebar.selectbox(
    "Choose a Country",
    [""] + country_options,
    key="sidebar_country",
    index=0
)

# university filter - depends on selected country
st.sidebar.markdown("### 🎓 Select University")
if selected_country:
    university_options = sorted(df[df["country"] == selected_country]["university"].dropna().unique())
elif selected_continent:
    university_options = sorted(df[df["continent"] == selected_continent]["university"].dropna().unique())
else:
    university_options = sorted([x for x in df["university"].dropna().unique()])

selected_university = st.sidebar.selectbox(
    "Select a University",
    [""] + university_options,
    key="sidebar_university",
    index=0
)

# Additional filters section
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Additional Filters")

# Field of study filter
field_options = sorted([x for x in df["field"].dropna().unique()])
selected_fields = st.sidebar.multiselect("Field of Study", field_options)

# Study level filter
level_options = sorted([x for x in df["level"].dropna().unique()])
selected_levels = st.sidebar.multiselect("Study Level", level_options)

# Cost cluster filter
cluster_options = ["Cheap", "Medium", "Expensive"]
selected_clusters = st.sidebar.multiselect("Cost Cluster", cluster_options)

# ================================================
# APPLY FILTERS TO DATAFRAME
# ================================================
# Start with a copy of the original dataframe
filtered_df = df.copy()

# Apply cascade filters
if selected_continent:
    filtered_df = filtered_df[filtered_df["continent"] == selected_continent]
if selected_country:
    filtered_df = filtered_df[filtered_df["country"] == selected_country]
if selected_university:
    filtered_df = filtered_df[filtered_df["university"] == selected_university]

# Apply additional filters
if selected_fields:
    filtered_df = filtered_df[filtered_df["field"].isin(selected_fields)]
if selected_levels:
    filtered_df = filtered_df[filtered_df["level"].isin(selected_levels)]
if selected_clusters:
    filtered_df = filtered_df[filtered_df["cluster_name"].isin(selected_clusters)]

# ================================================
# MAIN DASHBOARD HEADER AND KPIs
# ================================================
st.markdown('<h1 class="main-header">Educational Cost Intelligence Dashboard</h1>', unsafe_allow_html=True)
st.markdown("Compare overseas study costs, explore patterns across fields & regions, and segment programs into cost clusters.")

st.markdown("<br>", unsafe_allow_html = True)

# Key Performance Indicators (KPIs)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total programs",
        f"{len(filtered_df):,}",
        delta=f"{len(filtered_df) - len(df)}" if len(filtered_df) != len(df) else None
    )

with col2:
    avg_total_cost = filtered_df['total_study_cost_usd'].mean()
    overall_avg_cost = df['total_study_cost_usd'].mean()
    cost_difference = avg_total_cost - overall_avg_cost
    st.metric(
        "Avg Total Cost",
        f"${avg_total_cost:,.0f}",
        delta=f"{cost_difference:,.0f}" if cost_difference != 0 else None
    )

with col3:
    median_rent = filtered_df['rent_usd'].median()
    overall_rent = df['rent_usd'].median()
    rent_difference = median_rent - overall_rent
    st.metric(
        "Median Rent/Month",
        f"${median_rent:,.0f}",
        delta=f"{rent_difference:,.0f}" if rent_difference != 0 else None
    )

with col4:
    avg_yearly_cost = filtered_df['cost_per_year_usd'].mean()
    overall_yearly_cost = df['cost_per_year_usd'].mean()
    yearly_cost_difference = avg_yearly_cost - overall_yearly_cost
    st.metric(
        "Avg Cost/Year",
        f"${avg_yearly_cost:,.0f}",
        delta=f"{yearly_cost_difference:,.0f}" if yearly_cost_difference != 0 else None
    )

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")

# ================================================
# MAIN TABS DEFINITION
# ================================================
tabs = st.tabs(["Overview", "Top Rankings", "Compare Programs", "Cost Clusters", "Data Explorer"])

# ================================================
# TAB 1: OVERVIEW
# ================================================
with tabs[0]:
    st.markdown('<h2 class="sub-header">Global Cost Overview</h2>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html = True)
    
    # First row: continent Analysis and Cluster Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌍 Average Cost per Year by Continent")
        # Calculate average cost per year by continent
        continent_avg = filtered_df.groupby("continent")["cost_per_year_usd"].mean().sort_values(ascending=True).reset_index()
        
        # Create horizontal bar chart
        fig = px.bar(
            continent_avg,
            y="continent",
            x="cost_per_year_usd",
            orientation='h',
            color="cost_per_year_usd",
            color_continuous_scale='Viridis',
            labels={'cost_per_year_usd': 'Average Cost/Year (USD)'},
            text_auto='.0f'
        )
        fig.update_layout(
            height=400,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Cost Distribution by Cluster")
        # Calculate cluster distribution
        cluster_distribution = filtered_df['cluster_name'].value_counts().reset_index()
        cluster_distribution.columns = ['Cluster', 'Count']
        
        # Define cluster colors
        cluster_colors = {'Cheap': '#10B981', 'Medium': '#F59E0B', 'Expensive': '#EF4444'}
        
        # Create pie chart
        fig = px.pie(
            cluster_distribution,
            values='Count',
            names='Cluster',
            color='Cluster',
            color_discrete_map=cluster_colors,
            hole=0.4
        )
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}"
        )
        fig.update_layout(
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Second row: Cost Composition Analysis
    st.markdown("#### 📈 Average Cost Composition by Cluster")
    
    # Prepare data for stacked bar chart
    cluster_composition = filtered_df.groupby('cluster_name').agg({
        'tuition_usd': 'mean',
        'total_living_cost_usd': 'mean',
        'total_insurance_cost_usd': 'mean',
        'visa_fee_usd': 'mean'
    }).reset_index()
    
    # Melt the dataframe for visualization
    cluster_composition_melted = cluster_composition.melt(
        id_vars='cluster_name',
        value_vars=['tuition_usd', 'total_living_cost_usd', 'total_insurance_cost_usd', 'visa_fee_usd'],
        var_name='Cost Type',
        value_name='Average Cost'
    )
    
    # Map cost type names to more readable format
    cost_type_mapping = {
        'tuition_usd': 'Tuition',
        'total_living_cost_usd': 'Living Cost',
        'total_insurance_cost_usd': 'Insurance',
        'visa_fee_usd': 'Visa Fee'
    }
    cluster_composition_melted['Cost Type'] = cluster_composition_melted['Cost Type'].map(cost_type_mapping)
    
    # Create stacked bar chart
    fig = px.bar(
        cluster_composition_melted,
        x='cluster_name',
        y='Average Cost',
        color='Cost Type',
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Bold,
        text_auto='.2f'
    )
    
    fig.update_layout(
        xaxis_title="Cost Cluster",
        yaxis_title="Average Cost (USD)",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

# ================================================
# TAB 2: TOP RANKINGS
# ================================================
with tabs[1]:
    st.markdown('<h2 class="sub-header">Top Rankings by Cost</h2>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html = True)
    # Configuration section for ranking options
    col_config1, col_config2 = st.columns(2)
    
    with col_config1:
        top_n = st.slider("Number of top entries to show", 5, 30, 10, key="top_n_slider")
    
    with col_config2:
        ranking_type = st.selectbox(
            "Rank by:",
            ["Total Study Cost", "Cost per Year", "Tuition Fee", "Living Cost"],
            key="ranking_type"
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Map ranking type to column name
    ranking_column_mapping = {
        "Total Study Cost": "total_study_cost_usd",
        "Cost per Year": "cost_per_year_usd", 
        "Tuition Fee": "tuition_usd",
        "Living Cost": "total_living_cost_usd",
    }
    rank_column = ranking_column_mapping[ranking_type]
    
    # program study Rankings
    st.markdown(f"#### 🎒 Top {top_n} Study Programs by {ranking_type}")

    program_ranking = (
        filtered_df.groupby("program")[rank_column]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    # Create bar chart for program rankings
    fig = px.bar(
        program_ranking,
        x="program",
        y=rank_column,
        color=rank_column,
        color_continuous_scale='RdYlGn_r',
        labels={rank_column: f'Average {ranking_type} (USD)'},
        text_auto='.0f'
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # city Rankings
    st.markdown(f"#### 🏙️ Top {top_n} Cities by {ranking_type}")
    
    city_ranking = (
        filtered_df.groupby("city")[rank_column]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    
    # Create bar chart for city rankings
    fig = px.bar(
        city_ranking,
        x="city",
        y=rank_column,
        color=rank_column,
        color_continuous_scale='RdYlGn_r',
        labels={rank_column: f'Average {ranking_type} (USD)'},
        text_auto='.0f'
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # country Rankings
    st.markdown(f"#### 🌎 Top {top_n} Countries by {ranking_type}")
    
    country_ranking = (
        filtered_df.groupby("country")[rank_column]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    
    # Create horizontal bar chart for country rankings
    fig = px.bar(
        country_ranking,
        y="country",
        x=rank_column,
        orientation='h',
        color=rank_column,
        color_continuous_scale='RdYlGn_r',
        labels={rank_column: f'Average {ranking_type} (USD)'},
        text_auto='.0f'
    )
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # university Rankings
    st.markdown(f"#### 🎓 Top {top_n} Universities by {ranking_type}")
    
    university_ranking = (
        filtered_df.groupby("university")[rank_column]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    
    # Create a formatted table for university rankings
    university_ranking_display = university_ranking.copy()
    university_ranking_display['Rank'] = range(1, len(university_ranking_display) + 1)
    university_ranking_display = university_ranking_display[['Rank', 'university', rank_column]]
    university_ranking_display[rank_column] = university_ranking_display[rank_column].apply(lambda x: f"${x:,.0f}")
    
    # Display university rankings as a table
    st.dataframe(
        university_ranking_display,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small"),
            "University": st.column_config.TextColumn("university", width="large"),
            rank_column: st.column_config.TextColumn(f"Avg {ranking_type}")
        },
        use_container_width=True,
        hide_index=True
    )

# ================================================
# TAB 3: COMPARE PROGRAMS
# ================================================
with tabs[2]:
    st.markdown('<h2 class="sub-header">Compare Study Programs</h2>', unsafe_allow_html=True)
    
    # Create two columns for program selection
    col_selection1, col_selection2 = st.columns(2)
    
    # Function to create cascade selectors for program selection
    def create_cascade_selectors(prefix):
        """
        Create cascade selectors for continent, country, university, program, and level.
        """
        st.markdown(f"### Program {prefix}")
        
        # Continent selection
        continent_list = sorted(filtered_df["continent"].dropna().unique())
        selected_continent = st.selectbox(
            f"Continent {prefix}",
            [""] + continent_list,
            key=f"continent_{prefix}",
            index=0
        )
        
        # Country selection based on continent
        if selected_continent:
            country_list = sorted(filtered_df[filtered_df["continent"] == selected_continent]["country"].dropna().unique())
        else:
            country_list = sorted(filtered_df["country"].dropna().unique())
        
        selected_country = st.selectbox(
            f"Country {prefix}",
            [""] + country_list,
            key=f"country_{prefix}",
            index=0
        )
        
        # University selection based on country
        if selected_country:
            university_list = sorted(filtered_df[filtered_df["country"] == selected_country]["university"].dropna().unique())
        elif selected_continent:
            university_list = sorted(filtered_df[filtered_df["continent"] == selected_continent]["university"].dropna().unique())
        else:
            university_list = sorted(filtered_df["university"].dropna().unique())
        
        selected_university = st.selectbox(
            f"University {prefix}",
            [""] + university_list,
            key=f"university_{prefix}",
            index=0
        )
        
        # Program selection based on university
        if selected_university:
            program_list = sorted(filtered_df[filtered_df["university"] == selected_university]["program"].dropna().unique())
        elif selected_country:
            program_list = sorted(filtered_df[filtered_df["country"] == selected_country]["program"].dropna().unique())
        elif selected_continent:
            program_list = sorted(filtered_df[filtered_df["continent"] == selected_continent]["program"].dropna().unique())
        else:
            program_list = sorted(filtered_df["program"].dropna().unique())
        
        selected_program = st.selectbox(
            f"Program {prefix}",
            [""] + program_list,
            key=f"program_{prefix}",
            index=0
        )
        
        # Level selection based on program
        if selected_program and selected_university:
            program_filtered = filtered_df[(filtered_df["university"] == selected_university) & 
                                          (filtered_df["program"] == selected_program)]
            level_list = sorted(program_filtered["level"].dropna().unique())
        elif selected_program:
            program_filtered = filtered_df[filtered_df["program"] == selected_program]
            level_list = sorted(program_filtered["level"].dropna().unique())
        else:
            level_list = sorted(filtered_df["level"].dropna().unique())
        
        selected_level = st.selectbox(
            f"Level {prefix}",
            [""] + level_list,
            key=f"level_{prefix}",
            index=0
        )
        
        return selected_continent, selected_country, selected_university, selected_program, selected_level
    
    # Create selectors for program A
    with col_selection1:
        continent_a, country_a, university_a, program_a, level_a = create_cascade_selectors("A")
    
    # Create selectors for program B
    with col_selection2:
        continent_b, country_b, university_b, program_b, level_b = create_cascade_selectors("B")
    
    # Function to get program data
    def get_program_data(continent, country, university, program, level):
        """
        Get program data, handling cases where there are multiple entries.
        """
        # Start with all filtered data
        data_subset = filtered_df.copy()
        
        # Apply filters if selected
        if continent:
            data_subset = data_subset[data_subset["continent"] == continent]
        if country:
            data_subset = data_subset[data_subset["country"] == country]
        if university:
            data_subset = data_subset[data_subset["university"] == university]
        if program:
            data_subset = data_subset[data_subset["program"] == program]
        if level:
            data_subset = data_subset[data_subset["level"] == level]
        
        if data_subset.empty:
            return None
        
        # Check for duplicate entries
        duplicate_count = len(data_subset)
        
        if duplicate_count > 1:
            # Calculate averages for numerical columns
            numerical_cols = data_subset.select_dtypes(include=['float64', 'int64']).columns
            
            aggregated_data = {}
            
            # For numerical columns, calculate mean
            for col in numerical_cols:
                if col in data_subset.columns:
                    aggregated_data[col] = data_subset[col].mean()
            
            # For categorical columns
            categorical_cols = data_subset.select_dtypes(include=['object']).columns
            
            for col in categorical_cols:
                if col in data_subset.columns:
                    unique_values = data_subset[col].dropna().unique()
                    if len(unique_values) == 1:
                        aggregated_data[col] = unique_values[0]
                    else:
                        most_common = data_subset[col].mode()
                        aggregated_data[col] = most_common.iloc[0] if not most_common.empty else unique_values[0]
            
            aggregated_data['duplicate_count'] = duplicate_count
            
            return aggregated_data
        else:
            return data_subset.iloc[0].to_dict()
    
    # Get program data if selected
    program_a_data = None
    program_b_data = None
    
    if program_a and university_a and level_a:
        program_a_data = get_program_data(continent_a, country_a, university_a, program_a, level_a)
    
    if program_b and university_b and level_b:
        program_b_data = get_program_data(continent_b, country_b, university_b, program_b, level_b)
    
    # Display comparison if both programs are selected
    if program_a_data is not None and program_b_data is not None:
        # Display program information cards using a cleaner approach
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            # Create program A card
            university_a_name = program_a_data.get('university', 'N/A')
            program_a_name = program_a_data.get('program', 'N/A')
            level_a_name = program_a_data.get('level', 'N/A')
            country_a_name = program_a_data.get('country', 'N/A')
            field_a_name = program_a_data.get('field', 'N/A')
            duration_a = program_a_data.get('duration_years', 'N/A')
            cluster_a = program_a_data.get('cluster_name', 'N/A')
            
            # Determine cluster color
            cluster_color_a = '#EF4444'  # Default red for Expensive
            if cluster_a == 'Cheap':
                cluster_color_a = '#10B981'  # Green
            elif cluster_a == 'Medium':
                cluster_color_a = '#F59E0B'  # Orange
            
            # Create card HTML with proper escaping
            card_a_html = f"""
            <div class="program-card" style="border-color: #3498DB; padding: 20px; border-radius: 10px; background: #F9FAFB; margin-bottom: 1rem;">
                <h4 style="color: #1E3A8A; margin-bottom: 15px;">🎓 {university_a_name}</h4>
                <p><strong>Program:</strong> {program_a_name}</p>
                <p><strong>Level:</strong> {level_a_name}</p>
                <p><strong>Country:</strong> {country_a_name}</p>
                <p><strong>Field:</strong> {field_a_name}</p>
                <p><strong>Duration:</strong> {duration_a} years</p>
                <p><strong>Cluster:</strong> <span style="color: {cluster_color_a}; font-weight: bold;">{cluster_a}</span></p>
            </div>
            """
            
            st.markdown(card_a_html, unsafe_allow_html=True)
            
            # Show duplicate info if applicable
            if 'duplicate_count' in program_a_data and program_a_data['duplicate_count'] > 1:
                st.caption(f"*Average of {program_a_data['duplicate_count']} entries*")
        
        with col_info2:
            # Create program B card
            university_b_name = program_b_data.get('university', 'N/A')
            program_b_name = program_b_data.get('program', 'N/A')
            level_b_name = program_b_data.get('level', 'N/A')
            country_b_name = program_b_data.get('country', 'N/A')
            field_b_name = program_b_data.get('field', 'N/A')
            duration_b = program_b_data.get('duration_years', 'N/A')
            cluster_b = program_b_data.get('cluster_name', 'N/A')
            
            # Determine cluster color
            cluster_color_b = '#EF4444'  # Default red for Expensive
            if cluster_b == 'Cheap':
                cluster_color_b = '#10B981'  # Green
            elif cluster_b == 'Medium':
                cluster_color_b = '#F59E0B'  # Orange
            
            # Create card HTML with proper escaping
            card_b_html = f"""
            <div class="program-card" style="border-color: #F39C12; padding: 20px; border-radius: 10px; background: #F9FAFB; margin-bottom: 1rem;">
                <h4 style="color: #1E3A8A; margin-bottom: 15px;">🎓 {university_b_name}</h4>
                <p><strong>Program:</strong> {program_b_name}</p>
                <p><strong>Level:</strong> {level_b_name}</p>
                <p><strong>Country:</strong> {country_b_name}</p>
                <p><strong>Field:</strong> {field_b_name}</p>
                <p><strong>Duration:</strong> {duration_b} years</p>
                <p><strong>Cluster:</strong> <span style="color: {cluster_color_b}; font-weight: bold;">{cluster_b}</span></p>
            </div>
            """
            
            st.markdown(card_b_html, unsafe_allow_html=True)
            
            # Show duplicate info if applicable
            if 'duplicate_count' in program_b_data and program_b_data['duplicate_count'] > 1:
                st.caption(f"*Average of {program_b_data['duplicate_count']} entries*")
        
        # Cost Comparison - Grouped Bar Chart
        st.markdown("#### 📊 Cost Component Comparison")
        
        # Prepare comparison data
        cost_components = ['Tuition', 'Living Cost', 'Insurance', 'Visa', 'Total Cost']
        
        # Calculate values for program A
        program_a_values = [
            program_a_data.get('tuition_usd', 0),
            program_a_data.get('total_living_cost_usd', 0),
            program_a_data.get('total_insurance_cost_usd', 0),
            program_a_data.get('visa_fee_usd', 0),
            program_a_data.get('total_study_cost_usd', 0)
        ]
        
        # Calculate values for program B
        program_b_values = [
            program_b_data.get('tuition_usd', 0),
            program_b_data.get('total_living_cost_usd', 0),
            program_b_data.get('total_insurance_cost_usd', 0),
            program_b_data.get('visa_fee_usd', 0),
            program_b_data.get('total_study_cost_usd', 0)
        ]
        
        # Create grouped bar chart
        fig = go.Figure(data=[
            go.Bar(
                name=f"{program_a_data.get('university', 'program A')[:20]}...",
                x=cost_components, 
                y=program_a_values,
                marker_color='#3498DB',
                text=[f'${x:,.0f}' for x in program_a_values],
                textposition='auto'
            ),
            go.Bar(
                name=f"{program_b_data.get('university', 'program B')[:20]}...",
                x=cost_components, 
                y=program_b_values,
                marker_color='#F39C12',
                text=[f'${x:,.0f}' for x in program_b_values],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            barmode='group',
            yaxis_title="Cost (USD)",
            height=500,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Cost Difference Analysis
        st.markdown("#### 📈 Cost Difference Analysis")
        
        # Create metrics columns
        col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
        
        with col_metric1:
            total_cost_a = program_a_data.get('total_study_cost_usd', 0)
            total_cost_b = program_b_data.get('total_study_cost_usd', 0)
            total_cost_difference = total_cost_b - total_cost_a
            percentage_difference = (total_cost_difference / total_cost_a) * 100 if total_cost_a > 0 else 0
            st.metric(
                "Total Cost Diff",
                f"${abs(total_cost_difference):,.0f}",
                delta=f"{percentage_difference:+.1f}%",
                delta_color="inverse" if total_cost_difference > 0 else "normal"
            )
        
        with col_metric2:
            yearly_cost_a = program_a_data.get('cost_per_year_usd', 0)
            yearly_cost_b = program_b_data.get('cost_per_year_usd', 0)
            yearly_cost_difference = yearly_cost_b - yearly_cost_a
            st.metric(
                "Yearly Cost Diff",
                f"${abs(yearly_cost_difference):,.0f}",
                delta=f"{yearly_cost_difference:+,.0f}"
            )
        
        with col_metric3:
            rent_a = program_a_data.get('rent_usd', 0)
            rent_b = program_b_data.get('rent_usd', 0)
            rent_difference = rent_b - rent_a
            st.metric(
                "Monthly Rent Diff",
                f"${abs(rent_difference):,.0f}",
                delta=f"{rent_difference:+,.0f}"
            )
        
        with col_metric4:
            duration_a = program_a_data.get('duration_years', 1)
            duration_b = program_b_data.get('duration_years', 1)
            duration_ratio = duration_a / duration_b if duration_b > 0 else 0
            st.metric(
                "Duration Ratio",
                f"{duration_a:.1f}:{duration_b:.1f}",
                delta=f"{duration_ratio:.1f}x"
            )
    
    elif program_a_data is not None or program_b_data is not None:
        st.info("Please select programs from both columns to compare")
    else:
        st.info("Please select programs to compare")

# ================================================
# TAB 4: COST CLUSTERS
# ================================================
with tabs[3]:
    st.markdown('<h2 class="sub-header">Cost Cluster Analysis</h2>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html = True)
    
    # Prepare cluster statistics
    cluster_statistics = filtered_df.groupby('cluster_name').agg({
        'total_study_cost_usd': ['mean', 'median', 'count'],
        'cost_per_year_usd': 'mean',
        'tuition_usd': 'mean',
        'rent_usd': 'mean'
    }).round(0)
    
    # Flatten column names
    cluster_statistics.columns = ['_'.join(col).strip() for col in cluster_statistics.columns.values]
    cluster_statistics = cluster_statistics.reset_index()
    
    # Display cluster metrics in cards - Fixed order: Cheap, Medium, Expensive
    clusters_ordered = ['Cheap', 'Medium', 'Expensive']
    cluster_colors = {'Cheap': '#10B981', 'Medium': '#F59E0B', 'Expensive': '#EF4444'}

    # Ambil cluster yg benar2 ada datanya (setelah filter)
    available_clusters = [
        c for c in clusters_ordered 
        if c in cluster_statistics['cluster_name'].values]

    n = len(available_clusters)
    
    # Buat kolom dinamis biar center 
    if n == 3:
        target_cols = st.columns(3)
    elif n==2:
        # spacer kiri dan kanan --> 2 card ke tengah 
        spacer_1, c1, c2, spacer_r = st.columns([1,3,3,1])
        target_cols = [c1, c2]
    elif n==1:
        # 1 card tepat di tengah
        spacer_1, c1, spacer_r = st.columns([2,4,2])
        target_cols = [c1]
    else:
        st.info("No clusters data available for the selected filters")
        target_cols = []
    
    # Render card sesuai urutan Cheap --> Medium --> Expensive
    for i, cluster in enumerate(available_clusters):
        with target_cols[i]:
            stats = cluster_statistics[
                cluster_statistics['cluster_name'] == cluster
            ].iloc[0]
            
            st.markdown(f"""
            <div class="cluster-card" style="background: {cluster_colors[cluster]};">
                <h3 style="margin: 0; font-size: 1.5rem; text-align: center;">{cluster}</h3>
                <div style="margin-top: 15px;">
                    <div style="font-size: 0.9rem;">programs</div>
                    <div style="font-size: 1.8rem; font-weight: bold;">{int(stats['total_study_cost_usd_count']):,}</div>
                </div>
                <div style="margin-top: 10px;">
                    <div style="font-size: 0.9rem;">Avg Total Cost</div>
                    <div style="font-size: 1.2rem;">${stats['total_study_cost_usd_mean']:,.0f}</div>
                </div>
                <div style="margin-top: 10px;">
                    <div style="font-size: 0.9rem;">Avg Yearly Cost</div>
                    <div style="font-size: 1.2rem;">${stats['cost_per_year_usd_mean']:,.0f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Field Distribution by Cluster - Fixed order: Cheap, Medium, Expensive
    st.markdown("#### 📚 Field Distribution by Cluster")
    
    # Prepare data for field distribution
    cluster_field_data = filtered_df.groupby(['cluster_name', 'field']).size().reset_index(name='Count')
    
    # Order the clusters
    cluster_field_data['cluster_name'] = pd.Categorical(
        cluster_field_data['cluster_name'], 
        categories=clusters_ordered, 
        ordered=True
    )
    
    # Sort by cluster order and count
    cluster_field_data = cluster_field_data.sort_values(['cluster_name', 'Count'], ascending=[True, False])
    
    # Get top 5 fields per cluster for better visualization
    top_fields_per_cluster = cluster_field_data.groupby('cluster_name').head(5)
    
    # Create grouped bar chart with fixed cluster order
    fig = px.bar(
        top_fields_per_cluster,
        x='field',
        y='Count',
        color='cluster_name',
        color_discrete_map=cluster_colors,
        barmode='group',
        category_orders={'cluster_name': clusters_ordered},
        title='Top 5 Fields in Each Cost Cluster',
        labels={'Count': 'Number of programs', 'Field': 'Field of Study'}, 
        text_auto='.0f'
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="Field of Study",
        yaxis_title="Number of programs",
        legend_title="Cost Cluster",
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Geographic Distribution of Clusters
    st.markdown("#### 🌍 Geographic Distribution of Clusters")
    
    # Prepare data for geographic distribution
    country_cluster_data = filtered_df.groupby(['country', 'cluster_name']).size().reset_index(name='Count')
    
    # Order the clusters
    country_cluster_data['cluster_name'] = pd.Categorical(
        country_cluster_data['cluster_name'], 
        categories=clusters_ordered, 
        ordered=True
    )
    
    # Sort by cluster order
    country_cluster_data = country_cluster_data.sort_values(['cluster_name', 'Count'], ascending=[True, False])
    
    # Get top 10 countries by total program count
    top_countries = filtered_df['country'].value_counts().head(10).index.tolist()
    top_countries_data = country_cluster_data[country_cluster_data['country'].isin(top_countries)]
    
    # Create stacked bar chart with fixed cluster order
    fig = px.bar(
        top_countries_data,
        x='country',
        y='Count',
        color='cluster_name',
        color_discrete_map=cluster_colors,
        barmode='stack',
        category_orders={
            'country': top_countries,
            'cluster_name': clusters_ordered
        },
        title='Cluster Distribution in Top 10 Countries',
        labels={'Count': 'Number of programs', 'country': 'country'}, 
        text_auto='.0f'
    )
    
    fig.update_layout(
        xaxis_title="country",
        yaxis_title="Number of programs",
        height=400,
        legend_title="Cost Cluster",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ================================================
# TAB 5: DATA EXPLORER
# ================================================
with tabs[4]:
    st.markdown('<h2 class="sub-header">Interactive Data Explorer</h2>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)  # ⬅ jarak ke bawah

    col_search, col_sort, col_order = st.columns([2, 1, 1])
    
    with col_search:
        search_term = st.text_input(
            "🔍 Search across all columns:",
            placeholder="Type to search university, program, field...",
            key="explorer_search"
        )
    
    with col_sort:
        sort_column = st.selectbox(
            "Sort by:",
            ["total_study_cost_usd", "cost_per_year_usd", "tuition_usd", "rent_usd", "university", "country"],
            key="explorer_sort"
        )
    
    with col_order:
        sort_order = st.radio("Order:", ["Descending", "Ascending"], horizontal=True, key="explorer_order")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply search to dataframe
    explorer_data = filtered_df.copy()
    
    if search_term:
        mask = explorer_data.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        explorer_data = explorer_data[mask]
    
    # Apply sorting
    ascending_order = sort_order == "Ascending"
    explorer_data = explorer_data.sort_values(by=sort_column, ascending=ascending_order)
    
    # Define columns to display
    display_columns = [
        "university", "country", "continent", "city", "program", "field", "level",
        "cluster_name", "duration_years", "tuition_usd", "rent_usd", "living_cost_index",
        "total_study_cost_usd", "cost_per_year_usd"
    ]
    
    # Display results count
    st.markdown(f"**📋 Found {len(explorer_data)} programs**")
    
    # Configure column display settings
    column_configuration = {
        "university": st.column_config.TextColumn("university", width="large"),
        "country": st.column_config.TextColumn("country"),
        "continent": st.column_config.TextColumn("continent"),
        "city": st.column_config.TextColumn("city"),
        "program": st.column_config.TextColumn("program", width="medium"),
        "field": st.column_config.TextColumn("field"),
        "level": st.column_config.TextColumn("level"),
        "cluster_name": st.column_config.TextColumn(
            "Cluster",
            help="Cost cluster: Cheap, Medium, or Expensive"
        ),
        "duration_years": st.column_config.NumberColumn("Duration", format="%d years"),
        "tuition_usd": st.column_config.NumberColumn("Tuition", format="$%d"),
        "rent_usd": st.column_config.NumberColumn("Rent/Month", format="$%d"),
        "living_cost_index": st.column_config.NumberColumn("Cost Index", format="%.1f"),
        "total_study_cost_usd": st.column_config.NumberColumn("Total Cost", format="$%d"),
        "cost_per_year_usd": st.column_config.NumberColumn("Cost/Year", format="$%d"),
    }
    
    # Color coding function for cluster column
    def color_cluster_cells(value):
        if value == 'Cheap':
            return 'background-color: #D1FAE5; color: #065F46;'
        elif value == 'Medium':
            return 'background-color: #FEF3C7; color: #92400E;'
        elif value == 'Expensive':
            return 'background-color: #FEE2E2; color: #991B1B;'
        return ''
    
    # Apply styling to the dataframe
    styled_explorer_data = explorer_data[display_columns].style.applymap(
        color_cluster_cells, subset=['cluster_name']
    )
    
    # Display the styled dataframe
    st.dataframe(
        styled_explorer_data,
        column_config=column_configuration,
        use_container_width=True,
        height=600
    )
    
    # Download button for filtered data
    csv_data = explorer_data[display_columns].to_csv(index=False).encode('utf-8')
    
    # Center the download button
    col_left, col_center, col_right = st.columns([2, 1, 2])
    with col_center:
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv_data,
            file_name="filtered_study_cost.csv",
            mime="text/csv",
            use_container_width=True
        )

# Tambahkan di bagian bawah dashboard_app.py (sebelum footer)
st.markdown("""
<script>
// FIX TAB HEADERS FOR DARK/LIGHT MODE
function fixTabHeaders() {
    // Check current theme
    const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark';
    
    // Get all tab elements
    const tabs = document.querySelectorAll('.stTabs [data-baseweb="tab"]');
    
    tabs.forEach(tab => {
        const isActive = tab.getAttribute('aria-selected') === 'true';
        
        if (!isActive) {
            if (isDarkMode) {
                // Dark mode - white text, dark background
                tab.style.color = '#FFFFFF';
                tab.style.backgroundColor = '#374151';
                tab.style.borderColor = '#4B5563';
            } else {
                // Light mode - dark text, light background
                tab.style.color = '#1F2937';
                tab.style.backgroundColor = '#F3F4F6';
                tab.style.borderColor = '#E5E7EB';
            }
        } else {
            // Active tab - always blue with white text
            tab.style.backgroundColor = '#4F46E5';
            tab.style.color = '#FFFFFF';
            tab.style.borderColor = '#4F46E5';
        }
    });
}

// Run when page loads
setTimeout(fixTabHeaders, 100);

// Run when theme changes
const themeObserver = new MutationObserver((mutations) => {
    mutations.forEach(mutation => {
        if (mutation.attributeName === 'data-theme') {
            setTimeout(fixTabHeaders, 100);
        }
    });
});
themeObserver.observe(document.documentElement, { attributes: true });

// Run when tabs are clicked
document.addEventListener('click', function(e) {
    if (e.target.closest('.stTabs [data-baseweb="tab"]')) {
        setTimeout(fixTabHeaders, 50);
    }
});

// Also check periodically
setInterval(fixTabHeaders, 1000);

// Function to fix program cards in dark mode - DENGAN BACKGROUND LEBIH GELAP
function fixProgramCards() {
    const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark';
    const programCards = document.querySelectorAll('.program-card');
    
    programCards.forEach(card => {
        if (isDarkMode) {
            // Dark mode: background hitam gelap, teks abu-abu terang
            card.style.backgroundColor = '#0F172A';
            card.style.color = '#E2E8F0';
            
            // Perbaiki semua elemen teks di dalamnya
            const allElements = card.querySelectorAll('*');
            allElements.forEach(el => {
                const tagName = el.tagName.toLowerCase();
                const computedColor = window.getComputedStyle(el).color;
                
                // Jangan ubah warna untuk span cluster (warna khusus)
                if (el.tagName === 'SPAN' && 
                    (el.style.color.includes('#10B981') || 
                     el.style.color.includes('#F59E0B') || 
                     el.style.color.includes('#EF4444'))) {
                    return; // Biarkan warna asli cluster
                }
                
                // Ubah warna teks biasa menjadi abu-abu terang
                if (tagName !== 'img' && tagName !== 'svg' && tagName !== 'path') {
                    el.style.color = '#E2E8F0';
                }
            });
        } else {
            // Light mode: background terang, teks gelap
            card.style.backgroundColor = '#F9FAFB';
            card.style.color = '#1F2937';
        }
    });
}

// Run when theme changes
const themeObserver = new MutationObserver((mutations) => {
    mutations.forEach(mutation => {
        if (mutation.attributeName === 'data-theme') {
            setTimeout(fixProgramCards, 100);
        }
    });
});
themeObserver.observe(document.documentElement, { attributes: true });

</script>
""", unsafe_allow_html=True)

# ================================================
# FOOTER SECTION
# ================================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 20px;'>"
    f"Educational Cost Intelligence Dashboard • For educational purporses only"
    "</div>",
    unsafe_allow_html=True
)