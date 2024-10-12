from Colors import BLUE,YELLOW,RED,RESET,GREEN
from langchain_core.messages import ToolMessage,AIMessage
import uuid
from The_State import State
import fireworks.client
import time
import base64
from playwright.sync_api import sync_playwright
from Tools import Click,Type,Scroll,Go_back,Wait
import requests
import json

######################################### Outher ##############################################
############################################################################################ 

def Go_To_Google(playwright):
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto('https://www.google.com/')
    time.sleep(5)
    return page, browser

def Annotate(page):
    mark_page_script = """
        const customCSS = `
            ::-webkit-scrollbar {
                width: 10px;
            }
            ::-webkit-scrollbar-track {
                background: #27272a;
            }
            ::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 0.375rem;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
        `;

        const styleTag = document.createElement("style");
        styleTag.textContent = customCSS;
        document.head.append(styleTag);

        let labels = [];

        function unmarkPage() {
          // Unmark page logic
          for (const label of labels) {
            document.body.removeChild(label);
          }
          labels = [];
        }

        function markPage() {
          unmarkPage();

          var bodyRect = document.body.getBoundingClientRect();

          var items = Array.prototype.slice
            .call(document.querySelectorAll("*"))
            .map(function (element) {
              var vw = Math.max(
                document.documentElement.clientWidth || 0,
                window.innerWidth || 0
              );
              var vh = Math.max(
                document.documentElement.clientHeight || 0,
                window.innerHeight || 0
              );
              var textualContent = element.textContent.trim().replace(/\s{2,}/g, " ");
              var elementType = element.tagName.toLowerCase();
              var ariaLabel = element.getAttribute("aria-label") || "";

              var rects = [...element.getClientRects()]
                .filter((bb) => {
                  var center_x = bb.left + bb.width / 2;
                  var center_y = bb.top + bb.height / 2;
                  var elAtCenter = document.elementFromPoint(center_x, center_y);

                  return elAtCenter === element || element.contains(elAtCenter);
                })
                .map((bb) => {
                  const rect = {
                    left: Math.max(0, bb.left),
                    top: Math.max(0, bb.top),
                    right: Math.min(vw, bb.right),
                    bottom: Math.min(vh, bb.bottom),
                  };
                  return {
                    ...rect,
                    width: rect.right - rect.left,
                    height: rect.bottom - rect.top,
                  };
                });

              var area = rects.reduce((acc, rect) => acc + rect.width * rect.height, 0);

              return {
                element: element,
                include:
                  element.tagName === "INPUT" ||
                  element.tagName === "TEXTAREA" ||
                  element.tagName === "SELECT" ||
                  element.tagName === "BUTTON" ||
                  element.tagName === "A" ||
                  element.onclick != null ||
                  window.getComputedStyle(element).cursor == "pointer" ||
                  element.tagName === "IFRAME" ||
                  element.tagName === "VIDEO",
                area,
                rects,
                text: textualContent,
                type: elementType,
                ariaLabel: ariaLabel,
              };
            })
            .filter((item) => item.include && item.area >= 20);

          // Only keep inner clickable items
          items = items.filter(
            (x) => !items.some((y) => x.element.contains(y.element) && !(x == y))
          );

          // Function to generate random colors
          function getRandomColor() {
            var letters = "0123456789ABCDEF";
            var color = "#";
            for (var i = 0; i < 6; i++) {
              color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
          }

          /// Lets create a floating border on top of these elements that will always be visible
          items.forEach(function (item, index) {
            item.rects.forEach((bbox) => {
              newElement = document.createElement("div");
              var borderColor = getRandomColor();
              newElement.style.outline = `2px dashed ${borderColor}`;
              newElement.style.position = "fixed";
              newElement.style.left = bbox.left + "px";
              newElement.style.top = bbox.top + "px";
              newElement.style.width = bbox.width + "px";
              newElement.style.height = bbox.height + "px";
              newElement.style.pointerEvents = "none";
              newElement.style.boxSizing = "border-box";
              newElement.style.zIndex = 2147483647;
              // newElement.style.background = `${borderColor}80`;

              // Add floating label at the corner
              var label = document.createElement("span");
              label.textContent = index;
              label.style.position = "absolute";
              // These we can tweak if we want
              label.style.top = "-19px";
              label.style.left = "0px";
              label.style.background = "black"; // Set background to black
              label.style.color = "white";
              label.style.padding = "2px 4px";
              label.style.fontSize = "14px"; // Increase the font size
              label.style.fontWeight = "bold"; // Make the text bold
              label.style.borderRadius = "2px";
              newElement.appendChild(label);

              document.body.appendChild(newElement);
              labels.push(newElement);
              // item.element.setAttribute("-ai-label", label.textContent);
            });
          });
          const coordinates = items.flatMap((item) =>
            item.rects.map(({ left, top, width, height }) => ({
              x: (left + left + width) / 2,
              y: (top + top + height) / 2,
              type: item.type,
              text: item.text,
              ariaLabel: item.ariaLabel,
            }))
          );
          return coordinates;
        }
    """
    
    page.evaluate(mark_page_script)
    for _ in range(10):
        try:
            bboxes = page.evaluate("markPage()")
            break
        except Exception:
            # May be loading...
            time.sleep(3)
    screenshot = page.screenshot()
    page.evaluate("unmarkPage()")
    return {
        "img": base64.b64encode(screenshot).decode(), # str
        "bboxes": bboxes, # List[Dict]
    }

