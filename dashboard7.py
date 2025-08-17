import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Set page configuration
st.set_page_config(
    page_title="FE Data Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .tab-subheader {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff7f0e;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .warning-text {
        color: #d62728;
        font-weight: bold;
    }
    .success-text {
        color: #2ca02c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
base_path = Path(__file__).parent / "data"

# Define CSV file paths (relative)
files = {
    'farminfo': base_path / "merged_farminfo.csv",
    'fieldvisit': base_path / "merged_fieldvisit.csv",
    'rainfall': base_path / "merged_rainfall.csv"
}

# Load CSVs
df_farm = pd.read_csv(files['farminfo'])
df_visit = pd.read_csv(files['fieldvisit'])
df_rain = pd.read_csv(files['rainfall'])
        
        data = {}
        load_messages = []
        for key, file_path in files.items():
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                print(f"Debug: Loaded {key} with shape {df.shape} and columns {df.columns.tolist()}")
                data[key] = df
                load_messages.append(f"{key}: {len(df)} records")
            else:
                st.error(f"❌ File not found: {file_path}")
                data[key] = pd.DataFrame()
        
        st.success(f"✅ Loaded {' | '.join(load_messages)}")
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return {'farminfo': pd.DataFrame(), 'fieldvisit': pd.DataFrame(), 'rainfall': pd.DataFrame()}

def clean_farmer_data(df):
    """Clean farmer data with lenient handling of Farmer ID"""
    if df.empty:
        return df, df
    
    cleaned_df = df.copy()
    
    if 'Farmer ID' in cleaned_df.columns:
        cleaned_df['Farmer ID'] = pd.to_numeric(cleaned_df['Farmer ID'], errors='coerce')
        valid_farmer_mask = cleaned_df['Farmer ID'].notna()
        valid_data = cleaned_df[valid_farmer_mask].copy() if any(valid_farmer_mask) else cleaned_df
        valid_data['Farmer ID'] = valid_data['Farmer ID'].astype('Int64')
    else:
        valid_data = cleaned_df
    
    print(f"Debug: Cleaned {df.shape} to {valid_data.shape} for valid Farmer IDs")
    return cleaned_df, valid_data

def parse_visit_date(date_str):
    """Parse visit date and handle different formats"""
    if pd.isna(date_str) or str(date_str).strip() == '':
        return None
    try:
        formats = ['%Y/%m/%d', '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%m/%d/%Y']
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue
        return None
    except:
        return None

def classify_visit_period(date_str):
    """Classify visit into one of the sixteen visit periods"""
    date_obj = parse_visit_date(date_str)
    if date_obj is None:
        return "Unknown"
    
    visit_periods = [
        ("First Visit", datetime(2025, 6, 20), datetime(2025, 7, 14)),
        ("Second Visit", datetime(2025, 7, 15), datetime(2025, 7, 31)),
        ("Third Visit", datetime(2025, 8, 1), datetime(2025, 8, 14)),
        ("Fourth Visit", datetime(2025, 8, 15), datetime(2025, 8, 31)),
        ("Fifth Visit", datetime(2025, 9, 1), datetime(2025, 9, 14)),
        ("Sixth Visit", datetime(2025, 9, 15), datetime(2025, 9, 30)),
        ("Seventh Visit", datetime(2025, 10, 1), datetime(2025, 10, 14)),
        ("Eighth Visit", datetime(2025, 10, 15), datetime(2025, 10, 31)),
        ("Ninth Visit", datetime(2025, 11, 1), datetime(2025, 11, 14)),
        ("Tenth Visit", datetime(2025, 11, 15), datetime(2025, 11, 30)),
        ("Eleventh Visit", datetime(2025, 12, 1), datetime(2025, 12, 14)),
        ("Twelfth Visit", datetime(2025, 12, 15), datetime(2025, 12, 31)),
        ("Thirteenth Visit", datetime(2026, 1, 1), datetime(2026, 1, 14)),
        ("Fourteenth Visit", datetime(2026, 1, 15), datetime(2026, 1, 31)),
        ("Fifteenth Visit", datetime(2026, 2, 1), datetime(2026, 2, 14)),
        ("Sixteenth Visit", datetime(2026, 2, 15), datetime(2026, 2, 28))
    ]
    
    for visit_name, start_date, end_date in visit_periods:
        if start_date <= date_obj <= end_date:
            return visit_name
    return "Outside Range"

def create_fe_summary_table(original_df, valid_df, cluster=None):
    """Create FE summary table with farmer counts and IDs, filtered by cluster if provided"""
    if original_df.empty or 'FE_Name' not in original_df.columns:
        print("Debug: Empty original_df or missing FE_Name")
        return pd.DataFrame()
    
    if cluster and cluster != "All" and 'Cluster name' in original_df.columns:
        original_df = original_df[original_df['Cluster name'] == cluster]
        valid_df = valid_df[valid_df['Cluster name'] == cluster] if not valid_df.empty else valid_df
    
    all_fes = original_df['FE_Name'].dropna().unique()
    summary_data = []
    
    for fe_name in all_fes:
        if valid_df.empty or 'Farmer ID' not in valid_df.columns:
            summary_data.append({'FE Name': fe_name, 'Farmer Count': 0, 'Farmer IDs': '0'})
        else:
            fe_valid_data = valid_df[valid_df['FE_Name'] == fe_name]
            if fe_valid_data.empty:
                summary_data.append({'FE Name': fe_name, 'Farmer Count': 0, 'Farmer IDs': '0'})
            else:
                farmer_ids = fe_valid_data['Farmer ID'].unique()
                farmer_count = len(farmer_ids)
                farmer_ids_str = ', '.join(sorted(farmer_ids.astype(str)))
                summary_data.append({'FE Name': fe_name, 'Farmer Count': farmer_count, 'Farmer IDs': farmer_ids_str})
    
    summary_df = pd.DataFrame(summary_data).sort_values('Farmer Count', ascending=False)
    print(f"Debug: FE Summary Table shape: {summary_df.shape}")
    return summary_df

def find_duplicate_farmers(df, cluster=None):
    """Find FEs who collected same farmer data, filtered by cluster if provided"""
    if df.empty or 'FE_Name' not in df.columns or 'Farmer ID' not in df.columns:
        print("Debug: Empty df or missing columns in duplicate_farmers")
        return pd.DataFrame()
    
    if cluster and cluster != "All" and 'Cluster name' in df.columns:
        df = df[df['Cluster name'] == cluster]
    
    farmer_fe_counts = df.groupby('Farmer ID')['FE_Name'].nunique()
    duplicate_farmers = farmer_fe_counts[farmer_fe_counts > 1].index
    
    if len(duplicate_farmers) == 0:
        return pd.DataFrame()
    
    duplicate_data = []
    for farmer_id in duplicate_farmers:
        fes = df[df['Farmer ID'] == farmer_id]['FE_Name'].unique()
        duplicate_data.append({'Farmer ID': farmer_id, 'FEs Collected': ', '.join(fes), 'Count': len(fes)})
    
    duplicate_df = pd.DataFrame(duplicate_data).sort_values('Count', ascending=False)
    print(f"Debug: Duplicate Farmers shape: {duplicate_df.shape}")
    return duplicate_df

def analyze_visit_data(original_df, farminfo_df=None, cluster=None, selected_visits=None):
    """Analyze visit data for fieldvisit and rainfall, filtered by cluster and visit periods if provided"""
    if original_df.empty:
        print("Debug: Empty original_df in analyze_visit_data")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    all_fes = original_df['FE_Name'].dropna().unique() if 'FE_Name' in original_df.columns else []
    
    if cluster and cluster != "All" and farminfo_df is not None and not farminfo_df.empty and 'Cluster name' in farminfo_df.columns:
        cluster_farmers = farminfo_df[farminfo_df['Cluster name'] == cluster]['Farmer ID'].dropna().unique()
        original_df = original_df[original_df['Farmer ID'].isin(cluster_farmers)]
    
    visit_periods = [
        'First Visit', 'Second Visit', 'Third Visit', 'Fourth Visit', 'Fifth Visit', 
        'Sixth Visit', 'Seventh Visit', 'Eighth Visit', 'Ninth Visit', 'Tenth Visit',
        'Eleventh Visit', 'Twelfth Visit', 'Thirteenth Visit', 'Fourteenth Visit',
        'Fifteenth Visit', 'Sixteenth Visit'
    ]
    
    if 'Visit date' not in original_df.columns:
        if selected_visits and 'All' not in selected_visits:
            summary_data = [{'FE Name': fe_name, 'Visit Period': vp, 'Farmer Count': 0, 'Farmer IDs': 'No visit data collected'} 
                            for fe_name in all_fes for vp in selected_visits]
            comparison_data = [{
                'FE Name': fe_name,
                **{f'Unique Farmers {vp}': 0 for vp in selected_visits},
                'Farmers in Multiple Visits': 0,
                'Multiple Visit IDs': 'No visit data collected'
            } for fe_name in all_fes]
            detailed_data = [{'FE Name': fe_name, 'Category': f'{vp} Farmers', 'Count': 0, 'Farmer IDs': 'No visit data collected'} 
                             for fe_name in all_fes for vp in selected_visits]
        else:
            summary_data = [{'FE Name': fe_name, 'Visit Period': vp, 'Farmer Count': 0, 'Farmer IDs': 'No visit data collected'} 
                            for fe_name in all_fes for vp in visit_periods]
            comparison_data = [{
                'FE Name': fe_name,
                **{f'Unique Farmers {vp}': 0 for vp in visit_periods},
                'Farmers in Multiple Visits': 0,
                'Multiple Visit IDs': 'No visit data collected'
            } for fe_name in all_fes]
            detailed_data = [{'FE Name': fe_name, 'Category': f'{vp} Farmers', 'Count': 0, 'Farmer IDs': 'No visit data collected'} 
                             for fe_name in all_fes for vp in visit_periods]
        return pd.DataFrame(summary_data), pd.DataFrame(comparison_data), pd.DataFrame(detailed_data)
    
    _, valid_df = clean_farmer_data(original_df)
    if cluster and cluster != "All" and farminfo_df is not None and not farminfo_df.empty and 'Cluster name' in farminfo_df.columns:
        cluster_farmers = farminfo_df[farminfo_df['Cluster name'] == cluster]['Farmer ID'].dropna().unique()
        valid_df = valid_df[valid_df['Farmer ID'].isin(cluster_farmers)] if not valid_df.empty else valid_df
    
    valid_df['Visit Period'] = valid_df['Visit date'].apply(classify_visit_period) if not valid_df.empty else pd.Series(dtype=str)
    valid_visits = valid_df[
        (valid_df['Visit Period'].isin(visit_periods)) & 
        (valid_df['Farmer ID'].notna()) & 
        (valid_df['FE_Name'].notna())
    ].copy() if not valid_df.empty else pd.DataFrame()
    
    if not valid_visits.empty:
        valid_visits['Farmer ID'] = valid_visits['Farmer ID'].astype(str)
    
    visit_summary = []
    comparison_data = []
    detailed_breakdown = []
    
    all_fes = valid_visits['FE_Name'].dropna().unique() if not valid_visits.empty else []
    
    active_visits = visit_periods if selected_visits is None or 'All' in selected_visits else selected_visits
    
    for fe_name in all_fes:
        if valid_visits.empty:
            visit_farmers = {vp: set() for vp in active_visits}
        else:
            fe_data = valid_visits[valid_visits['FE_Name'] == fe_name]
            visit_farmers = {vp: set(fe_data[fe_data['Visit Period'] == vp]['Farmer ID'].unique()) 
                             if not fe_data[fe_data['Visit Period'] == vp].empty else set() 
                             for vp in active_visits}
        
        # Calculate farmers in multiple visits (only relevant if all visits or multiple visits are shown)
        all_visit_farmers = set().union(*visit_farmers.values())
        multiple_visits = {farmer for farmer in all_visit_farmers 
                         if sum(farmer in visit_farmers[vp] for vp in active_visits) > 1} if len(active_visits) > 1 else set()
        
        # Visit Summary
        for vp in active_visits:
            farmers = visit_farmers[vp]
            visit_summary.append({
                'FE Name': fe_name,
                'Visit Period': vp,
                'Farmer Count': len(farmers),
                'Farmer IDs': ', '.join(sorted(farmers)) if farmers else '0'
            })
        
        # Comparison Data
        comparison_entry = {
            'FE Name': fe_name,
            **{f'Unique Farmers {vp}': len(visit_farmers[vp]) for vp in active_visits}
        }
        if len(active_visits) > 1:
            comparison_entry.update({
                'Farmers in Multiple Visits': len(multiple_visits),
                'Multiple Visit IDs': ', '.join(sorted(multiple_visits)) if multiple_visits else '0'
            })
        comparison_data.append(comparison_entry)
        
        # Detailed Breakdown (only include {vp} Farmers)
        for vp in active_visits:
            farmers = visit_farmers[vp]
            detailed_breakdown.append({
                'FE Name': fe_name,
                'Category': f'{vp} Farmers',
                'Count': len(farmers),
                'Farmer IDs': ', '.join(sorted(farmers)) if farmers else '0'
            })
    
    visit_summary_df = pd.DataFrame(visit_summary)
    comparison_df = pd.DataFrame(comparison_data)
    detailed_df = pd.DataFrame(detailed_breakdown)
    print(f"Debug: Visit Summary shape: {visit_summary_df.shape}, Comparison shape: {comparison_df.shape}, Detailed shape: {detailed_df.shape}")
    return visit_summary_df, comparison_df, detailed_df

def get_combined_fe_breakdown(fe_name, farminfo_df, fieldvisit_df, rainfall_df, cluster=None, selected_visits=None):
    """Generate combined breakdown for a selected FE across all datasets, filtered by cluster and visit periods if provided"""
    breakdown_data = {'Dataset': [], 'Category': [], 'Count': [], 'Farmer IDs': []}
    
    farminfo_filtered = farminfo_df
    if cluster and cluster != "All" and not farminfo_df.empty and 'Cluster name' in farminfo_df.columns:
        farminfo_filtered = farminfo_df[farminfo_df['Cluster name'] == cluster]
    
    _, farminfo_valid = clean_farmer_data(farminfo_filtered)
    _, fieldvisit_valid = clean_farmer_data(fieldvisit_df)
    _, rainfall_valid = clean_farmer_data(rainfall_df)
    
    if cluster and cluster != "All" and not farminfo_df.empty and 'Cluster name' in farminfo_df.columns:
        cluster_farmers = farminfo_df[farminfo_df['Cluster name'] == cluster]['Farmer ID'].dropna().unique()
        fieldvisit_valid = fieldvisit_valid[fieldvisit_valid['Farmer ID'].isin(cluster_farmers)] if not fieldvisit_valid.empty else fieldvisit_valid
        rainfall_valid = rainfall_valid[rainfall_valid['Farmer ID'].isin(cluster_farmers)] if not rainfall_valid.empty else rainfall_valid
    
    farminfo_fe_exists = not farminfo_filtered.empty and 'FE_Name' in farminfo_filtered.columns and fe_name in farminfo_filtered['FE_Name'].values
    fieldvisit_fe_exists = not fieldvisit_valid.empty and 'FE_Name' in fieldvisit_valid.columns and fe_name in fieldvisit_valid['FE_Name'].values
    rainfall_fe_exists = not rainfall_valid.empty and 'FE_Name' in rainfall_valid.columns and fe_name in rainfall_valid['FE_Name'].values
    
    visit_periods = [
        'First Visit', 'Second Visit', 'Third Visit', 'Fourth Visit', 'Fifth Visit', 
        'Sixth Visit', 'Seventh Visit', 'Eighth Visit', 'Ninth Visit', 'Tenth Visit',
        'Eleventh Visit', 'Twelfth Visit', 'Thirteenth Visit', 'Fourteenth Visit',
        'Fifteenth Visit', 'Sixteenth Visit'
    ]
    active_visits = visit_periods if selected_visits is None or 'All' in selected_visits else selected_visits
    
    # Farminfo data
    if not farminfo_fe_exists:
        breakdown_data['Dataset'].append('Farminfo')
        breakdown_data['Category'].append('Farminfo')
        breakdown_data['Count'].append(0)
        breakdown_data['Farmer IDs'].append(f'FE {fe_name} not found in Farminfo dataset')
    else:
        fe_farminfo = farminfo_valid[farminfo_valid['FE_Name'] == fe_name] if not farminfo_valid.empty else pd.DataFrame()
        farmer_count = fe_farminfo['Farmer ID'].nunique() if not fe_farminfo.empty else 0
        farmer_ids = ', '.join(sorted(fe_farminfo['Farmer ID'].astype(str).unique())) if not fe_farminfo.empty else '0'
        breakdown_data['Dataset'].append('Farminfo')
        breakdown_data['Category'].append('Farminfo')
        breakdown_data['Count'].append(farmer_count)
        breakdown_data['Farmer IDs'].append(farmer_ids)
    
    # Get farminfo Farmer IDs for "Not in" calculations
    farminfo_farmers = set(fe_farminfo['Farmer ID'].astype(str).unique()) if farminfo_fe_exists and not fe_farminfo.empty else set()
    
    # Fieldvisit data
    if not fieldvisit_fe_exists:
        for vp in active_visits:
            breakdown_data['Dataset'].append('Fieldvisit')
            breakdown_data['Category'].append(f'{vp} Farmers')
            breakdown_data['Count'].append(0)
            breakdown_data['Farmer IDs'].append(f'FE {fe_name} not found in Fieldvisit dataset')
            breakdown_data['Dataset'].append('Fieldvisit')
            breakdown_data['Category'].append(f'Not in {vp}')
            breakdown_data['Count'].append(0)
            breakdown_data['Farmer IDs'].append(f'FE {fe_name} not found in Fieldvisit dataset')
    else:
        _, _, detailed_df = analyze_visit_data(fieldvisit_valid, farminfo_df, cluster, selected_visits)
        fe_fieldvisit = detailed_df[detailed_df['FE Name'] == fe_name] if not detailed_df.empty else pd.DataFrame()
        for vp in active_visits:
            # {vp} Farmers
            breakdown_data['Dataset'].append('Fieldvisit')
            breakdown_data['Category'].append(f'{vp} Farmers')
            if not fe_fieldvisit.empty and f'{vp} Farmers' in fe_fieldvisit['Category'].values:
                row = fe_fieldvisit[fe_fieldvisit['Category'] == f'{vp} Farmers'].iloc[0]
                breakdown_data['Count'].append(row['Count'])
                breakdown_data['Farmer IDs'].append(row['Farmer IDs'])
            else:
                breakdown_data['Count'].append(0)
                breakdown_data['Farmer IDs'].append('0')
            
            # Not in {vp}
            breakdown_data['Dataset'].append('Fieldvisit')
            breakdown_data['Category'].append(f'Not in {vp}')
            if not fe_fieldvisit.empty and f'{vp} Farmers' in fe_fieldvisit['Category'].values:
                visit_farmers = set(fe_fieldvisit[fe_fieldvisit['Category'] == f'{vp} Farmers']['Farmer IDs'].iloc[0].split(', ')) if fe_fieldvisit[fe_fieldvisit['Category'] == f'{vp} Farmers']['Farmer IDs'].iloc[0] != '0' else set()
                not_in_vp = farminfo_farmers - visit_farmers
                breakdown_data['Count'].append(len(not_in_vp))
                breakdown_data['Farmer IDs'].append(', '.join(sorted(not_in_vp)) if not_in_vp else '0')
            else:
                breakdown_data['Count'].append(len(farminfo_farmers))
                breakdown_data['Farmer IDs'].append(', '.join(sorted(farminfo_farmers)) if farminfo_farmers else '0')
    
    # Rainfall data
    if not rainfall_fe_exists:
        for vp in active_visits:
            breakdown_data['Dataset'].append('Rainfall')
            breakdown_data['Category'].append(f'{vp} Farmers')
            breakdown_data['Count'].append(0)
            breakdown_data['Farmer IDs'].append(f'FE {fe_name} not found in Rainfall dataset')
            breakdown_data['Dataset'].append('Rainfall')
            breakdown_data['Category'].append(f'Not in {vp}')
            breakdown_data['Count'].append(0)
            breakdown_data['Farmer IDs'].append(f'FE {fe_name} not found in Rainfall dataset')
    else:
        _, _, detailed_df = analyze_visit_data(rainfall_valid, farminfo_df, cluster, selected_visits)
        fe_rainfall = detailed_df[detailed_df['FE Name'] == fe_name] if not detailed_df.empty else pd.DataFrame()
        for vp in active_visits:
            # {vp} Farmers
            breakdown_data['Dataset'].append('Rainfall')
            breakdown_data['Category'].append(f'{vp} Farmers')
            if not fe_rainfall.empty and f'{vp} Farmers' in fe_rainfall['Category'].values:
                row = fe_rainfall[fe_rainfall['Category'] == f'{vp} Farmers'].iloc[0]
                breakdown_data['Count'].append(row['Count'])
                breakdown_data['Farmer IDs'].append(row['Farmer IDs'])
            else:
                breakdown_data['Count'].append(0)
                breakdown_data['Farmer IDs'].append('0')
            
            # Not in {vp}
            breakdown_data['Dataset'].append('Rainfall')
            breakdown_data['Category'].append(f'Not in {vp}')
            if not fe_rainfall.empty and f'{vp} Farmers' in fe_rainfall['Category'].values:
                visit_farmers = set(fe_rainfall[fe_rainfall['Category'] == f'{vp} Farmers']['Farmer IDs'].iloc[0].split(', ')) if fe_rainfall[fe_rainfall['Category'] == f'{vp} Farmers']['Farmer IDs'].iloc[0] != '0' else set()
                not_in_vp = farminfo_farmers - visit_farmers
                breakdown_data['Count'].append(len(not_in_vp))
                breakdown_data['Farmer IDs'].append(', '.join(sorted(not_in_vp)) if not_in_vp else '0')
            else:
                breakdown_data['Count'].append(len(farminfo_farmers))
                breakdown_data['Farmer IDs'].append(', '.join(sorted(farminfo_farmers)) if farminfo_farmers else '0')
    
    combined_df = pd.DataFrame(breakdown_data)
    print(f"Debug: Combined FE Breakdown shape: {combined_df.shape}")
    return combined_df

def get_missing_fes(data, cluster=None):
    """Identify FEs not present in farminfo dataset with dataset context"""
    all_fes = set()
    for df_key, df in data.items():
        if not df.empty and 'FE_Name' in df.columns:
            all_fes.update(df['FE_Name'].dropna().unique())
    
    farminfo_fes = set(data['farminfo']['FE_Name'].dropna().unique()) if not data['farminfo'].empty and 'FE_Name' in data['farminfo'].columns else set()
    if cluster and cluster != "All" and not data['farminfo'].empty and 'Cluster name' in data['farminfo'].columns:
        farminfo_fes = set(data['farminfo'][data['farminfo']['Cluster name'] == cluster]['FE_Name'].dropna().unique())
    
    missing_fes = all_fes - farminfo_fes
    missing_data = []
    for fe in missing_fes:
        if fe not in data['fieldvisit']['FE_Name'].dropna().unique() if not data['fieldvisit'].empty and 'FE_Name' in data['fieldvisit'].columns else True:
            missing_data.append({'FE Name': fe, 'Missing In': 'Fieldvisit'})
        if fe not in data['rainfall']['FE_Name'].dropna().unique() if not data['rainfall'].empty and 'FE_Name' in data['rainfall'].columns else True:
            missing_data.append({'FE Name': fe, 'Missing In': 'Rainfall'})
    
    missing_df = pd.DataFrame(missing_data).drop_duplicates()
    print(f"Debug: Missing FEs shape: {missing_df.shape}")
    return missing_df

def main():
    # Main title
    st.markdown('<h1 class="main-header">🌾 FE Data Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading data..."):
        data = load_data()
    
    # Get cluster options
    cluster_options = ['All']
    if not data['farminfo'].empty and 'Cluster name' in data['farminfo'].columns:
        cluster_options.extend(sorted(data['farminfo']['Cluster name'].dropna().unique()))
    
    # Cluster selector
    selected_cluster = st.selectbox("Select Cluster:", options=cluster_options, key="global_cluster_selector")
    
    # Visit multiselector
    visit_periods = [
        'All', 'First Visit', 'Second Visit', 'Third Visit', 'Fourth Visit', 'Fifth Visit', 
        'Sixth Visit', 'Seventh Visit', 'Eighth Visit', 'Ninth Visit', 'Tenth Visit',
        'Eleventh Visit', 'Twelfth Visit', 'Thirteenth Visit', 'Fourteenth Visit',
        'Fifteenth Visit', 'Sixteenth Visit'
    ]
    selected_visits = st.multiselect("Select Visit Periods (select 'All' to include all visits):", 
                                     options=visit_periods, 
                                     default=['All'], 
                                     key="global_visit_selector")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Farminfo Analysis", "🏃‍♂️ Fieldvisit Analysis", "🌧️ Rainfall Analysis", "🔗 Combined FE Analysis"])
    
    # TAB 1: FARMINFO ANALYSIS
    with tab1:
        st.markdown('<h2 class="tab-subheader">📋 Farminfo Data Analysis</h2>', unsafe_allow_html=True)
        
        # Display missing FEs
        missing_fes_df = get_missing_fes(data, selected_cluster)
        if not missing_fes_df.empty:
            st.markdown('<div class="warning-text">FEs not present in other datasets:</div>', unsafe_allow_html=True)
            st.dataframe(missing_fes_df, use_container_width=True)
        
        if data['farminfo'].empty:
            st.error("No farminfo data available")
        else:
            original_df = data['farminfo']
            _, valid_df = clean_farmer_data(original_df)
            
            if selected_cluster != "All" and 'Cluster name' in original_df.columns:
                original_df = original_df[original_df['Cluster name'] == selected_cluster]
                valid_df = valid_df[valid_df['Cluster name'] == selected_cluster] if not valid_df.empty else valid_df
            
            # Overall Statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(original_df))
            with col2:
                st.metric("Total FEs", original_df['FE_Name'].nunique() if 'FE_Name' in original_df.columns else 0)
            with col3:
                st.metric("Unique Farmers", valid_df['Farmer ID'].nunique() if not valid_df.empty and 'Farmer ID' in valid_df.columns else 0)
            
            # FE Summary Table
            st.subheader("📊 FE Performance Summary")
            summary_df = create_fe_summary_table(original_df, valid_df, selected_cluster)
            if not summary_df.empty:
                st.dataframe(summary_df, use_container_width=True)
                if st.button("Show Chart for FE Performance Summary", key="farminfo_summary_chart"):
                    chart_data = summary_df.set_index('FE Name')['Farmer Count']
                    st.bar_chart(chart_data)
                
                # FEs with less than 5 farmers
                st.subheader("⚠️ FEs with Less than 5 Farmer Data")
                less_than_5 = summary_df[summary_df['Farmer Count'] < 5]
                if not less_than_5.empty:
                    st.markdown('<div class="warning-text">', unsafe_allow_html=True)
                    st.dataframe(less_than_5, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.success("All FEs have collected 5 or more farmer data!")
                
                # Duplicate farmer data
                st.subheader("🔄 FEs with Same Farmer Data")
                if not valid_df.empty:
                    duplicate_df = find_duplicate_farmers(valid_df, selected_cluster)
                    if not duplicate_df.empty:
                        st.markdown('<div class="warning-text">', unsafe_allow_html=True)
                        st.dataframe(duplicate_df, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.success("No duplicate farmer data found across FEs!")
                else:
                    st.info("No valid farmer data to check for duplicates")
                
                # FE Selector for detailed breakdown
                st.subheader("🔍 Individual FE Breakdown")
                if 'FE_Name' in original_df.columns:
                    selected_fe = st.selectbox("Select FE for detailed analysis:", 
                                             options=original_df['FE_Name'].dropna().unique(),
                                             key="farminfo_fe_selector")
                    
                    if selected_fe:
                        fe_summary = summary_df[summary_df['FE Name'] == selected_fe]
                        if not fe_summary.empty:
                            fe_row = fe_summary.iloc[0]
                            st.write(f"**FE Name:** {selected_fe}")
                            st.write(f"**Total Farmers:** {fe_row['Farmer Count']}")
                            st.write(f"**Farmer IDs:** {fe_row['Farmer IDs']}")
                            if st.button("Show Chart for Individual FE", key=f"farminfo_fe_chart_{selected_fe}"):
                                chart_data = pd.DataFrame({'Count': [fe_row['Farmer Count']]}, index=['Total Farmers'])
                                st.bar_chart(chart_data)
    
    # TAB 2: FIELDVISIT ANALYSIS
    with tab2:
        st.markdown('<h2 class="tab-subheader">🏃‍♂️ Fieldvisit Data Analysis</h2>', unsafe_allow_html=True)
        
        # Display missing FEs
        missing_fes_df = get_missing_fes(data, selected_cluster)
        if not missing_fes_df.empty:
            st.markdown('<div class="warning-text">FEs not present in other datasets:</div>', unsafe_allow_html=True)
            st.dataframe(missing_fes_df, use_container_width=True)
        
        if data['fieldvisit'].empty:
            st.error("No fieldvisit data available")
        else:
            original_df = data['fieldvisit']
            _, valid_df = clean_farmer_data(original_df)
            
            if selected_cluster != "All" and not data['farminfo'].empty and 'Cluster name' in data['farminfo'].columns:
                cluster_farmers = data['farminfo'][data['farminfo']['Cluster name'] == selected_cluster]['Farmer ID'].dropna().unique()
                original_df = original_df[original_df['Farmer ID'].isin(cluster_farmers)]
                valid_df = valid_df[valid_df['Farmer ID'].isin(cluster_farmers)] if not valid_df.empty else valid_df
            
            # Overall Statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Records", len(original_df))
            with col2:
                st.metric("Total FEs", original_df['FE_Name'].nunique() if 'FE_Name' in original_df.columns else 0)
            with col3:
                st.metric("Unique Farmers", valid_df['Farmer ID'].nunique() if not valid_df.empty and 'Farmer ID' in valid_df.columns else 0)
            with col4:
                if 'Visit date' in original_df.columns:
                    st.metric("Visit Records", original_df['Visit date'].notna().sum())
                else:
                    st.metric("Visit Records", 0)
            
            # Analyze visit data
            visit_summary_df, comparison_df, detailed_df = analyze_visit_data(original_df, data['farminfo'], selected_cluster, selected_visits)
            
            if not comparison_df.empty:
                # Visit Comparison Table
                st.subheader("📊 FE Visit Comparison Summary")
                st.dataframe(comparison_df, use_container_width=True)
                if st.button("Show Chart for FE Visit Comparison Summary", key="fieldvisit_comparison_chart"):
                    chart_data = comparison_df.set_index('FE Name')
                    if 'All' in selected_visits:
                        chart_data = chart_data[[f'Unique Farmers {vp}' for vp in visit_periods[1:]] + ['Farmers in Multiple Visits']]
                    else:
                        chart_data = chart_data[[f'Unique Farmers {vp}' for vp in selected_visits]]
                    st.bar_chart(chart_data, use_container_width=True)
                
                # Detailed Visit Analysis
                st.subheader("📅 Visit Period Analysis")
                visit_list = visit_periods[1:] if 'All' in selected_visits else selected_visits
                
                for vp in visit_list:
                    st.write(f"**{vp} Analysis**")
                    vp_detail = detailed_df[detailed_df['Category'] == f'{vp} Farmers']
                    if not vp_detail.empty:
                        st.dataframe(vp_detail[['FE Name', 'Count', 'Farmer IDs']], use_container_width=True)
                        if st.button(f"Show Chart for {vp} Analysis", key=f"fieldvisit_{vp.lower().replace(' ', '_')}_chart"):
                            chart_data = vp_detail.set_index('FE Name')['Count']
                            st.bar_chart(chart_data, use_container_width=True)
                
                # FE Selector for detailed breakdown
                st.subheader("🔍 Individual FE Breakdown")
                if 'FE_Name' in original_df.columns:
                    selected_fe = st.selectbox("Select FE for detailed analysis:", 
                                             options=original_df['FE_Name'].dropna().unique(),
                                             key="fieldvisit_fe_selector")
                    
                    if selected_fe:
                        fe_breakdown = detailed_df[detailed_df['FE Name'] == selected_fe]
                        # Add Farminfo data
                        farminfo_filtered = data['farminfo']
                        if selected_cluster != "All" and 'Cluster name' in farminfo_filtered.columns:
                            farminfo_filtered = farminfo_filtered[farminfo_filtered['Cluster name'] == selected_cluster]
                        _, farminfo_valid = clean_farmer_data(farminfo_filtered)
                        farminfo_fe = farminfo_valid[farminfo_valid['FE_Name'] == selected_fe] if not farminfo_valid.empty else pd.DataFrame()
                        farminfo_row = {
                            'FE Name': selected_fe,
                            'Category': 'Farminfo',
                            'Count': farminfo_fe['Farmer ID'].nunique() if not farminfo_fe.empty else 0,
                            'Farmer IDs': ', '.join(sorted(farminfo_fe['Farmer ID'].astype(str).unique())) if not farminfo_fe.empty else f'<span class="warning-text">FE {selected_fe} not found in Farminfo dataset</span>'
                        }
                        fe_breakdown = pd.concat([pd.DataFrame([farminfo_row]), fe_breakdown]) if not fe_breakdown.empty else pd.DataFrame([farminfo_row])
                        if not fe_breakdown.empty:
                            st.markdown(fe_breakdown[['Category', 'Count', 'Farmer IDs']].to_html(escape=False), unsafe_allow_html=True)
                            if st.button("Show Chart for Individual FE", key=f"fieldvisit_fe_chart_{selected_fe}"):
                                chart_data = fe_breakdown.set_index('Category')['Count']
                                st.bar_chart(chart_data, use_container_width=True)
            else:
                st.warning("No visit data found for analysis")
    
    # TAB 3: RAINFALL ANALYSIS
    with tab3:
        st.markdown('<h2 class="tab-subheader">🌧️ Rainfall Data Analysis</h2>', unsafe_allow_html=True)
        
        # Display missing FEs
        missing_fes_df = get_missing_fes(data, selected_cluster)
        if not missing_fes_df.empty:
            st.markdown('<div class="warning-text">FEs not present in other datasets:</div>', unsafe_allow_html=True)
            st.dataframe(missing_fes_df, use_container_width=True)
        
        if data['rainfall'].empty:
            st.error("No rainfall data available")
        else:
            original_df = data['rainfall']
            _, valid_df = clean_farmer_data(original_df)
            
            if selected_cluster != "All" and not data['farminfo'].empty and 'Cluster name' in data['farminfo'].columns:
                cluster_farmers = data['farminfo'][data['farminfo']['Cluster name'] == selected_cluster]['Farmer ID'].dropna().unique()
                original_df = original_df[original_df['Farmer ID'].isin(cluster_farmers)]
                valid_df = valid_df[valid_df['Farmer ID'].isin(cluster_farmers)] if not valid_df.empty else valid_df
            
            # Overall Statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Records", len(original_df))
            with col2:
                st.metric("Total FEs", original_df['FE_Name'].nunique() if 'FE_Name' in original_df.columns else 0)
            with col3:
                st.metric("Unique Farmers", valid_df['Farmer ID'].nunique() if not valid_df.empty and 'Farmer ID' in valid_df.columns else 0)
            with col4:
                if 'Visit date' in original_df.columns:
                    st.metric("Visit Records", original_df['Visit date'].notna().sum())
                else:
                    st.metric("Visit Records", 0)
            
            # Analyze visit data
            visit_summary_df, comparison_df, detailed_df = analyze_visit_data(original_df, data['farminfo'], selected_cluster, selected_visits)
            
            if not comparison_df.empty:
                # Visit Comparison Table
                st.subheader("📊 FE Visit Comparison Summary")
                st.dataframe(comparison_df, use_container_width=True)
                if st.button("Show Chart for FE Visit Comparison Summary", key="rainfall_comparison_chart"):
                    chart_data = comparison_df.set_index('FE Name')
                    if 'All' in selected_visits:
                        chart_data = chart_data[[f'Unique Farmers {vp}' for vp in visit_periods[1:]] + ['Farmers in Multiple Visits']]
                    else:
                        chart_data = chart_data[[f'Unique Farmers {vp}' for vp in selected_visits]]
                    st.bar_chart(chart_data, use_container_width=True)
                
                # Detailed Visit Analysis
                st.subheader("📅 Visit Period Analysis")
                visit_list = visit_periods[1:] if 'All' in selected_visits else selected_visits
                
                for vp in visit_list:
                    st.write(f"**{vp} Analysis**")
                    vp_detail = detailed_df[detailed_df['Category'] == f'{vp} Farmers']
                    if not vp_detail.empty:
                        st.dataframe(vp_detail[['FE Name', 'Count', 'Farmer IDs']], use_container_width=True)
                        if st.button(f"Show Chart for {vp} Analysis", key=f"rainfall_{vp.lower().replace(' ', '_')}_chart"):
                            chart_data = vp_detail.set_index('FE Name')['Count']
                            st.bar_chart(chart_data, use_container_width=True)
                
                # FE Selector for detailed breakdown
                st.subheader("🔍 Individual FE Breakdown")
                if 'FE_Name' in original_df.columns:
                    selected_fe = st.selectbox("Select FE for detailed analysis:", 
                                             options=original_df['FE_Name'].dropna().unique(),
                                             key="rainfall_fe_selector")
                    
                    if selected_fe:
                        fe_breakdown = detailed_df[detailed_df['FE Name'] == selected_fe]
                        # Add Farminfo data
                        farminfo_filtered = data['farminfo']
                        if selected_cluster != "All" and 'Cluster name' in farminfo_filtered.columns:
                            farminfo_filtered = farminfo_filtered[farminfo_filtered['Cluster name'] == selected_cluster]
                        _, farminfo_valid = clean_farmer_data(farminfo_filtered)
                        farminfo_fe = farminfo_valid[farminfo_valid['FE_Name'] == selected_fe] if not farminfo_valid.empty else pd.DataFrame()
                        farminfo_row = {
                            'FE Name': selected_fe,
                            'Category': 'Farminfo',
                            'Count': farminfo_fe['Farmer ID'].nunique() if not farminfo_fe.empty else 0,
                            'Farmer IDs': ', '.join(sorted(farminfo_fe['Farmer ID'].astype(str).unique())) if not farminfo_fe.empty else f'<span class="warning-text">FE {selected_fe} not found in Farminfo dataset</span>'
                        }
                        fe_breakdown = pd.concat([pd.DataFrame([farminfo_row]), fe_breakdown]) if not fe_breakdown.empty else pd.DataFrame([farminfo_row])
                        if not fe_breakdown.empty:
                            st.markdown(fe_breakdown[['Category', 'Count', 'Farmer IDs']].to_html(escape=False), unsafe_allow_html=True)
                            if st.button("Show Chart for Individual FE", key=f"rainfall_fe_chart_{selected_fe}"):
                                chart_data = fe_breakdown.set_index('Category')['Count']
                                st.bar_chart(chart_data, use_container_width=True)
            else:
                st.warning("No visit data found for analysis")
    
    # TAB 4: COMBINED FE ANALYSIS
    with tab4:
        st.markdown('<h2 class="tab-subheader">🔗 Combined FE Analysis</h2>', unsafe_allow_html=True)
        
        # Display missing FEs
        missing_fes_df = get_missing_fes(data, selected_cluster)
        if not missing_fes_df.empty:
            st.markdown('<div class="warning-text">FEs not present in other datasets:</div>', unsafe_allow_html=True)
            st.dataframe(missing_fes_df, use_container_width=True)
        
        # Get all unique FE names from all datasets, filtered by cluster
        all_fes = set()
        if not data['farminfo'].empty and 'Cluster name' in data['farminfo'].columns and selected_cluster != "All":
            cluster_farmers = data['farminfo'][data['farminfo']['Cluster name'] == selected_cluster]['Farmer ID'].dropna().unique()
            for df in [data['farminfo'], data['fieldvisit'], data['rainfall']]:
                if not df.empty and 'FE_Name' in df.columns and 'Farmer ID' in df.columns:
                    temp_df = df[df['Farmer ID'].isin(cluster_farmers)]
                    all_fes.update(temp_df['FE_Name'].dropna().unique())
        else:
            for df in [data['farminfo'], data['fieldvisit'], data['rainfall']]:
                if not df.empty and 'FE_Name' in df.columns:
                    all_fes.update(df['FE_Name'].dropna().unique())
        
        all_fes = sorted(list(all_fes))
        
        if not all_fes:
            st.error("No Field Executives found in any dataset")
        else:
            selected_fe = st.selectbox("Select FE for combined analysis:", 
                                     options=all_fes,
                                     key="combined_fe_selector")
            
            if selected_fe:
                st.markdown(f'<h3 class="success-text">👤 Field Executive: {selected_fe}</h3>', unsafe_allow_html=True)
                
                # Get combined breakdown
                combined_df = get_combined_fe_breakdown(selected_fe, 
                                                     data['farminfo'], 
                                                     data['fieldvisit'], 
                                                     data['rainfall'], 
                                                     selected_cluster, 
                                                     selected_visits)
                
                # Display Farminfo Summary
                st.markdown('<h4>📋 Farm Info</h4>', unsafe_allow_html=True)
                farminfo_row = combined_df[combined_df['Dataset'] == 'Farminfo']
                if not farminfo_row.empty:
                    row = farminfo_row.iloc[0]
                    if 'not found' in row['Farmer IDs']:
                        st.markdown(f'<div class="warning-text">{row["Farmer IDs"]}</div>', unsafe_allow_html=True)
                    else:
                        st.write(f"**Farminfo ({row['Count']}):** {row['Farmer IDs']}")
                
                # Display Fieldvisit Summary
                st.markdown('<h4>🧾 Field Visit Summary</h4>', unsafe_allow_html=True)
                fieldvisit_rows = combined_df[combined_df['Dataset'] == 'Fieldvisit']
                if not fieldvisit_rows.empty:
                    if 'not found' in fieldvisit_rows['Farmer IDs'].iloc[0]:
                        st.markdown(f'<div class="warning-text">{fieldvisit_rows["Farmer IDs"].iloc[0]}</div>', unsafe_allow_html=True)
                    else:
                        for _, row in fieldvisit_rows.iterrows():
                            st.write(f"**{row['Category']} ({row['Count']}):** {row['Farmer IDs']}")
                
                # Display Rainfall Summary
                st.markdown('<h4>🌧️ Rainfall Summary</h4>', unsafe_allow_html=True)
                rainfall_rows = combined_df[combined_df['Dataset'] == 'Rainfall']
                if not rainfall_rows.empty:
                    if 'not found' in rainfall_rows['Farmer IDs'].iloc[0]:
                        st.markdown(f'<div class="warning-text">{rainfall_rows["Farmer IDs"].iloc[0]}</div>', unsafe_allow_html=True)
                    else:
                        for _, row in rainfall_rows.iterrows():
                            st.write(f"**{row['Category']} ({row['Count']}):** {row['Farmer IDs']}")
                
                # Chart for Combined FE Analysis
                if st.button("Show Chart for Combined FE Analysis", key=f"combined_fe_chart_{selected_fe}"):
                    chart_data = combined_df[combined_df['Farmer IDs'].str.contains('not found') == False]
                    if not chart_data.empty:
                        chart_data = chart_data.pivot(index='Dataset', columns='Category', values='Count').fillna(0)
                        st.bar_chart(chart_data, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("📊 **FE Data Analysis Dashboard** | Built with Streamlit")

if __name__ == "__main__":
    main()