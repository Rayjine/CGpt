#!/usr/bin/env python3
import os
from client.ensembl_client import EnsemblClient

def main():
    # Create the client
    client = EnsemblClient()
    
    print("Ensembl Genomics Assistant")
    print("==========================")
    print("Ask questions about genes, variants, and genomics.")
    print("Type 'exit' to quit.\n")
    
    # Run the interactive loop
    while True:
        # Get user question
        question = input("\nYour question: ")
        
        # Check if user wants to exit
        if question.lower() in ["exit", "quit", "q"]:
            break
            
        # Skip empty questions
        if not question.strip():
            continue
            
        print("\nThinking...\n")
        
        try:
            # Get response from Claude
            response = client.query(question)
            
            # Print the response
            print(response)
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()