from langgraph.graph import END, StateGraph, START
from The_State import State
from  Functions import Leader_function,Extractor_function,Navigator_function,Condition_function1,Visualize
from Functions import Click_function,Type_function,Scroll_function,Wait_function,Go_back_function,Annotate_function,Condition_function2

graph_builder = StateGraph(State)
graph_builder.add_node("Leader",Leader_function)
graph_builder.add_node("Extractor",Extractor_function)
graph_builder.add_node("Navigator",Navigator_function)
graph_builder.add_node("Click",Click_function)
graph_builder.add_node("Type",Type_function)
graph_builder.add_node("Scroll",Scroll_function)
graph_builder.add_node("Wait",Wait_function)
graph_builder.add_node("Go_back",Go_back_function)
graph_builder.add_node("Annotate",Annotate_function)


graph_builder.add_edge(START,"Leader")
graph_builder.add_conditional_edges("Navigator",Condition_function2,{"click":"Click","type":"Type","scroll":"Scroll","wait":"Wait","go_back":"Go_back","navigator":"Navigator"})
graph_builder.add_edge("Click","Annotate")
graph_builder.add_edge("Type","Annotate")
graph_builder.add_edge("Scroll","Annotate")
graph_builder.add_edge("Wait","Annotate")
graph_builder.add_edge("Go_back","Annotate")
graph_builder.add_edge("Annotate","Extractor")
graph_builder.add_edge("Extractor","Leader")
graph_builder.add_conditional_edges("Leader",Condition_function1,{"END":"__end__","CONTINUE":"Navigator"})

Graph = graph_builder.compile()



#Visualize(Graph)

async def Run(Start_Input):
    event_stream = Graph.astream(Start_Input,{"recursion_limit": 100,},)
    async for event in event_stream:
        pass








