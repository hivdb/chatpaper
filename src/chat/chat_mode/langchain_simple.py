from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from src.apis.embedding import get_vectordb
from ..chat_history import ChatHistory


def chat_one_question(model, prompt_template, paper_file_path):
    chat_history = ChatHistory(paper_file_path, model)

    index_folder = paper_file_path.parent / 'index'
    db = get_vectordb(paper_file_path, index_folder)
    retriever = db.as_retriever()

    question = input('\nPlease enter your question: ')
    prompt = prompt_template.format(question=question)

    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(
            temperature=0,
            model_name=model,
        ), chain_type="stuff", retriever=retriever)
    answer = (qa.run(prompt))
