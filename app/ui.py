import streamlit as st
from core.game_manager import GameManager
from core.graph_plot import create_probability_plot
from core.board_visualizer import render_board

def render_ui():
    st.title("BattleMind Chess Showdown")

    # Session state initialization
    if "game" not in st.session_state:
        st.session_state.game = GameManager()

    game = st.session_state.game

    # Layout: Board and Info
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Chessboard")
        render_board(game)

    with col2:
        st.subheader("Move List")
        st.write("\n".join(game.move_history))

        st.subheader("AI Thinking...")
        st.progress(game.ai_think_percentage)

    # Probability graph
    st.subheader("Win Probability")
    create_probability_plot(game.probabilities)

    # Action Buttons
    if st.button("Make AI Move"):
        game.make_ai_move()
    elif st.button("Restart Game"):
        game.reset()
