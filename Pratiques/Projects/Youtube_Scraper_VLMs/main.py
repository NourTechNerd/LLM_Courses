"""########################## Description 
# The same Objectif of the previous Project but with VLMs instead of LLMs.
# Why because VLMs with Browsing ability can perform better than LLMs With RAG.


from Functions import Visualize
from Graph import Graph
from Tools import Annotate
from test import Page

#Visualize(Graph)

annotate = Annotate(Page)
ImageURL = annotate["img_url"]
BBoxes   = annotate["bboxes"]
Youtube_handle = "@aiadvantage"
User_request = f"Tell me about Youtuber with the Channel handle is {Youtube_handle}"
Start_Input = {"User_request":User_request,"page":Page,"Image_url":ImageURL,"bboxes":BBoxes}

Page.mouse.click(411,272)
Page.keyboard.type("ydcsdcvscvscvy")
print("Clickeddddd")

for event in Graph.stream(Start_Input):
    for value in event.values():
        pass

Graph.astream(Start_Input)
# Close the browser and Playwright after all operations are done
#browser.close()
#playwright.stop()"""

import asyncio
from playwright.async_api import async_playwright
from Tools import Annotate
from Graph import Graph,Run


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=None)
        page = await browser.new_page()
        await page.goto("https://www.google.com")
        await asyncio.sleep(2)
        annotate = await Annotate(page)
        ImageURL = annotate["Image_url"]
        BBoxes   = annotate["bboxes"]
        Youtube_handle = "@aiadvantage"
        User_request = f"Tell me about Youtuber with the Channel handle is {Youtube_handle}"
        Start_Input = {"User_request":User_request,"page":page,"Image_url":ImageURL,"bboxes":BBoxes}
        await Run(Start_Input)
        #print(Start_Input)

        #await browser.close()

# Run the main function using asyncio.run
if __name__ == "__main__":
    asyncio.run(main())
