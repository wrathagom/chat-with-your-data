import streamlit as st

st.title('Current State')

st.write('This page shows the current Streamlit state, it is mostly for debugging purposes.')

st.divider()

st.write(st.session_state)