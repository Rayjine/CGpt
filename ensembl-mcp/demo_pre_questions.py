from client.ensembl_client import EnsemblClient

client = EnsemblClient(debug=True)

# Example genomics questions
questions = [
    "What is the function of the BRCA1 gene?",
    "What are the known variants in the CFTR gene associated with cystic fibrosis?",
    "Where is the TP53 gene located in the human genome?",
    "What is the protein sequence of PSEN1?",
    "Which genes are involved in Alzheimer's disease?"
]

# Test each question
for question in questions:
    print(f"\nQuestion: {question}")
    print("-" * 80)
    response = client.query(question)
    print(f"Response: {response}")
    print("=" * 80)