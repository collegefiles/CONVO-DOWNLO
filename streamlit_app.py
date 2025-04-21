import streamlit as st
import multiprocessing
from bot import run_bot
import os

def main():
    st.title("Telegram Bot Controller")
    
    if not os.getenv('TELEGRAM_TOKEN'):
        st.error("Telegram token not configured!")
        st.markdown("""
        Please add your token to:
        1. `.streamlit/secrets.toml` for local development
        2. Streamlit Sharing secrets for deployment
        """)
        return
    
    if st.button("Start Bot"):
        if 'bot_process' not in st.session_state:
            st.session_state.bot_process = multiprocessing.Process(
                target=run_bot,
                daemon=True
            )
            st.session_state.bot_process.start()
            st.success("Bot started successfully!")
    
    if st.button("Stop Bot"):
        if 'bot_process' in st.session_state:
            st.session_state.bot_process.terminate()
            del st.session_state.bot_process
            st.success("Bot stopped successfully!")

if __name__ == '__main__':
    main()
