import chainlit as cl
import openai
import os
import base64

# Open AI
api_key = os.getenv("OPENAI_API_KEY")
endpoint_url = "https://api.openai.com/v1"
# # https://platform.openai.com/docs/models/gpt-4o
model_kwargs = {
    "model": "gpt-4o",
    "temperature": 0.3,
    "max_tokens": 500
}

# Runpod + HF Mistral
# runpod_serverless_id = os.getenv("RUNPOD_SERVERLESS_ID")
# api_key = os.getenv("RUNPOD_API_KEY")
# endpoint_url = f"https://api.runpod.ai/v2/{runpod_serverless_id}/openai/v1"
# model_kwargs = {
#     "model": "mistralai/Mistral-7B-Instruct-v0.3",
#     "temperature": 0.3,
#     "max_tokens": 500
# }

client = openai.AsyncClient(api_key=api_key, base_url=endpoint_url)

# @cl.on_message
# async def on_message(message: cl.Message):
#     # Maintain an array of messages in the user session
#     message_history = cl.user_session.get("message_history", [])

#     # Processing images exclusively
#     images = [file for file in message.elements if "image" in file.mime] if message.elements else []

#     if images:
#         # Read the first image and encode it to base64
#         with open(images[0].path, "rb") as f:
#             base64_image = base64.b64encode(f.read()).decode('utf-8')
#         message_history.append({
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": message.content if message.content else "What’s in this image?"
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": f"data:image/jpeg;base64,{base64_image}"
#                     }
#                 }
#             ]
#         })
#     else:
#         message_history.append({"role": "user", "content": message.content})

#     response_message = cl.Message(content="")
#     await response_message.send()
    
#     # Pass in the full message history for each request
#     stream = await client.chat.completions.create(messages=message_history, 
#                                                   stream=True, **model_kwargs)
#     async for part in stream:
#         if token := part.choices[0].delta.content or "":
#             await response_message.stream_token(token)

#     await response_message.update()

#     # Record the AI's response in the history
#     message_history.append({"role": "assistant", "content": response_message.content})
#     cl.user_session.set("message_history", message_history)

# Pre - Milestone 5
@cl.on_message
async def on_message(message: cl.Message):
    try:
        message_history = cl.user_session.get("message_history", [])
        message_history.append({"role": "user", "content": message.content})
        # Your custom logic goes here...

        stream = await client.chat.completions.create(
            messages=[{"role": "user", "content": message.content}],
            stream=True,
            **model_kwargs
        )

        response_message = cl.Message(content="")
        await response_message.send()

        async for part in stream:
            if token := part.choices[0].delta.content or "":
                await response_message.stream_token(token)

        await response_message.update()

        message_history.append({"role":"assistant", "content": response_message.content})
        cl.user_session.set("message_history", message_history)

    except Exception as e:
        # Log the full error for debugging
        print(f"Error during API call: {e}")
        # Send a user-friendly error message
        await cl.ErrorMessage(content=f"Sorry, an error occurred while processing your request.").send()
