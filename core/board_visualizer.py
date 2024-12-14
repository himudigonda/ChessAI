import chess
import streamlit as st

def render_board(game):
    board_svg = game.board._repr_svg_()
    st.image(board_svg, use_column_width=True)
