import streamlit as st
from flows.nl_to_sql import process_nl_query


def run_ui():
    st.title("NLQ to SQL Agent")
    nl_query = st.text_input("Enter your natural language query:")
    if st.button("Generate SQL"):
        sql, result = process_nl_query(nl_query)
        st.write(f"SQL: {sql}")
        st.write("Result:")
        st.dataframe(result)
