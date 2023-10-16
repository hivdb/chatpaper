import openai
import os


def chat_openai(model, messages, temperature=0):
    openai.api_key = os.getenv('OPENAI_API_KEY')

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature
    )

    return response


def embedding_openai(model, text):
    openai.api_key = os.getenv('OPENAI_API_KEY')

    return openai.Embedding.create(
        input=[text], model=model)['data'][0]['embedding']
