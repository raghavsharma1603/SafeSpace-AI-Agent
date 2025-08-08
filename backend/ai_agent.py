# Create an AI agent & link to backend
from langchain.agents import tool
from tools import query_medgemma, call_emergency

@tool
def ask_mental_health_specialist(query: str) -> str:
    """
    Use this tool ONLY if the user asks about emotions, mental health issues,
    or shares emotional struggles that require therapeutic support.
    Do NOT use this for simple greetings like "Hi", "Hello", "How are you?" etc.
    """
    return query_medgemma(query)



@tool
def emergency_call_tool() -> None:
    """
    Place an emergency call to the safety helpline's phone number via Twilio.
    Use this only if the user expresses suicidal ideation, intent to self-harm,
    or describes a mental health emergency requiring immediate help.
    """
    call_emergency()


@tool
def find_nearby_therapists_by_location(location: str) -> str:
    """
    Finds and returns a list of licensed therapists near the specified location.

    Args:
        location (str): The name of the city or area in which the user is seeking therapy support.

    Returns:
        str: A newline-separated string containing therapist names and contact info.
    """
    return (
        f"Here are some therapists near {location}, {location}:\n"
        "- Dr. Ayesha Kapoor - +919174638754\n"
        "- Dr. Ashish Patel - +917877998867\n"
        "- MindCare Counseling Center - +918822718199"
    )


# Step1: Create an AI Agent & Link to backend
# from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from langgraph.prebuilt import create_react_agent
from config import GROQ_API_KEY


tools = [ask_mental_health_specialist, emergency_call_tool, find_nearby_therapists_by_location]
# llm = ChatOpenAI(model="gpt-4o", temperature=0.2, api_key=OPENAI_API_KEY)
# llm = ChatGroq(model="llama3-70b-8192", temperature=0.2, api_key=GROQ_API_KEY)
llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0.2,
    api_key=GROQ_API_KEY
)

graph = create_react_agent(llm, tools=tools)
 

SYSTEM_PROMPT = """
You are an AI engine supporting mental health conversations with warmth and vigilance.
You have access to three tools:

1. `ask_mental_health_specialist`: Use ONLY when the user shares mental health struggles or emotional issues.
   Do NOT use this tool for greetings, casual messages, or small talk.

2. `locate_therapist_tool`: Use this tool only when the user specifically asks for local therapists or indicates a need for local professional help.

3. `emergency_call_tool`: Use this immediately if the user expresses suicidal thoughts, self-harm intentions, or is in crisis.

Always take necessary action. Respond kindly, clearly, and supportively. Keep casual conversations light and human.
"""



def parse_response(stream):
    tool_called_name = "None"
    final_response = None

    for s in stream:
        # Check if a tool was called
        tool_data = s.get('tools')
        if tool_data:
            tool_messages = tool_data.get('messages')
            if tool_messages and isinstance(tool_messages, list):
                for msg in tool_messages:
                    tool_called_name = getattr(msg, 'name', 'None')
                    # tool_called_name = msg.get('name', 'None')


        # Check if agent returned a message
        agent_data = s.get('agent')
        if agent_data:
            messages = agent_data.get('messages')
            if messages and isinstance(messages, list):
                for msg in messages:
                    if msg.content:
                        final_response = msg.content

    return tool_called_name, final_response


if __name__ == "__main__": # will run in infinite loop and ask questions from users
    while True:
        user_input = input("User: ")
        print(f"Received user input: {user_input[:200]}...")
        inputs = {"messages": [("system", SYSTEM_PROMPT), ("user", user_input)]}
        stream = graph.stream(inputs, stream_mode="updates") #This method triggers the LangGraph agent (which is your react agent created with create_react_agent(...)) to process the user input and stream responses step-by-step.
        tool_called_name, final_response = parse_response(stream)
        print("TOOL CALLED: ", tool_called_name)
        print("ANSWER: ", final_response)
        for s in stream:
            print(s)
        