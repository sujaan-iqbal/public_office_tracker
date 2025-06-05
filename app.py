import streamlit as st
from pathlib import Path
import pandas as pd
import json
from src.data_loader import DataLoader
from src.validator import DataValidator
from src.analyzer import DataAnalyzer
from src.exporter import DataExporter

# Set page config
st.set_page_config(
    page_title="Public Office Data Tracker",
    page_icon="🏛️",
    layout="wide"
)

# Custom CSS
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found. Using default styles.")

local_css("style.css")

# Initialize session state
if 'officials_data' not in st.session_state:
    st.session_state.officials_data = None
if 'officials_df' not in st.session_state:
    st.session_state.officials_df = None

# App title and description
st.title("🏛️ Public Office Data Tracker")
st.markdown("""
A tool for collecting, organizing, and analyzing public records of elected officials.
""")

# Sidebar for data management
with st.sidebar:
    st.header("Data Management")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload JSON file", 
        type=["json"],
        help="Upload a JSON file containing officials data"
    )
    
    # Load default data button
    if st.button("Load Sample Data"):
        try:
            data = DataLoader.load_json("data/officials.json")
            validator = DataValidator("data/schema.json")
            
            if validator.validate_data(data):
                st.session_state.officials_data = data
                officials_list = DataLoader.get_officials(data)
                st.session_state.officials_df = DataAnalyzer.officials_to_dataframe(officials_list)
                st.success("Sample data loaded successfully!")
            else:
                st.error("Sample data validation failed")
        except Exception as e:
            st.error(f"Error loading sample data: {str(e)}")
    
    # Export options
    if st.session_state.officials_data:
        st.header("Export Options")
        export_format = st.selectbox(
            "Select export format",
            ["CSV", "JSON"]
        )
        
        if st.button(f"Export as {export_format}"):
            try:
                officials = DataLoader.get_officials(st.session_state.officials_data)
                if export_format == "CSV":
                    DataExporter.export_to_csv(officials, "officials_export.csv")
                    with open("officials_export.csv", "rb") as f:
                        st.download_button(
                            "Download CSV",
                            f,
                            file_name="officials_export.csv"
                        )
                else:
                    DataExporter.export_to_json(officials, "officials_export.json")
                    with open("officials_export.json", "rb") as f:
                        st.download_button(
                            "Download JSON",
                            f,
                            file_name="officials_export.json"
                        )
                st.success(f"Data exported to {export_format} successfully!")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")

# Main content area
if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        validator = DataValidator("data/schema.json")
        
        if validator.validate_data(data):
            st.session_state.officials_data = data
            officials_list = DataLoader.get_officials(data)
            st.session_state.officials_df = DataAnalyzer.officials_to_dataframe(officials_list)
            st.success("File uploaded and validated successfully!")
        else:
            st.error("Data validation failed")
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

