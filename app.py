import streamlit as st
from app.ui import render_ui

def main():
    st.set_page_config(page_title="BattleMind Chess", layout="wide")
    render_ui()

if __name__ == "__main__":
    main()
