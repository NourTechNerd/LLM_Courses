from langserve import RemoteRunnable
from langchain.schema import SystemMessage, HumanMessage
import time

joke_chain = RemoteRunnable("http://localhost:8000/joke/")
LLM = RemoteRunnable("http://localhost:8000/Fireworks/")

################## Example 1

prompt_LLM = [
    SystemMessage(content='Your name is TextGuru. You are a helpful assistant.'),
    HumanMessage(content='Hello!')
]

#print(joke_chain.invoke({"topic": "About Dogs"}))
"""for chunk in LLM.stream(prompt):
    print(chunk.content, end=" ")
"""
################## Example 2
from langserve import CustomUserType
VLM = RemoteRunnable("http://localhost:8000/Flash/")

class VLM_Input(CustomUserType):
    text: str
    Image_URL : str


image_url = "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"
Mytext = "What you see ?"
Input = VLM_Input(text=Mytext,Image_URL=image_url)
response = VLM.invoke(Input)
print(response)
print(type(response))