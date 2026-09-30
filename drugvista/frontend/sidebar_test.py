"""Minimal sidebar test"""
import streamlit as st

st.set_page_config(
    page_title="Sidebar Test",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.markdown("## SIDEBAR TEST")
    st.write("If you can see this, the native Streamlit sidebar is working.")
    st.radio("Nav", ["Option A", "Option B", "Option C"])

st.title("Main Content Area")
st.write("The sidebar should be visible on the left.")

