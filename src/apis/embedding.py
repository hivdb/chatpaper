import tiktoken
import openai
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import DocArrayHnswSearch
from langchain.vectorstores import DocArrayInMemorySearch # noqa
from src.doc_format.md import MarkdownSectionLoader
from src.doc_format.md import MarkdownParagraphLoader
from .openai_api import embedding_openai


def get_token_length(text, model='gpt-3.5-turbo'):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)


def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return embedding_openai(model, text)


def get_vectordb(file_path, indexes_path, mode='section'):
    # TODO: get number of elements in index
    # TODO, check index is up-to-date with content, not with date
    # TODO, if one secion try embedding by paragraph
    index_folder = indexes_path / f'index_{mode}'

    if index_folder.exists():
        vectordb = load_index(str(index_folder))
    else:
        vectordb = embedding_markdown(file_path, str(index_folder), mode)

    return vectordb


def load_index(index_folder):
    embeddings = OpenAIEmbeddings()
    vectordb = DocArrayHnswSearch.from_params(
        work_dir=index_folder, embedding=embeddings, n_dim=1536)

    return vectordb


def embedding_markdown(
        file_path, index_folder, mode='section', chuck_overlap=0):

    # TODO, if section <= 3, use paragraph split

    if mode == 'paragraph':
        docs = MarkdownParagraphLoader(file_path).load()
    else:
        docs = MarkdownSectionLoader(file_path).load()
    # TODO, log meta, number of embedding body

    embeddings = OpenAIEmbeddings()

    vectordb = DocArrayHnswSearch.from_documents(
        docs,
        embeddings,
        work_dir=index_folder,
        n_dim=1536
    )
    return vectordb
