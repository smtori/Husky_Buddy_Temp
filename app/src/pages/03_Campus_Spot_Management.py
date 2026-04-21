"""Handles Campus Spot Management UI + Logic"""

import logging
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks
from typing import Optional, Any

# creates logger object for module - for debug/info/error messages
logger = logging.getLogger(__name__)

# configures streamlit page with title and landscape layout
st.set_page_config(page_title='Campus Spot Management', layout='wide')

# renders sidebar navigation (logo, go to home, user auth check)
SideBarLinks()

st.header("Manage Campus Spots")

# return to Admin Home page
if st.button("← Back to Admin Home", type="primary", use_container_width=False):
    st.switch_page('pages/00_Admin_Home.py')

API_BASE = 'http://api:4000'

# ---- Fetch all campus spots ----
def fetch_campus_spots() -> Any:
    try:
        response = requests.get(f"{API_BASE}/campus-spots")
        if response.status_code == 200:
            return response.json()
        else:
            try:
                error_msg = response.json().get('error', 'Unknown error')
            except:
                error_msg = f"HTTP {response.status_code}: {response.text}"
            st.error(f"Error fetching spots: {error_msg}")
            return []
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return []

# ---- Create a new campus spot ----
def create_campus_spot(spot_name: Any, location: Any) -> Optional[None]:
    try:
        response = requests.post(
            f"{API_BASE}/campus-spots",
            json={"spot_name": spot_name, "location": location}
        )
        if response.status_code == 201:
            st.success("Campus spot created successfully!")
            st.rerun()
        else:
            try:
                error_msg = response.json().get('error', 'Unknown error')
            except:
                error_msg = f"HTTP {response.status_code}: {response.text}"
            st.error(f"Error: {error_msg}")
    except Exception as e:
        st.error(f"Connection error: {str(e)}")

# ---- Update a campus spot ----
def update_campus_spot(spot_id: Any, spot_name: Any, location: Any) -> Optional[None]:
    try:
        response = requests.put(
            f"{API_BASE}/campus-spots/{spot_id}",
            json={"spot_name": spot_name, "location": location}
        )
        if response.status_code == 200:
            st.success("Campus spot updated successfully!")
            st.rerun()
        else:
            try:
                error_msg = response.json().get('error', 'Unknown error')
            except:
                error_msg = f"HTTP {response.status_code}: {response.text}"
            st.error(f"Error: {error_msg}")
    except Exception as e:
        st.error(f"Connection error: {str(e)}")

# ---- Delete a campus spot ----
def delete_campus_spot(spot_id: Any) -> Optional[None]:
    try:
        response = requests.delete(f"{API_BASE}/campus-spots/{spot_id}")
        if response.status_code == 200:
            st.success("Campus spot deleted successfully!")
            st.rerun()
        else:
            try:
                error_msg = response.json().get('error', 'Unknown error')
            except:
                error_msg = f"HTTP {response.status_code}: {response.text}"
            st.error(f"Error: {error_msg}")
    except Exception as e:
        st.error(f"Connection error: {str(e)}")

# ---- Main UI ----
st.divider()

# Create two columns for add spot form and view spots
col1, col2 = st.columns([1, 2])

# ---- Left column: Add new spot form ----
with col1:
    st.subheader("Add New Spot")
    with st.form("add_spot_form"):
        new_spot_name = st.text_input("Spot Name", placeholder="e.g., Library Lounge")
        new_location = st.text_input("Location", placeholder="e.g., 3rd Floor, Main Library")
        submitted = st.form_submit_button("Create Spot", use_container_width=True)
        
        if submitted:
            if new_spot_name and new_location:
                create_campus_spot(new_spot_name, new_location)
            else:
                st.error("Please fill in all fields")

# ---- Right column: View and manage existing spots ----
with col2:
    st.subheader("Existing Spots")
    spots = fetch_campus_spots()
    
    if spots:
        # Display spots in a table
        spots_df = pd.DataFrame(spots)
        st.dataframe(spots_df, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("Edit or Delete a Spot")
        
        # Select spot to edit/delete
        spot_options = {f"{spot['spot_name']} - {spot['location']}": spot for spot in spots}
        selected_spot_display = st.selectbox("Select a spot", list(spot_options.keys()))
        selected_spot = spot_options[selected_spot_display]
        
        # Create two columns for edit and delete buttons
        edit_col, delete_col = st.columns(2)
        
        with edit_col:
            if st.button("Edit Spot", use_container_width=True):
                st.session_state.editing_spot_id = selected_spot['spot_id']
        
        with delete_col:
            if st.button("Delete Spot", use_container_width=True, type="secondary"):
                st.session_state.confirm_delete_id = selected_spot['spot_id']
        
        # Show confirmation if delete was clicked
        if "confirm_delete_id" in st.session_state:
            st.warning(f"Are you sure you want to delete this spot?")
            confirm_col, cancel_col = st.columns(2)
            
            with confirm_col:
                if st.button("Confirm Delete", use_container_width=True, type="primary"):
                    delete_campus_spot(st.session_state.confirm_delete_id)
                    del st.session_state.confirm_delete_id
            
            with cancel_col:
                if st.button("Cancel", use_container_width=True):
                    del st.session_state.confirm_delete_id
                    st.rerun()
        
        # ---- Edit form (shown when editing) ----
        if "editing_spot_id" in st.session_state:
            st.divider()
            st.subheader("Edit Spot")
            
            edit_spot = next(s for s in spots if s['spot_id'] == st.session_state.editing_spot_id)
            
            with st.form("edit_spot_form"):
                edited_name = st.text_input("Spot Name", value=edit_spot['spot_name'])
                edited_location = st.text_input("Location", value=edit_spot['location'])
                
                if st.form_submit_button("Save Changes", use_container_width=True):
                    if edited_name and edited_location:
                        update_campus_spot(edit_spot['spot_id'], edited_name, edited_location)
                    else:
                        st.error("Please fill in all fields")
            
            # Cancel button outside the form
            if st.button("Cancel Edit", use_container_width=True):
                del st.session_state.editing_spot_id
                st.rerun()
    else:
        st.info("No campus spots found. Create one to get started!")



