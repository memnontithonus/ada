from google import genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Google GenAI client
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def main():
    print("ADA (Advanced Design Assistant) initialized. Type 'exit' to quit.")
    
    while True:
        try:
            user_input = input("\nEnter your message: ")
            
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            # Generate response
            response = model.generate_content(user_input)
            
            # Print response
            print("\nADA:", response.text)
            
        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    main()