if st.session_state.officials_df is not None:
    st.header("Data Overview")
    
    # Show raw data
    if st.checkbox("Show raw data"):
        st.dataframe(st.session_state.officials_df)
    
    # Statistics with column existence checks
    st.subheader("Basic Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Officials", len(st.session_state.officials_df))
    
    with col2:
        if 'party' in st.session_state.officials_df.columns:
            unique_parties = st.session_state.officials_df['party'].nunique()
            st.metric("Unique Parties", unique_parties)
        else:
            st.metric("Unique Parties", "N/A")
    
    with col3:
        if 'designation' in st.session_state.officials_df.columns:
            unique_designations = st.session_state.officials_df['designation'].nunique()
            st.metric("Unique Designations", unique_designations)
        else:
            st.metric("Unique Designations", "N/A")
    
    # Visualization tabs with error handling
    tab1, tab2, tab3 = st.tabs(["Party Distribution", "Designation Breakdown", "Social Media Presence"])
    
    with tab1:
        if 'party' in st.session_state.officials_df.columns:
            try:
                party_counts = st.session_state.officials_df['party'].value_counts().reset_index()
                party_counts.columns = ['party', 'count']
                st.bar_chart(party_counts.set_index('party'))
            except Exception as e:
                st.error(f"Could not generate party distribution: {str(e)}")
        else:
            st.warning("Party information not available in the dataset")
    
    with tab2:
        if 'designation' in st.session_state.officials_df.columns:
            try:
                designation_counts = st.session_state.officials_df['designation'].value_counts().reset_index()
                designation_counts.columns = ['designation', 'count']
                st.bar_chart(designation_counts.set_index('designation'))
            except Exception as e:
                st.error(f"Could not generate designation breakdown: {str(e)}")
        else:
            st.warning("Designation information not available in the dataset")
    
    with tab3:
        if 'social_media' in st.session_state.officials_df.columns:
            try:
                df_with_social = st.session_state.officials_df.copy()
                # Safely extract social media data
                social_data = {
                    'twitter': [],
                    'facebook': [],
                    'instagram': []
                }
                
                for sm in df_with_social['social_media']:
                    if isinstance(sm, dict):
                        for platform in social_data.keys():
                            social_data[platform].append(sm.get(platform))
                    else:
                        for platform in social_data.keys():
                            social_data[platform].append(None)
                
                for platform, values in social_data.items():
                    df_with_social[platform] = values
                
                social_cols = [col for col in ['twitter', 'facebook', 'instagram'] 
                             if col in df_with_social.columns and df_with_social[col].notna().any()]
                
                if social_cols:
                    social_counts = pd.DataFrame({
                        'Platform': social_cols,
                        'Count': [df_with_social[col].notna().sum() for col in social_cols]
                    })
                    st.bar_chart(social_counts.set_index('Platform'))
                    
                    st.subheader("Officials with Social Media")
                    display_cols = ['name']
                    if 'designation' in df_with_social.columns:
                        display_cols.append('designation')
                    if 'party' in df_with_social.columns:
                        display_cols.append('party')
                    
                    st.dataframe(
                        df_with_social[display_cols + social_cols].dropna(
                            how='all', 
                            subset=social_cols
                        )
                    )
                else:
                    st.warning("No social media data available")
            except Exception as e:
                st.error(f"Error processing social media data: {str(e)}")
        else:
            st.warning("Social media data not available in the dataset")
    
    # Search functionality with column checks
    st.header("Search Officials")
    search_col1, search_col2 = st.columns(2)
    
    with search_col1:
        search_name = st.text_input("Search by name")
    
    with search_col2:
        party_options = ["All"]
        if 'party' in st.session_state.officials_df.columns:
            party_options.extend(st.session_state.officials_df['party'].dropna().unique().tolist())
        search_party = st.selectbox("Filter by party", party_options)
    
    filtered_df = st.session_state.officials_df.copy()
    
    if search_name:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search_name, case=False, na=False)
        ]
    
    if search_party != "All" and 'party' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['party'] == search_party]
    
    st.dataframe(filtered_df)
    
    # Add new official form
    st.header("Add New Official")
    with st.form("new_official_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name*")
            designation = st.text_input("Designation*")
            jurisdiction = st.text_input("Jurisdiction*")
        
        with col2:
            party = st.text_input("Political Party")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
        
        st.subheader("Social Media")
        twitter = st.text_input("Twitter (handle or URL)")
        facebook = st.text_input("Facebook URL")
        instagram = st.text_input("Instagram (handle or URL)")
        
        submitted = st.form_submit_button("Add Official")
        
        if submitted:
            if not name or not designation or not jurisdiction:
                st.error("Please fill in required fields (marked with *)")
            else:
                new_official = {
                    "name": name,
                    "designation": designation,
                    "jurisdiction": jurisdiction,
                    "party": party if party else None
                }
                
                # Add contact info if provided
                if email or phone:
                    new_official["contact"] = {}
                    if email:
                        new_official["contact"]["email"] = email
                    if phone:
                        new_official["contact"]["phone"] = phone
                
                # Add social media if provided
                social_media = {}
                if twitter:
                    social_media["twitter"] = twitter
                if facebook:
                    social_media["facebook"] = facebook
                if instagram:
                    social_media["instagram"] = instagram
                
                if social_media:
                    new_official["social_media"] = social_media
                
                # Validate and add to data
                try:
                    validator = DataValidator("data/schema.json")
                    if validator.validate_official(new_official):
                        if 'officials' not in st.session_state.officials_data:
                            st.session_state.officials_data['officials'] = []
                        st.session_state.officials_data['officials'].append(new_official)
                        st.session_state.officials_df = DataAnalyzer.officials_to_dataframe(
                            DataLoader.get_officials(st.session_state.officials_data)
                        )
                        st.success("Official added successfully!")
                    else:
                        st.error("Validation failed. Please check your inputs.")
                except Exception as e:
                    st.error(f"Error adding official: {str(e)}")
else:
    st.info("Please upload a JSON file or load sample data to get started")