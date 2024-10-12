from colorama import Style,init
from huggingface_hub import HfApi, HfFolder
import os
from dotenv import load_dotenv
import ast
import json
import asyncio


load_dotenv()
init(autoreset=True)


HfFolder.save_token(os.getenv("HUG_TOKEN_KEY"))
api = HfApi()
repo_name = "Noureddinesa/Images"

def Save_To_HuggingFace(image_bytes):
    api.upload_file(
            path_or_fileobj=image_bytes,
            path_in_repo="Screenshot.jpeg",
            repo_id=repo_name
        )
    print(Style.BRIGHT+"Image uploaded")
    image_url = f"https://huggingface.co/{repo_name}/resolve/main/Screenshot.jpeg"
    return image_url


def Parse_dict_string(dict_string):
    try:
        # First try using ast.literal_eval
        parsed_dict = ast.literal_eval(dict_string)
        if isinstance(parsed_dict, dict):
            return parsed_dict
        else:
            raise ValueError("The string does not contain a valid dictionary")
    except (ValueError, SyntaxError):
        try:
            # If ast.literal_eval fails, try json.loads
            parsed_dict = json.loads(dict_string)
            if isinstance(parsed_dict, dict):
                return parsed_dict
            else:
                raise ValueError("The string does not contain a valid dictionary")
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error parsing dictionary string: {e}")
            return None


def format_descriptions(bboxes):
    labels = []
    for i, bbox in enumerate(bboxes):
        text = bbox.get("ariaLabel") or ""
        if not text.strip():
            text = bbox["text"]
        el_type = bbox.get("type")
        labels.append(f'{i} (<{el_type}/>): "{text}"')
    output = "\nValid Bounding Boxes:\n" + "\n".join(labels)
    return output

async def Annotate(page):

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
            await asyncio.sleep(3)
    screenshot = await page.screenshot(quality=100, type="jpeg",full_page=False)
    #print(page.url)
    await page.evaluate("unmarkPage()")
    print(Style.BRIGHT+"Image annotated")
    return {
        "Image_url": Save_To_HuggingFace(screenshot), #str
        "bboxes": bboxes, # List[Dict]
    }

def string_to_list(input_string):
    # Remove the square brackets and split by commas, stripping any extra spaces
    return [item.strip() for item in input_string.strip("[]").split(",")]





