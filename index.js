import { GoogleGenerativeAI } from "@google/generative-ai";
import * as dotenv from 'dotenv';
import readline from 'readline';

// Load environment variables
dotenv.config();

const GOOGLE_API_KEY = process.env.GOOGLE_API_KEY;

if (!GOOGLE_API_KEY) {
  console.error("Error: GOOGLE_API_KEY not found in environment variables.");
  process.exit(1);
}

// Initialize Google GenAI client
const genAI = new GoogleGenerativeAI(GOOGLE_API_KEY);
const model = genAI.getGenerativeModel({ model: "gemini-pro" });

// Create readline interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

async function main() {
  console.log("ADA (Advanced Design Assistant) initialized. Type 'exit' to quit.");

  while (true) {
    try {
      const userInput = await new Promise(resolve => {
        rl.question("\nEnter your message: ", resolve);
      });

      if (userInput.toLowerCase() === 'exit') {
        console.log("Goodbye!");
        rl.close();
        break;
      }

      // Generate response
      const result = await model.generateContent(userInput);
      const response = await result.response;
      
      // Print response
      console.log("\nADA:", response.text());
      
    } catch (error) {
      console.error("An error occurred:", error.message);
      continue;
    }
  }
}

main().catch(console.error);