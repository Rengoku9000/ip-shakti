import streamlit as st
st.set_page_config(page_title="SidebarTest", layout="wide", initial_sidebar_state="expanded")
with st.sidebar:
    st.write("## SIDEBAR TEST")
    st.write("Sidebar is working!")
    st.radio("Nav", ["A", "B", "C"])
st.title("Main Content")
st.write("Sidebar should be on the left.")
