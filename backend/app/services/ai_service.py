from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_cheatsheet(text:str)->str:
    prompt = prompt = f"""
        Can you read the context of the file and create a cheat sheet for all the information which will be useful in 
        the exams?

        CONTENT:
        {text}
    """

    response = client.responses.create(
        model="gpt-4o-mini",
        input = [
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.output_text
