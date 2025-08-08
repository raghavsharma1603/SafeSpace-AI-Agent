# set up FASTAPI
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn 
from ai_agent import graph,SYSTEM_PROMPT,parse_response

# to connect frontend to backend
app = FastAPI()

# Receive and validate requst from frontend using pydantic
class Query(BaseModel):
    message: str

@app.post("/ask")
async def ask(query: Query):
    # response = ai_agent(query)
    # response= "This is from backend"
    
    inputs = {"messages": [("system", SYSTEM_PROMPT), ("user",query.message)]}
    stream = graph.stream(inputs, stream_mode="updates") #This method triggers the LangGraph agent (which is your react agent created with create_react_agent(...)) to process the user input and stream responses step-by-step.
    tool_called_name, final_response = parse_response(stream)
    # print("TOOL CALLED: ", tool_called_name)
    # print("ANSWER: ", final_response)           
     
# Send response to the front end
    return {"response": final_response,
            "tool_called": tool_called_name}

if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True)