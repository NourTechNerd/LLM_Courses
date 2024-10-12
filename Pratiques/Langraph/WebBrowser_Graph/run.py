from Functions import main,MLLM_FireLLava,Save_To_Local
from The_State import State
from langchain_core.messages import ToolMessage,AIMessage
import json

result,page = main()
Question = "I want to buy an online ticket with ONCF The National Railway Office"
Image = result["img"]
Bounding_boxes = result["bboxes"]
Messages = [ToolMessage(content="Google lanched",tool_call_id="111")]

state_test = State(Image=Image,User_request=Question,bboxes=Bounding_boxes,messages= Messages)
#response = MLLM_FireLLava(state_test)
#print(response.content)
response = MLLM_Phi3Vision(state_test)
response_content = response.json()
print(json.dumps(response_content, indent=4))  # Pretty-print the JSON response

Save_To_Local(Image,image_path=r"C:\Users\hp\Downloads\LLM_Courses\Pratiques\Langraph\WebBrowser_Graph\output1_image.png")



