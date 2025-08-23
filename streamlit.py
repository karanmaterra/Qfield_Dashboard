import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="MATERRA®",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS styling to match Materra design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    
    /* Main container styling */
    .stApp {
        background: linear-gradient(135deg, #f8f6ff 0%, #e8e2ff 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom header */
    .custom-header {
        background: white;
        padding: 1rem 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        position: sticky;
        top: 0;
        z-index: 1000;
        margin: -1rem -1rem 2rem -1rem;
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .logo {
        font-size: 2rem;
        font-weight: 700;
        color: #2d1b69;
        letter-spacing: -0.5px;
    }
    
    .nav-tabs {
        display: flex;
        gap: 2rem;
        align-items: center;
    }
    
    .nav-tab {
        color: #666;
        text-decoration: none;
        font-weight: 500;
        padding: 0.5rem 0;
        border-bottom: 2px solid transparent;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .nav-tab:hover {
        color: #2d1b69;
        border-bottom-color: #a855f7;
    }
    
    .nav-tab.active {
        color: #2d1b69;
        border-bottom-color: #a855f7;
    }
    
    .cta-button {
        background: linear-gradient(135deg, #a855f7 0%, #8b5cf6 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
    }
    
    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(168, 85, 247, 0.3);
    }
    
    /* Hero section */
    .hero-section {
        text-align: center;
        padding: 4rem 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        color: #2d1b69;
        margin-bottom: 1.5rem;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: #666;
        margin-bottom: 2rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.6;
    }
    
    /* Content cards */
    .content-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border: 1px solid rgba(168, 85, 247, 0.1);
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2d1b69;
        margin-bottom: 1rem;
    }
    
    .card-content {
        color: #666;
        line-height: 1.6;
    }
    
    /* Footer */
    .custom-footer {
        background: linear-gradient(135deg, #2d1b69 0%, #1e1340 100%);
        color: white;
        padding: 3rem 2rem 1rem;
        margin-top: 4rem;
    }
    
    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr;
        gap: 2rem;
    }
    
    .footer-section h4 {
        font-weight: 600;
        margin-bottom: 1rem;
        color: #a855f7;
    }
    
    .footer-section p, .footer-section a {
        color: rgba(255,255,255,0.8);
        text-decoration: none;
        line-height: 1.6;
    }
    
    .footer-section a:hover {
        color: #a855f7;
    }
    
    .footer-tagline {
        font-style: italic;
        color: rgba(255,255,255,0.6);
    }
    
    .footer-bottom {
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 1rem;
        margin-top: 2rem;
        text-align: center;
        color: rgba(255,255,255,0.6);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .header-content {
            flex-direction: column;
            gap: 1rem;
        }
        
        .nav-tabs {
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .hero-title {
            font-size: 2.5rem;
        }
        
        .footer-content {
            grid-template-columns: 1fr;
        }
        
        .custom-header {
            padding: 1rem;
        }
    }
    
    /* Streamlit specific overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        border-radius: 50px;
        background: rgba(168, 85, 247, 0.1);
        color: #2d1b69;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #a855f7 0%, #8b5cf6 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Custom header
st.markdown("""
<div class="custom-header">
    <div class="header-content">
        <div class="logo">MATERRA®</div>
        <button class="cta-button">Refreshs</button>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state for tab management
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Farm Info"

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🌾 Farm Info", "🚜 Field Visit", "🌧️ Rainfall", "📊 Observation", "🔗 Combine"])

with tab1:
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Farm Information Management</h1>
        <p class="hero-subtitle">Comprehensive farm data management system for modern agriculture</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="content-card">
            <h3 class="card-title">Farm Details</h3>
            <div class="card-content">
                Track and manage your farm's basic information, location data, and operational details.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("farm_info"):
            farm_name = st.text_input("Farm Name")
            location = st.text_input("Location")
            area = st.number_input("Total Area (acres)", min_value=0.0)
            crop_type = st.selectbox("Primary Crop", ["Wheat", "Rice", "Corn", "Cotton", "Soybeans"])
            submitted = st.form_submit_button("Save Farm Info")
            
            if submitted:
                st.success("Farm information saved successfully!")
    
    with col2:
        st.markdown("""
        <div class="content-card">
            <h3 class="card-title">Quick Stats</h3>
            <div class="card-content">
                Overview of your farm's key metrics and performance indicators.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample metrics
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total Farms", "12", "2")
        with col_b:
            st.metric("Active Fields", "45", "3")
        with col_c:
            st.metric("Avg Yield", "85%", "5%")

with tab2:
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Field Visit Tracking</h1>
        <p class="hero-subtitle">Monitor and document field visits with detailed observations</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="content-card">
        <h3 class="card-title">Recent Visits</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample visit data
    visit_data = {
        'Date': ['2025-08-20', '2025-08-18', '2025-08-15', '2025-08-12'],
        'Field': ['North Field', 'South Field', 'East Field', 'West Field'],
        'Purpose': ['Pest Inspection', 'Irrigation Check', 'Soil Testing', 'Harvest Planning'],
        'Status': ['Completed', 'Completed', 'In Progress', 'Scheduled']
    }
    
    df_visits = pd.DataFrame(visit_data)
    st.dataframe(df_visits, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Schedule New Visit")
        with st.form("new_visit"):
            visit_date = st.date_input("Visit Date")
            field_select = st.selectbox("Select Field", ["North Field", "South Field", "East Field", "West Field"])
            visit_purpose = st.text_area("Purpose of Visit")
            priority = st.select_slider("Priority", ["Low", "Medium", "High"])
            submit_visit = st.form_submit_button("Schedule Visit")
            
            if submit_visit:
                st.success("Visit scheduled successfully!")

with tab3:
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Rainfall Monitoring</h1>
        <p class="hero-subtitle">Track precipitation patterns and water management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample rainfall data
    rainfall_data = {
        'Date': pd.date_range('2025-08-01', '2025-08-23', freq='D'),
        'Rainfall (mm)': [0, 2.5, 0, 15.2, 8.7, 0, 0, 22.1, 5.3, 0, 
                         12.8, 0, 3.2, 18.9, 0, 0, 7.1, 25.4, 0, 9.6, 0, 0, 4.8]
    }
    
    df_rainfall = pd.DataFrame(rainfall_data)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="content-card">
            <h3 class="card-title">Rainfall Chart</h3>
        </div>
        """, unsafe_allow_html=True)
        
        fig = px.bar(df_rainfall, x='Date', y='Rainfall (mm)', 
                     title="Daily Rainfall Data",
                     color='Rainfall (mm)',
                     color_continuous_scale=['#e8e2ff', '#a855f7'])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="content-card">
            <h3 class="card-title">Summary</h3>
        </div>
        """, unsafe_allow_html=True)
        
        total_rainfall = df_rainfall['Rainfall (mm)'].sum()
        avg_rainfall = df_rainfall['Rainfall (mm)'].mean()
        rainy_days = (df_rainfall['Rainfall (mm)'] > 0).sum()
        
        st.metric("Total Rainfall", f"{total_rainfall:.1f} mm")
        st.metric("Average Daily", f"{avg_rainfall:.1f} mm")
        st.metric("Rainy Days", f"{rainy_days}")

with tab4:
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Field Observations</h1>
        <p class="hero-subtitle">Document and analyze crop conditions and field status</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="content-card">
            <h3 class="card-title">Add New Observation</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("observation"):
            obs_date = st.date_input("Observation Date")
            field_obs = st.selectbox("Field", ["North Field", "South Field", "East Field", "West Field"])
            crop_stage = st.selectbox("Crop Stage", ["Seedling", "Vegetative", "Flowering", "Maturity"])
            health_rating = st.slider("Health Rating", 1, 10, 7)
            notes = st.text_area("Additional Notes")
            submit_obs = st.form_submit_button("Save Observation")
            
            if submit_obs:
                st.success("Observation recorded successfully!")
    
    with col2:
        st.markdown("""
        <div class="content-card">
            <h3 class="card-title">Recent Observations</h3>
        </div>
        """, unsafe_allow_html=True)
        
        obs_data = {
            'Date': ['2025-08-23', '2025-08-22', '2025-08-21'],
            'Field': ['North Field', 'South Field', 'East Field'],
            'Health Score': [8, 7, 9],
            'Stage': ['Flowering', 'Vegetative', 'Maturity']
        }
        
        df_obs = pd.DataFrame(obs_data)
        st.dataframe(df_obs, use_container_width=True)
        
        # Health trend chart
        fig_health = px.line(df_obs, x='Date', y='Health Score', 
                           title="Field Health Trends",
                           color_discrete_sequence=['#a855f7'])
        fig_health.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_health, use_container_width=True)

with tab5:
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">Combined Analytics</h1>
        <p class="hero-subtitle">Comprehensive dashboard combining all farm data insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Dashboard with combined metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Farms", "12", "2")
    with col2:
        st.metric("Weekly Rainfall", "45.2 mm", "15.3")
    with col3:
        st.metric("Avg Field Health", "8.2/10", "0.5")
    with col4:
        st.metric("Scheduled Visits", "8", "3")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("""
        <div class="content-card">
            <h3 class="card-title">Farm Performance Overview</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Combined performance chart
        perf_data = {
            'Metric': ['Yield Efficiency', 'Water Usage', 'Pest Control', 'Soil Health', 'Equipment Usage'],
            'Score': [85, 78, 92, 88, 75]
        }
        
        fig_perf = px.bar(perf_data, x='Metric', y='Score',
                         title="Key Performance Indicators",
                         color='Score',
                         color_continuous_scale=['#e8e2ff', '#a855f7'])
        fig_perf.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_perf, use_container_width=True)
    
    with col_right:
        st.markdown("""
        <div class="content-card">
            <h3 class="card-title">Weekly Summary</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.success("✅ All scheduled field visits completed")
        st.info("📊 Average field health score: 8.2/10")
        st.warning("⚠️ 2 fields require irrigation attention")
        st.info("🌧️ Favorable rainfall conditions this week")
        
        st.subheader("Recommendations")
        st.write("• Increase monitoring frequency for East Field")
        st.write("• Schedule pest control treatment for North Field")
        st.write("• Optimize irrigation schedule based on rainfall data")

# Custom footer
st.markdown("""
<div class="custom-footer">
    <div class="footer-content">
        <div class="footer-section">
            <h4>AgriTech Platform</h4>
            <p class="footer-tagline">From seeds to harvest, we've got you covered.</p>
            <p>Advanced agricultural management solutions for modern farming operations.</p>
        </div>
        <div class="footer-section">
            <h4>Farm Management</h4>
            <a href="#">Farm Info</a><br>
            <a href="#">Field Monitoring</a><br>
            <a href="#">Crop Planning</a><br>
            <a href="#">Resource Management</a>
        </div>
        <div class="footer-section">
            <h4>Analytics</h4>
            <a href="#">Weather Data</a><br>
            <a href="#">Yield Forecasting</a><br>
            <a href="#">Performance Metrics</a><br>
            <a href="#">Reports</a>
        </div>
        <div class="footer-section">
            <h4>Support</h4>
            <a href="#">Documentation</a><br>
            <a href="#">Training</a><br>
            <a href="#">Contact Us</a><br>
            <a href="#">Community</a>
        </div>
    </div>
    <div class="footer-bottom">
        <p>&copy; 2025 AgriTech Platform. Empowering sustainable agriculture through technology.</p>
    </div>
</div>
""", unsafe_allow_html=True)