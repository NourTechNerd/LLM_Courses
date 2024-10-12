from typing import List, Optional, TypedDict
from playwright.async_api import Page
from langgraph.graph.message import add_messages
from typing import Annotated


class BBox(TypedDict):
    x: float
    y: float
    text: str
    type: str
    ariaLabel: str

class State(TypedDict):
    page              : Page  
    User_request      : str  
    Image_url         : str  # The Browser's SceenShot URL
    bboxes            : List[BBox]  # The bounding boxes from the browser annotation function.
    #bbox_descriptions : str
    Best_Action       : str
    action            : str
    args              : Optional[List[str]]
    Youtuber_Data     : str
    messages          : Annotated[list, add_messages] # The recorded messages.
    

     





