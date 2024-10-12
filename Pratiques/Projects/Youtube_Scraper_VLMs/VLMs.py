from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Any


load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class Navigator_Output(BaseModel):
    """Identifying Next action and its arguments"""
    Action    : str = Field(..., description="This is the next action to perform")
    Arguments : str = Field(..., description="This is the python List of arguments of the next action")
    
class Extractor_Output(BaseModel):
    """Identifying the  The youtuber data in a form of a python dictionary"""
    Youtuber_data  : str  = Field(..., description="""This is are the extracted informations 
                                  in a form of a python dictionary,if there is no data, respond with this : 'No data founded' """)


Leader_System = """You are The Leader of the Youtuber Search Team.\n  

- Your Team Memebers are : \n
    - The Navigator  : A guy that can navigate the Web Browser\n
    _ The Navigator can Click, Type, Scroll, Wait for somthing to Load and he can Go back to the previous page.\n
    - The Extractor : A guy that can extract informations about the Youtuber from the Web Page.\n
    
- Your Task is  : \n
    - Tell The just the Navigator What to do next based on the Current Web Page and The prevoius interactions.\n 
    
- Steps to perform your mission  with efficiency:\n

    1. Observe The ScreenShot Image of the current Web Page to Undestand is it and what countains.\n
    2. Try to find What to do next in order to discover Informations about this Youtuber.\n 
    
- In each iteration, you will receive : \n
  
  - The User request.\n
  - The ScreenShot Image of the current Web Page.\n
  - The previous conversations of your team.\n
    
- Important Notes : \n
    
    - Don't Try to connect or Sign up or Sign in with any service.\n
    - Do not describe what you see just perform your task .\n
    - Give just One suggestion not multiple.\n
    - Your Suggestion must beconcise and runnable.\n
    - You can end the search with : FINISH keyword.\n
    """

Navigator_System = """You are a robot browsing the web, just like humans and a Team member of the Youtuber Search Team.\n 

- Your Team Memebers are : \n
    - The Leader : The guy that is leading this team and Tell you what to do next.\n
    - The Extractor : A guy that can extract informations about the Youtuber from the Web Page.\n

- Your Task is  : \n
    -  Determine the Next action and its arguments.Based on The Leader suggestion\n

- Steps to perform your mission  with efficiency:\n

   1.  Observe the Bounding Boxes descriptions properly (It Countains the Numerical Labels ,types of the Webpage Elements).\n
   2.  Observe the Given annotated ScreenShot Image Try to figure out The numerical labels in the top left of each Bounding Box.\n
   3.  Observe The suggestion of Your Leader.
   3.  Finaly Give the Next action to do with the appropriate action name and action arguments.\n
   
- In each iteration, you will receive : \n
  
  - The suggestion from the Leader.\n
  - The ScreenShot Image of the current Web Page.\n
  - The Bounding Boxes descriptions of the Web page Elements.\n

  
- Important Notes : \n 
   
    - Give just One Action with arguments not multiple.\n
    - The  Numerical Labels are palaced in the TOP LEFT corner of each bounding box.and provided also in the Bounding Boxes descriptions.\n
    - The available actions names are : Click, Type, Scroll, Wait, Back.\n
    - Don't interact with useless web elements like Login, Sign-in, donation that appear in Webpages.\n
    - Arguments of each action are :\n

            - Click : [Numerical_Label]

            - Type : [Numerical_Label,content to Type]

            - Scroll : [Numerical_Label or WINDOW, up or down]

            - Wait  : []

            - Back  : [] \n   
    - Some Informations about Types :
    
            - <textarea/> : Where you can Type something.\n
            - <input/>   : Where you can Click something.\n
            
    - Do not describe what you see just perform your task .\n
            
"""

Extractor_System =  """You are an expert at Extracting informations about the Youtuber from the Web Page,and a Team member of the Youtuber Search Team.\n 

- Your Team Memebers are : \n
    - The Leader : The guy that is leading this team and Tell you what to do next.\n
    - The Navigator : A guy that can navigate the Web Browser.he can Click, Type, Scroll...\n

- Your Task is  : \n
    -  Extract Informations about the Youtuber from the Web Page.\n

- Steps to perform your mission  with efficiency:\n

   1.  Observe the Given  ScreenShot of the Web Page.\n
   2.  Extract Informations about the Youtuber from the Web Page like : Fist Name,Last Name,Email,Bio,Social Links, Subscribers, etc.\n
   3.  Finaly organize the extracted Informations With the help informations in one single a python dictionary format.\n
   
- In each iteration, you will receive : \n
  
  - The ScreenShot Image of the current Web Page.\n
  - The help data already extracted about the youtuber.\n
  
- Important Notes : \n 

  - if there is no data, Youtuber_data will be this : 'No data founded' \n
  -  The extracted Informations are organized in a python dictionary format.\n
  -  The extracted Informations must be accurate and Correct.\n
  - Do not describe what you see just perform your task .\n
            
"""

vlm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",api_key=GOOGLE_API_KEY,temperature=0.2)

Navigator = vlm.with_structured_output(Navigator_Output)
#Extractor = vlm.with_structured_output(Extractor_Output)

def Run_Leader(User_request,image_url,history):
    Leader_response=vlm.invoke(
        [
            SystemMessage(content=Leader_System),
            HumanMessage(
                content=[
                    {"type": "text",
                     "text":  f"""This is the annotated ScreenShot Image of the current Web Page\n
                           The User Request : {User_request}\n
                           The previous conversations of your team : {history}\n
                        """
                    },
                    {"type": "image_url", "image_url": {"url": image_url}},
                ]
            )
        ]
    )
    return Leader_response
   
def Run_Navigator(image_url,bbox_descriptions,Best_Action):  
    Messages =  [
            SystemMessage(content=Navigator_System),
            HumanMessage(
                content=[
                    {"type": "text",
                     "text": f"""This is the annotated ScreenShot Image of the current Web Page\n
                           The Bounding Boxes descriptions{bbox_descriptions}\n\n
                           The Suggestion of Your Leader : {Best_Action}\n
                        """
                    },
                    {"type": "image_url", "image_url": {"url": image_url}},
                ]
            )
        ]
    Navigator_response=Navigator.invoke(Messages)
    return Navigator_response

def Run_Extractor(image_url,Help_data):  
    Extractor_response=vlm.invoke(
        [
            SystemMessage(content=Extractor_System),
            HumanMessage(
                content=[
                    {"type": "text", "text": 
                        
                        f"""This is the ScreenShot Image of the current Web Page Extract the Youtuber Informations.\n
                           The help data already extracted about the youtuber : {Help_data}\n"""
                    },
                    {"type": "image_url", "image_url": {"url": image_url}},
                ]
            )
        ]
    )
    return Extractor_response
    












