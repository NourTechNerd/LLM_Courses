########## just Colors :
# ANSI escape codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

from langchain_core.tools import StructuredTool
from langchain.pydantic_v1 import BaseModel, Field

################################ OpenWeather ##############################################
###########################################################################################
import os
from langchain_community.utilities import OpenWeatherMapAPIWrapper

os.environ["OPENWEATHERMAP_API_KEY"] = "173302c5b0b96d80bcb52bc315943bb9"
weather = OpenWeatherMapAPIWrapper()

# With this class I define my parametres of the tool and I give description that
#--> Will help the LLM to understand the  tool schema.
class OpenWeather_Arg(BaseModel):
    Location: str = Field(...,description="The Location is often a city name like London, Casablanca ...")

def run(Location:str) -> str:
    weather_data = weather.run(Location)
    return weather_data


OpenWeather = StructuredTool.from_function(
    func=run,
    name="OpenWeather",
    description="Give the Weather information for a specific Location",
    args_schema=OpenWeather_Arg,
    return_direct=False,
)

#print(OpenWeather.invoke("Meknes"))
####################################### Tavily ############################################
###########################################################################################
from langchain_community.tools.tavily_search import TavilySearchResults

os.environ["TAVILY_API_KEY"] = "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"
Tavily = TavilySearchResults(max_results=3,name="Tavily")
#print(Tavily.invoke("What is Langraph ?"))

####################################### AskNewsSearch ############################################
###########################################################################################

from langchain_community.tools.asknews import AskNewsSearch


os.environ["ASKNEWS_CLIENT_ID"] = "b4753573-7c63-4a42-be1e-27e6a4986db9"
os.environ["ASKNEWS_CLIENT_SECRET"] = "PlWZYQ7c1LX2At7NBKbrCcHV2l"

AskNews = AskNewsSearch(max_results=2)


####################################### RAG    ############################################
###########################################################################################

### Build The RAG System

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.ollama import OllamaEmbeddings
import os
import shutil



# Set embeddings

def Embedding_function():
    embeddings = OllamaEmbeddings(model="nomic-embed-text",show_progress =True)
    return embeddings

"""
# Docs to index
urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
]

# Load
docs = [WebBaseLoader(url).load() for url in urls]
docs = [item for sublist in docs for item in sublist]

# Split (Chunking)
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=500, chunk_overlap=80
)
chunks = text_splitter.split_documents(docs)

# Create Chroma DataBase :
CHROMA_PATH = "/teamspace/studios/this_studio/LLM_Courses/Pratiques/Langraph/Adaptive RAG/Chroma"

def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        
def save_to_chroma(chunks,Ids): 
    clear_database()
    # Create a new DB from the chunks.
    db = Chroma.from_documents(chunks, Embedding_function(), persist_directory=CHROMA_PATH,ids=Ids)
    db.persist() # Forcing the Save
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

def Create_Chunks_Ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0
    ids = []
    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Chunk Id
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id
        ids.append(chunk_id)
    return chunks,ids

chunks,ids = Create_Chunks_Ids(chunks)
save_to_chroma(chunks,ids)

"""

CHROMA_PATH = "/teamspace/studios/this_studio/LLM_Courses/Pratiques/Langraph/Adaptive RAG/Chroma"

def Get_Context(Question):
    # Searching for Relevent Chunks from DataBase
    results = db.similarity_search_with_relevance_scores(Question,k=3)
    context_text = "\n\n---\n\n".join([chunk.page_content for chunk, _score in results])
    return context_text

db = Chroma(persist_directory=CHROMA_PATH, embedding_function=Embedding_function())


## Use The RAG System as a Tool

from langchain_core.tools import StructuredTool
from langchain.pydantic_v1 import BaseModel, Field

class RAG_Arg(BaseModel):
    query: str = Field(...,description="""The query to use in searching for relevent information from  a the Database That countain
    articls about Agents, Prompt Engineering and Adversiral Attacks-LLMs""")

def Get_Context(query:str)-> str:
    # Searching for Relevent Chunks from DataBase
    results = db.similarity_search_with_relevance_scores(query,k=3)
    context_text = "\n\n---\n\n".join([chunk.page_content for chunk, _score in results])
    return context_text

RAG_System = StructuredTool.from_function(
    func=Get_Context,
    name="RAG System",
    description="This tool give a good informations about Agents, Prompt Engineering and Adversiral Attacks-LLMs",
    args_schema=RAG_Arg,
    return_direct=False,
)








