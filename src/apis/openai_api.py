from openai import OpenAI
import openai
import os


def chat_openai(model, messages, temperature=0):

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        # max_tokens=2000
    )

    return response


def embedding_openai(model, text):
    openai.api_key = os.getenv('OPENAI_API_KEY')

    return openai.Embedding.create(
        input=[text], model=model)['data'][0]['embedding']
