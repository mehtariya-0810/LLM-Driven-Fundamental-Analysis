def injestion():

    from knowledgebase import MyKnowledgeBase
    from knowledgebase import (
        DOCUMENT_SOURCE_DIRECTORY
    )

    kb = MyKnowledgeBase(
            pdf_source_folder_path=DOCUMENT_SOURCE_DIRECTORY
    )

    print("=> Creating vector db. It might take a while. Please be patient.")
    kb.initiate_document_injetion_pipeline()
