from pydantic import BaseModel, Field
from typing import Union, List
from openai import OpenAI
import os

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

system_content = """
You will be provided a conversation between a recruiter and a chatbot. The conversation is about describing a job position a recruiter is looking for and the ideal candidate for this position. 
You must convert the descriptin into the structure described in the response format.
Your goal is to output a json with the informations from the description following the response format.
For the work experience block, you must fill all the fields, you can invent the name of a company or institution and enrich the description, when required experience duration is provided, start date and end date should be consistent with the duration.
"""
class WorkExperience(BaseModel):
    title: Union[str, None] = Field(description="Job Title")
    company: Union[str, None] = Field(description="Company name")
    location: Union[str, None] = Field(description="location of the job")
    contract_type: Union[str, None] = Field(description="Type of the contract")
    start_date: Union[str, None] = Field(description="Start date of the job")
    end_date: Union[str, None] = Field(description="End date of the job")
    description: Union[str, None] = Field(description="Description of the job along with skills and tools")


class CandidateProfile(BaseModel):
    work_experiences: List[WorkExperience] = Field(description="List of past work experiences")
    #skills: List[str] = Field(description="List of skills")


def create_candidate(description):
    response = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": description},
        ],
        response_format=CandidateProfile
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    save_session_path = "./data/session.txt"
    with open(save_session_path, 'r') as f:
        desc = f.read() 
    print(create_candidate(desc))