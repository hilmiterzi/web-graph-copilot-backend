from app.domain.main_AI.models import AI_copilot
from app.domain.main_AI.agents.tasksAI import assistant_to_create_branches_or_task_under_node, tools
from openai import OpenAI, AsyncOpenAI
import json
import dotenv
import os


dotenv.load_dotenv()

prompt = """ You and your assistant will help the user to build and expand projects in the fastest and nicest ways
It's really important to correctly pass the right nodeId understand under what node the user wants something to be added to..
  
        
     Chat, brainstorm, help, ask questions to the user to fully understand what they're trying to build and make use of your assistant that will read the whole conversation and add tasks and nodes to the project!
     """

available_functions = {
    "assistant_to_create_branches_or_task_under_node": assistant_to_create_branches_or_task_under_node,
}  # only one function in this example, but you can have multiple


async def ai(ai_payload: AI_copilot, sio, sid):
    client = AsyncOpenAI()
    client.api_key = os.getenv("OPENAI_API_KEY")
    #TODO move tools to

    #gpt - 3.5 - turbo - 1106
    #"gpt-4-0125-preview"

    request_params = {
        'model': ai_payload.selected_model,
        'messages': ai_payload.history,
        'temperature': 0.1
    }

    if not ai_payload.creative_mode:
        request_params['tools'] = tools
        request_params['tool_choice'] = "auto"
    print("Voor response in Main AI")
    print(ai_payload.history)

    response = await client.chat.completions.create(
        **request_params
    )
    print("Na response in Main AI")
    response_message = response.choices[0].message

    tool_calls = response_message.tool_calls
    if tool_calls:

        del response_message.function_call
        # response_message.content = "function calling is active"
        ai_payload.history.append(response_message.dict())    # extend conversation with assistant's reply

        for tool_call in tool_calls:
            function_name = tool_call.function.name

            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            function_args["ai_payload"] = ai_payload
            function_args["sio"] = sio
            function_args["sid"] = sid

            function_response = await function_to_call(
                **function_args
            )
            print(function_response,"printing funcion_response")
            # ai_payload.history[1]["content"] = function_response
            ai_payload.history.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": "The graph is updated, ask the user if they're satisfied..",
                }
            )

        return await ai(ai_payload, sio, sid)
    ai_payload.history.append({"role": "assistant", "content": response_message.content})
    return ai_payload
