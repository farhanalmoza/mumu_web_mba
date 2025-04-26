import streamlit as st

st.title("Market Basket Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    st.header("Total Transaction")

with col2:
    st.header("Total Data")

with col3:
    st.header("Total Item")