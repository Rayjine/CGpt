import streamlit as st
from client.ensembl_client import EnsemblClient

st.title("Genomics Explorer with Claude")

# Initialize the client
client = EnsemblClient()

# Create a text input for the user's question
user_question = st.text_input("Ask a genomics question:")

if st.button("Submit") and user_question:
    with st.spinner("Claude is thinking..."):
        response = client.query(user_question)
    st.write(response)

# Example questions
st.sidebar.header("Example Questions")
examples = [
    "What is the function of the BRCA1 gene?",
    "What are the known variants in the CFTR gene associated with cystic fibrosis?",
    "Where is the TP53 gene located in the human genome?",
    "What is the protein sequence of PSEN1?",
    "Which genes are involved in Alzheimer's disease?"
]

for example in examples:
    if st.sidebar.button(example):
        st.session_state.user_question = example
        st.experimental_rerun()