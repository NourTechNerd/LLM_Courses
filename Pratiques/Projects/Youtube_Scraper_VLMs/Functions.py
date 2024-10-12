from langchain_core.messages import ToolMessage,AIMessage
import uuid
from The_State import State
from Tools import format_descriptions,string_to_list,Save_To_HuggingFace
from VLMs import Run_Extractor,Run_Navigator,Run_Leader
from colorama import Fore, Style,init
import io
import matplotlib.pyplot as plt
from PIL import Image
import asyncio

init(autoreset=True)

def print_readable_messages(messages):
    for idx, message in enumerate(messages, start=1):
        print(f"Message {idx}:")
        print(f"  Name: {message.name}")
        print(f"  Content:\n{message.content}\n")
        print("-" * 40)  # Separator for readability

def Leader_function(state:State):
    print(Style.BRIGHT+Fore.GREEN+"Leader ...")
    
    User_request = state["User_request"]
    Image_url = state["Image_url"]
    history = state["messages"][-3:]
    
    print("\nLen History : \n",len(history))
    
    print(f"\nUser Request :\n {User_request} ,\n Image :\n {Image_url} ,\n History\n\n")
    print_readable_messages(history)
    
    Leader_response = Run_Leader(User_request,Image_url,history)
    Leader_message = AIMessage(content=Leader_response.content,name = "Leader")
    return {"messages":Leader_message,"Best_Action":Leader_response.content}

def Navigator_function(state:State):
    print(Style.BRIGHT+Fore.GREEN+"Navigator ...")
    
    Image_url = state["Image_url"]
    bbox_descriptions = format_descriptions(state["bboxes"])
    Best_Action = state["Best_Action"]
    
    print(f"\nImage : \n{Image_url} ,\n Bbox Descriptions : \n{bbox_descriptions} ,\n Best Action : \n{Best_Action}\n\n")
    
    Navigator_response = Run_Navigator(Image_url,bbox_descriptions,Best_Action)
    print(f"\n Navigator_response : \n {Navigator_response}")
    Navigator_message = AIMessage(content=Navigator_response.Action,name = "Navigator")
    
    return {"messages":Navigator_message,"action":Navigator_response.Action,"args":string_to_list(Navigator_response.Arguments)}

def Extractor_function(state:State):
    print(Style.BRIGHT+Fore.GREEN+"Extractor ...")
    
    Image_url = state["Image_url"]
    Help_data = state["Youtuber_Data"]
    
    print(f"\nImage : \n{Image_url} ,\n Help Data : \n{Help_data}\n\n")
    
    Extractor_response = Run_Extractor(Image_url,Help_data)
    
    print(f"\n Extractor_response : \n {Extractor_response}")
    
    if Extractor_response is not None:
        Extractor_message = AIMessage(content=Extractor_response.content,name = "Extractor")
        return {"messages":Extractor_message,"Youtuber_Data":Extractor_response.content}
  
async def Click_function(state:State):  
    page = state["page"]
    ###################### Get the Id of the Item
    args   = state["args"]
    action = state["action"]
    print(Style.BRIGHT+Fore.YELLOW+f"Action : {action} , Args : {args}")
    bbox_id = args[0] 
    bbox_id = int(bbox_id) # To convert from str to int
    ####################### Get the BBOX of the Item
    try:
        bbox = state["bboxes"][bbox_id]
        x, y = bbox["x"], bbox["y"]
        await page.mouse.click(x, y)
        message = f"Clicked {bbox_id}"
    except Exception:
        message = "Error: no bbox for : {bbox_id} or Bad Arguments"
        
    print(Style.BRIGHT+message)
    Tool_Message= ToolMessage(content=message,name=action, tool_call_id=str(uuid.uuid4()))
    return {"messages": Tool_Message}

async def Type_function(state:State):
    page = state["page"]
    ###################### Get the Id of the Item
    args   = state["args"]
    action = state["action"]
    ###################### Get the Id of the Item
    args   = state["args"]
    action = state["action"]
    print(Style.BRIGHT+Fore.YELLOW+f"Action : {action} , Args : {args}")
    text = args[1]
    bbox_id = args[0] 
    bbox_id = int(bbox_id) # To convert from str to int
    ####################### Get the BBOX of the Item
    try:
        bbox = state["bboxes"][bbox_id]
        x, y = bbox["x"], bbox["y"]
        await page.mouse.click(x, y)
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Backspace")
        await page.keyboard.type(text)
        await page.keyboard.press("Enter")
        message = f"Typed {text} and submitted"
    except Exception:
        message = "Error: no bbox for : {bbox_id} or Bad Arguments"
  
    print(Style.BRIGHT+message)
    Tool_Message = ToolMessage(content=message,name=action, tool_call_id=str(uuid.uuid4()))
    return {"messages": Tool_Message}
  

