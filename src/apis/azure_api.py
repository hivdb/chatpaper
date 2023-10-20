import openai
import os


def chat_azure(model, messages, temperature=0):
    openai.api_key = os.getenv('AZURE_OPEN_AI_API_KEY')
    openai.api_base = os.getenv('AZURE_OPEN_AI_API_ENDPOINT')
    openai.api_type = os.getenv('AZURE_OPEN_AI_API_TYPE')
    openai.api_version = os.getenv('AZURE_OPEN_AI_API_VERSION')

    if model == 'gpt-4-32k':
        engine = os.getenv('AZURE_GPT4_32K_ID')
    else:
        raise Exception(f"Not supported model {model}")

    response = openai.ChatCompletion.create(
        engine=engine,
        messages=messages,
        temperature=temperature
    )

    return response


def embedding_azure(model, text):
    openai.api_key = os.getenv('AZURE_OPEN_AI_API_KEY')
    openai.api_base = os.getenv('AZURE_OPEN_AI_API_ENDPOINT')
    openai.api_type = os.getenv('AZURE_OPEN_AI_API_TYPE')
    openai.api_version = os.getenv('AZURE_OPEN_AI_API_VERSION')

    engine = os.getenv('AZURE_EMBEDDING_ID')

    return openai.Embedding.create(
        input=[text],
        model=model,
        engine=engine)['data'][0]['embedding']