def main():
    with sync_playwright() as playwright:
        page, browser = Go_To_Google(playwright)
        result = Annotate(page)
        browser.close()
        return result, page
    
######################################### Tools ##############################################
############################################################################################ 
def Tools_function(state:State):
    page = state["page"]
    ###################### Get the Id of the Item
    args   = state["Agent_response"]["args"]
    action = state["Agent_response"]["action"]
    print(f"{BLUE} Action : {action} {YELLOW} Arguments {args} {RESET}")
    
    if len(args) > 0: 
        bbox_id = args[0] 
        bbox_id = int(bbox_id) # To convert from str to int
        ####################### Get the BBOX of the Item
        try:
            bbox = state["bboxes"][bbox_id]
        except Exception:
            return f"Error: no bbox for : {bbox_id}"
        ###################### Click in x,y coordinates
        x, y = bbox["x"], bbox["y"]
        
    if action == "Click":
        message = Click(page,bbox_id,x,y)
    elif action == "Type":
        text = args[1]
        message= Type(page,bbox_id,x,y,text)
    elif action == "Scroll":
        message= Scroll(page,args,x,y)
    elif action == "Wait":
        message= Wait()
    elif action == "Back":
        message= Go_back(page)
    elif action == "Go_Google":
        message= Go_To_Google(page)
    else:
        print("action unknowen")
    Tool_Message= ToolMessage(content=message,name=action, tool_call_id=str(uuid.uuid4()))
    return {"messages": Tool_Message}
    
######################################### MLLM ##############################################
############################################################################################ 

fireworks.client.api_key = "vM776YwjfS5VNRGwtYWGbaCM0qrphAfPUfO4DB9TV3pWcP7M"
System_Prompt = """Imagine you are a robot browsing the web, just like humans. Now you need to complete a task. In each iteration, you will receive an Observation that includes a screenshot of a webpage and some texts. This screenshot will

feature Numerical Labels placed in the TOP LEFT corner of each Web Element. Carefully analyze the visual

information to identify the Numerical Label corresponding to the Web Element that requires interaction, then follow

the guidelines and choose one of the following actions:

1. Click a Web Element.

2. Type something

3. Scroll up or down.

4. Wait 

5. Go back

6. Return to google to start over.

8. Respond with the final answer

A list of Possible Actions Names : actions ["Click","Type","Scroll","Wait","Back","Go_Google","FINISH"]

Arguments of each action are :

- Click : [Numerical_Label]

- Type : [Numerical_Label,content to Type]

- Scroll : [Numerical_Label or WINDOW, up or down]

- Wait  : []

- Back  : []

- Go_Google : []

- FINISH  : [] (if you want to Respond with the final answer)

Key Guidelines You MUST follow:

* Action guidelines *

1) Execute only one action per iteration.

2) When clicking or typing, ensure to select the correct bounding box.

3) Numeric labels lie in the top-left corner of their corresponding bounding boxes and are colored the same.

* Web Browsing Guidelines *

1) Don't interact with useless web elements like Login, Sign-in, donation that appear in Webpages

2) Select strategically to minimize time wasted.

"""

def format_descriptions(state:State):
    labels = []
    for i, bbox in enumerate(state["bboxes"]):
        text = bbox.get("ariaLabel") or ""
        if not text.strip():
            text = bbox["text"]
        el_type = bbox.get("type")
        labels.append(f'{i} (<{el_type}/>): "{text}"')
    state["bbox_descriptions"] = "\nValid Bounding Boxes:\n" + "\n".join(labels)
    return state

def MLLM_FireLLava(state:State):
    state = format_descriptions(state)
    User_request = state["User_request"]
    Image        = state["Image"]
    BBox_desc    = state["bbox_descriptions"]
    Old_messages = state["messages"]
    #print(state)
    response = fireworks.client.ChatCompletion.create(model = "accounts/fireworks/models/firellava-13b",
    messages = [
        {
        "role": "system",
        "content": System_Prompt
    },
        {"role": "user",
        "content": [
        {
        "type": "text",
        "text": f"""The User Request : {User_request}
        A description of Elements in the WebPage : {BBox_desc}
        
        Your response should be in a forme of a python dictionary with the following keys :
        
        action : str (The action to do)
        
        args : List[str] (arguments for the action)
        
        Dont't forget this :
        
                A list of Possible Actions Names : actions ["Click","Type","Scroll","Wait","Back","Go_Google","FINISH"]

                Arguments of each action are :

                - Click : [Numerical_Label]

                - Type : [Numerical_Label,content to Type]

                - Scroll : [Numerical_Label or WINDOW, up or down]

                - Wait  : []

                - Back  : []

                - Go_Google : []

                - FINISH  : [] (if you want to Respond with the final answer)
                
                - Numerical_Label can be found in the top left of each bounding box.(it's an int)
                
        The prevouis interactions here :
        
        {Old_messages}
        """,
        }, 
        {
        "type": "image_url",
        "image_url": {"url": f"data:image/jpeg;base64,{Image}"},
        }, ],
    }
    ]
    )
    message = response.choices[0].message.content
    MLLM_Message= AIMessage(content=message,name="Your Message")
    #return {"messages":MLLM_Message}
    return MLLM_Message

def Save_To_Local(Image64,image_path):
    image_data = base64.b64decode(Image64)
    with open(image_path, "wb") as f:
        f.write(image_data)
    print("Image saved")    
  