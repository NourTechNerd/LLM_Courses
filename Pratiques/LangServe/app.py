#!/usr/bin/env python
from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain_fireworks import ChatFireworks
from langserve import add_routes
import os
from dotenv import load_dotenv
from langchain_core.pydantic_v1 import BaseModel, Field

load_dotenv()

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

add_routes(
    app,
    ChatFireworks(api_key=os.getenv("FIREWORKS_API_KEY"),model="accounts/fireworks/models/mixtral-8x22b-instruct",temperature=0.7),
    path="/fireworks",
    playground_type = "chat"
)



model = ChatFireworks(api_key=os.getenv("FIREWORKS_API_KEY"),model="accounts/fireworks/models/mixtral-8x22b-instruct",temperature=0.7)
prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
class Output(BaseModel):
    Joke: str = Field(description="This is the joke")
    
add_routes(
    app,
    prompt | model,
    path="/joke",
    #output_type=Output,
)





if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
    

