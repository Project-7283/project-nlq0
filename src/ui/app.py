import streamlit as st
from src.flows.nl_to_sql import process_nl_query
from src.utils.container import Container

def run_ui():
    st.set_page_config(page_title="NLQ to SQL Agent", layout="wide")
    st.title("NLQ to SQL Agent")
    
    # Initialize session state
    if "history" not in st.session_state:
        st.session_state.history = []
    if "current_result" not in st.session_state:
        st.session_state.current_result = None

    container = Container.get_instance()
    feedback_service = container.get_feedback_service()
    evolution_service = container.get_graph_evolution_service()

    nl_query = st.text_input("Enter your natural language query:")
    
    if st.button("Generate SQL"):
        with st.spinner("Generating SQL..."):
            try:
                sql, result, context = process_nl_query(nl_query)
                st.session_state.current_result = {
                    "query": nl_query,
                    "sql": sql,
                    "result": result,
                    "context": context,
                    "feedback_submitted": False
                }
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Display Results
    if st.session_state.current_result:
        data = st.session_state.current_result
        
        st.subheader("Generated SQL")
        st.code(data["sql"], language="sql")
        
        st.subheader("Result")
        st.dataframe(data["result"])
        
        # Feedback Section
        if not data["feedback_submitted"]:
            st.divider()
            st.subheader("Was this helpful?")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Yes, Correct"):
                    feedback_id = feedback_service.log_feedback(
                        user_query=data["query"],
                        generated_sql=data["sql"],
                        rating=1,
                        graph_context=data["context"]
                    )
                    # Trigger Evolution
                    evolution_service.process_positive_feedback({
                        "graph_context": data["context"]
                    })
                    st.success("Thanks for your feedback! The system has learned from this.")
                    data["feedback_submitted"] = True
                    st.rerun()
            
            with col2:
                if st.button("👎 No, Incorrect"):
                    st.session_state.show_negative_feedback_form = True

            if st.session_state.get("show_negative_feedback_form"):
                with st.form("negative_feedback"):
                    comment = st.text_area("What went wrong?", placeholder="e.g., Wrong table used, missing filter...")
                    submit = st.form_submit_button("Submit Feedback")
                    
                    if submit:
                        feedback_id = feedback_service.log_feedback(
                            user_query=data["query"],
                            generated_sql=data["sql"],
                            rating=-1,
                            user_comment=comment,
                            graph_context=data["context"]
                        )
                        st.success("Thanks! We'll use this to improve.")
                        data["feedback_submitted"] = True
                        st.session_state.show_negative_feedback_form = False
                        st.rerun()
