# streamlit_app.py
import streamlit as st
import multiprocessing
from bot import bot_process

def main():
    st.title("Telegram Bot Controller")
    
    if st.button("Start Bot"):
        if 'bot_process' not in st.session_state:
            st.session_state.bot_process = multiprocessing.Process(target=bot_process)
            st.session_state.bot_process.start()
            st.success("Bot started!")
    
    if st.button("Stop Bot"):
        if 'bot_process' in st.session_state:
            st.session_state.bot_process.terminate()
            del st.session_state.bot_process
            st.success("Bot stopped!")

if __name__ == '__main__':
    main()
