def get_qa_chain():
    from model import MyGPT4ALL
    from knowledgebase import MyKnowledgeBase
    from knowledgebase import (
        DOCUMENT_SOURCE_DIRECTORY
    )

    # import all the langchain modules
    from langchain.chains import RetrievalQA
    from langchain.embeddings import GPT4AllEmbeddings

    # GPT4ALL_MODEL_NAME='ggml-gpt4all-j-v1.3-groovy.bin'
    # GPT4ALL_MODEL_NAME='all-MiniLM-L6-v2-f16.gguf'
    # GPT4ALL_MODEL_NAME='orca-mini-3b-gguf2-q4_0.gguf'
    GPT4ALL_MODEL_NAME='mistral-7b-instruct-v0.1.Q4_0.gguf'
    GPT4ALL_MODEL_FOLDER_PATH='GPT4All_models'
    GPT4ALL_BACKEND='llama'
    GPT4ALL_ALLOW_STREAMING=True
    GPT4ALL_ALLOW_DOWNLOAD=False

    llm = MyGPT4ALL(
        model_folder_path=GPT4ALL_MODEL_FOLDER_PATH,
        model_name=GPT4ALL_MODEL_NAME,
        allow_streaming=GPT4ALL_ALLOW_STREAMING,
        allow_download=GPT4ALL_ALLOW_DOWNLOAD
    )

    embeddings = GPT4AllEmbeddings()

    kb = MyKnowledgeBase(
        pdf_source_folder_path=DOCUMENT_SOURCE_DIRECTORY
    )

    # get the retriver object from the vector db 
    retriever = kb.return_retriever_from_persistant_vector_db(embedder=embeddings)

    qa_chain = RetrievalQA.from_chain_type(
        llm = llm,
        chain_type='stuff',
        retriever=retriever,
        return_source_documents=False, verbose=True
    )

    return qa_chain

