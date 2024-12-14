import matplotlib.pyplot as plt
import streamlit as st

def create_probability_plot(probabilities):
    fig, ax = plt.subplots()
    ax.plot(probabilities, color="blue")
    ax.set_title("Win Probability")
    ax.set_xlabel("Move Number")
    ax.set_ylabel("White Win %")
    st.pyplot(fig)
