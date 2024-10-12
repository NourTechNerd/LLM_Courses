from langchain_core.tools import StructuredTool
from langchain.pydantic_v1 import BaseModel, Field

################################ OpenWeather ##############################################
###########################################################################################
import os
from langchain_community.utilities import OpenWeatherMapAPIWrapper

os.environ["OPENWEATHERMAP_API_KEY"] = "173302c5b0b96d80bcb52bc315943bb9"
weather = OpenWeatherMapAPIWrapper()

# With this class I define my parametres of the tool and I give description that
#--> Will help the LLM to understand the  tool schema.
class OpenWeather_Arg(BaseModel):
    Location: str = Field(...,description="The Location is often a city name like London, Casablanca ...")

def run(Location:str) -> str:
    weather_data = weather.run(Location)
    return weather_data


OpenWeather = StructuredTool.from_function(
    func=run,
    name="OpenWeather",
    description="Give the Weather information for a specific Location",
    args_schema=OpenWeather_Arg,
    return_direct=False,
)

####################################### Tavily ############################################
###########################################################################################
from langchain_community.tools.tavily_search import TavilySearchResults
import os

os.environ["TAVILY_API_KEY"] = "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"
Tavily = TavilySearchResults(max_results=2,name="Tavily")

####################################### AskNewsSearch ############################################
###########################################################################################

from langchain_community.tools.asknews import AskNewsSearch


os.environ["ASKNEWS_CLIENT_ID"] = "b4753573-7c63-4a42-be1e-27e6a4986db9"
os.environ["ASKNEWS_CLIENT_SECRET"] = "PlWZYQ7c1LX2At7NBKbrCcHV2l"

AskNews = AskNewsSearch(max_results=2)























