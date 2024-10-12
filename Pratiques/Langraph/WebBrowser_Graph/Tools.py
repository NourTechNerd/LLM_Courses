from playwright.sync_api import sync_playwright
import time


def Click(page,bbox_id,x,y):
    page.mouse.click(x, y)
    return f"Clicked {bbox_id}"

def Type(page,bbox_id,x,y,text):
    Click(page,bbox_id,x,y)
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    page.keyboard.type(text)
    page.keyboard.press("Enter")
    return f"Typed {text} and submitted"

def Scroll(page,scroll_args,x=0,y=0):
    target, direction = scroll_args
    ############################### Scroll in the main Window
    if target.upper() == "WINDOW":
        scroll_amount = 500
        scroll_direction = (-scroll_amount if direction.lower() == "up" else scroll_amount)
        page.evaluate(f"window.scrollBy(0, {scroll_direction})")
    ############################## Scroll in an element inthe Main window
    else:
        # Scrolling within a specific element
        scroll_amount = 200
        scroll_direction = (-scroll_amount if direction.lower() == "up" else scroll_amount)
        page.mouse.move(x, y)
        page.mouse.wheel(0, scroll_direction)

    return f"Scrolled {direction} in {'window' if target.upper() == 'WINDOW' else 'element'}"


def Wait(sleep_time = 5):
    time.sleep(sleep_time)
    return f"Waited for {sleep_time}s."

def Go_back(page):
    page.go_back()
    return f"Navigated back a page to {page.url}."










