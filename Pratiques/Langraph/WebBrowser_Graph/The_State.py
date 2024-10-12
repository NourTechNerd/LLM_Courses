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

class MLLM_Response(TypedDict):
    action: str
    args: Optional[List[str]] # it's hold the id of the Item in the Image and may countain
                              # The text to type.

class State(TypedDict):
    page              : Page  
    User_request      : str  
    Image             : str  # The Browser's SceenShot
    bboxes            : List[BBox]  # The bounding boxes from the browser annotation function.
    bbox_descriptions : str
    Agent_response    : MLLM_Response  # The Agent's output
    messages          : Annotated[list, add_messages] # The recorded messages.

     





