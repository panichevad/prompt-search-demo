import streamlit as st
from openai import OpenAI
import os
import json
from pydantic import BaseModel, Field
from enum import Enum
from langchain_core.output_parsers import JsonOutputParser

parser = JsonOutputParser()

candidates_data_description = """
1. **Professional Headline**: A brief professional summary or title.
2. **Work Experiences**: Details of the candidate's work history, including:
   - Contract type (e.g., full-time, internship).
   - Organization details, including name, logo URL, reference, and URL.
   - Profession and specific title within the job.
   - Job description and key tasks carried out along with skills and tools used.
   - Location of the job, including city and country details.
   - Skills utilized in each role,  each with potential multilinguistic names, references, and types (e.g., tool, skill).
   - Start and end dates of each job.
   - Whether the job was full remote.
"""

system_content_candidate_new = """
You are an experienced recruitment assistant. Your objective is to help a recruiter identify and build the key 
attributes and qualifications for the perfect candidate for a specific job opening by facilitating a structured conversation.

Guidelines:
You will be provided a job title and desired experience level of a perfect candidate.

Gather Candidates Requirements:
- First ask the recruiter to add some details about the job opening.
- Then ask about preferred past experiences. 
- Based on the information of job opening and past experience, add soft skills and hard skills the candidate would have. DO NOT ask about education. 

Summarize the information gathered to ensure accuracy and completeness.
Confirm with the recruiter that all important aspects have been covered and ask if there’s anything else they’d like to add.

To keep a chat-based approach, gather the information in distinct question. 
Questions must be short and simple to keep the experience fluid, like WhatsApp messages.

Once all informations are gathered the final output must be a complete summary of what the recruiter is looking for.

FINAL OUTPUT:
COMPLETE SUMMARY OF THE INFORMATION GATHERED.

The message must be concised.
KEEP IT SHORT AND SIMPLE.
This SUMMARY MUST be your LAST message.
"""

# system_content_candidate_new_ = """
# You are a friendly recruitment assistant helping to build candidate profiles through casual chat. Keep responses short and conversational, like WhatsApp messages.

# Process:
# 1. User provides a job title and experience level
# 2. You'll ask brief, focused questions about:
#    - Key job responsibilities
#    - Required past experience
#    - Essential skills (both technical and soft skills)

# Guidelines:
# - Ask ONE question at a time
# - Keep questions short and informal
# - Wait for my response before moving to the next question
# - Maintain a natural conversation flow
# - If an answer needs clarification, ask follow-up questions

# After gathering all information, provide a concise summary with these sections:
# - Role Overview
# - Must-Have Experience
# - Key Skills
# - Nice-to-Have Qualities

# Keep the final summary under 200 words and in bullet points.
# """


class Status(str, Enum):
    in_progress = "In progress"
    finish = "Finished"


class ResponseModel(BaseModel):
    status: Status = Field(description="The status of the response, indicating whether the task is still ongoing or completed. When outputing the summary of the candidates. The status must pass to Finished")
    response: str = Field(description="The text content of the response from the assistant.  Each message should ask about one type of information and propose suggestions if relevant.")
    

# Initialize OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)


# Streamlit app
def main():
    st.title("AI SOURCING ASSISTANT")

    # Initialize session state for conversation
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": system_content_candidate_new + "\n" + candidates_data_description},
            {"role": "assistant", "content": "Enter the job title and required experience level for your open position"}]
    if 'action_description' not in st.session_state:
        st.session_state.action_description = "In progress"
    if 'next_actions' not in st.session_state:
        st.session_state.next_actions = []

    # Display conversation history
    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue
        st.chat_message(msg["role"]).write(msg["content"])

    # User input field at the bottom
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Add user input to conversation
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # Call OpenAI ChatCompletion
        response = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=st.session_state.messages,
            response_format=ResponseModel
        )

        # Process and display the response
        msg = response.choices[0].message.content
        print(msg)
        response_text = parser.parse(msg)["response"]
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.chat_message("assistant").write(response_text)

        if parser.parse(msg)["status"] == "Finished":
            data_path = './data/'
            if not os.path.exists(data_path):
                os.makedirs(data_path)
                print(f"Folder '{data_path}' created successfully")
            
            save_resume_path = "./data/resume.txt"
            with open(save_resume_path, 'w') as f: 
                f.write(response_text)
                f.close()
            st.session_state.action_description = "Finished"


    # Handle next actions when status is finish
    if st.session_state.action_description == "Finished":
        # save session output
        save_session_path = "./data/session.txt"
        with open(save_session_path, 'w') as f: 
            f.write(str(st.session_state.messages))
            f.close()

if __name__ == "__main__":
    main()
