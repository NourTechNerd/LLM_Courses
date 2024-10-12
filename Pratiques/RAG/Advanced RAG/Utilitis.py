from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os


load_dotenv()

embedder = GoogleGenerativeAIEmbeddings(google_api_key=os.getenv("GOOGLE_API_KEY"))
### Load Files

def Load_Files(Data_Path):
    loader = DirectoryLoader(Data_Path,show_progress=True)
    documents = loader.load()
    return documents

### Chunking

def Chunk(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks

### Create Chroma Vector Store

import shutil

def Save_to_chroma(chunks,CHROMA_PATH):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    db = Chroma.from_documents(chunks, embedder, persist_directory=CHROMA_PATH)
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")
    