async def Scroll_function(state:State):
    page = state["page"]
    ###################### Get the Id of the Item
    args   = state["args"]
    action = state["action"]
    ###################### Get the Id of the Item
    args   = state["args"]
    action = state["action"]
    print(Style.BRIGHT+Fore.YELLOW+f"Action : {action} , Args : {args}") 
    target, direction = args
    ############################### Scroll in the main Window
    if target.upper() == "WINDOW":
        scroll_amount = 500
        scroll_direction = (-scroll_amount if direction.lower() == "up" else scroll_amount)
        await page.evaluate(f"window.scrollBy(0, {scroll_direction})")
        message = f"Scrolled {direction} in Window"
    ############################## Scroll in an element inthe Main window
    else:
        
        ####################### Get the BBOX of the Item
        try:
            bbox_id = int(target) # To convert from str to int
            bbox = state["bboxes"][bbox_id]
            x, y = bbox["x"], bbox["y"]
            scroll_amount = 200
            scroll_direction = (-scroll_amount if direction.lower() == "up" else scroll_amount)
            await page.mouse.move(x, y)
            await page.mouse.wheel(0, scroll_direction)
            message = f"Scrolled {direction} in element {bbox_id}"
            
        except Exception:
            message = "Error: no bbox for : {bbox_id} or Bad Arguments"
        
    
    print(Style.BRIGHT+message)
    Tool_Message = ToolMessage(content=message,name=action, tool_call_id=str(uuid.uuid4()))
    return {"messages": Tool_Message}

async def Wait_function(state:State,sleep_time = 5):
    page = state["page"]
    ###################### Get the Id of the Item
    args   = state["args"]
    action = state["action"]
    print(Style.BRIGHT+Fore.YELLOW+f"Action : {action} , Args : {args}")
    await asyncio.sleep(sleep_time)
    message = f"Waited for {sleep_time}s."
    print(Style.BRIGHT+message)
    Tool_Message = ToolMessage(content=message,name=action, tool_call_id=str(uuid.uuid4()))
    return {"messages": Tool_Message}

async def Go_back_function(state:State):
    page   = state["page"]
    ###################### Get the Id of the Item
    args   = state["args"]
    action = state["action"]
    print(Style.BRIGHT+Fore.YELLOW+f"Action : {action} , Args : {args}")
    
    await page.go_back()
    message = f"Navigated back a page to {page.url}."
    print(Style.BRIGHT+message)
    Tool_Message = ToolMessage(content=message,name=action, tool_call_id=str(uuid.uuid4()))
    return {"messages": Tool_Message}
  
  
from langchain_core.runnables import chain as chain_decorator

@chain_decorator
async def mark_page(page):
        
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
    
    await page.evaluate(mark_page_script)
    for _ in range(10):
        try:
            bboxes = await page.evaluate("markPage()")
            break
        except Exception:
            # May be loading...
            asyncio.sleep(3)
    screenshot = await page.screenshot()
    # Ensure the bboxes don't follow us around
    await page.evaluate("unmarkPage()")
    return {
        "Image_url": Save_To_HuggingFace(screenshot), #str
        "bboxes": bboxes, # List[Dict]
    }


async def Annotate_function(state:State):
    marked_page = await mark_page.with_retry().ainvoke(state["page"])
    print(Style.BRIGHT+"Image Annotated...")
    return {
        "Image_url": marked_page["Image_url"], #str
        "bboxes": marked_page["bboxes"], # List[Dict]
    }


def Condition_function1(state:State):
    print(Style.BRIGHT+Fore.CYAN+"Condition 1 ...")
    Leader_response = state["Best_Action"]
    if "FINISH" in Leader_response.upper():
        return "END"
    return "CONTINUE"

def Condition_function2(state:State):
    print(Style.BRIGHT+Fore.CYAN+"Condition 2...")
    action = state["action"]
    if "click" in action.lower():
        return "click"
    elif "type" in action.lower():
        return "type"
    elif "scroll" in action.lower():
        return "scroll"
    elif "wait" in action.lower():
        return "wait"
    elif "go_back" in action.lower():
        return "go_back"
    else:
        return "navigator"
    
    
def Visualize(Graph):
    image_data = Graph.get_graph(xray=True).draw_png()
    image_buffer = io.BytesIO(image_data)
    img = Image.open(image_buffer)
    plt.imshow(img)
    plt.axis('off')  # Hide the axis
    plt.show()











