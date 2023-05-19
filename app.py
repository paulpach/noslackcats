import os
import re
import requests
import logging
import uvicorn

logging.basicConfig(level=logging.DEBUG)

from fastapi import FastAPI, Request
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2, service_pb2_grpc, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2


app = AsyncApp(
        token=os.environ["SLACK_BOT_TOKEN"],
        signing_secret=os.environ["SLACK_SIGNING_SECRET"]
    )

app_handler = AsyncSlackRequestHandler(app)

api = FastAPI()

@api.post("/slack/events")
async def endpoint(req: Request):
    return await app_handler.handle(req)

@api.get("/")
async def root():
    return {"message": "NoSlackCats is up!"}

async def is_cat(file_bytes):
    # Get the Clarifai API key from the environment variables
    CLARIFAI_API_KEY = os.environ["CLARIFAI_API_KEY"]

    # Set the ID of the Clarifai model to use for cat image recognition
    cat_model_id = "aaa03c23b3724a16a56b629203edc62c"

    # Create the gRPC channel
    stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())

    metadata = (("authorization", f"Key {CLARIFAI_API_KEY}"),)

    request = service_pb2.PostModelOutputsRequest(
        model_id=cat_model_id,
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(image=resources_pb2.Image(base64=file_bytes))
            )
        ],
    )
    response = stub.PostModelOutputs(request, metadata=metadata)

    if response.status.code != status_code_pb2.SUCCESS:
        print(response)
        return False
       # raise Exception(f"Request failed, status code: {response.status}")

    cat_concept = None
    # loop through the concepts from Clarifai response for the one we want
    for concept in response.outputs[0].data.concepts:
        if concept.name.lower() == 'cat':
            cat_concept = concept
            break
    if cat_concept is not None:
        return True
    else:
        return False

@app.event("file_shared")
async def handle_file_shared(event, say):
    file_id = event["file_id"]
    file_info = await app.client.files_info(file=file_id)
    file_url = file_info["file"]["url_private"]
    # Only worry about the file if it's an image
    if is_image_url(file_url):
        file_bytes = await download_file_bytes(file_url)
        if await is_cat(file_bytes):
            await say("Come on. That looks like a :cat:!") 
            # todo: here's where I would delete the cat image... ;) 
        # else:
            # await say("That's not a cat.")

@app.event("message")
async def handle_message(event, say):
    message_text = event["text"]
    # Decided to handle the images shared via url that unfurl 
    url = await extract_url(message_text)
    if url is not None:
        url = url.strip("<>") # Slack image urls had some extra characters we don't need
        if await is_image_url(url):
            file_bytes = await download_file_bytes(url)
            if await is_cat(file_bytes):
                await say("Come on. That looks like a :cat:!")
            # else:
                # await say("That's not a cat.")

async def download_file_bytes(url):
    response = requests.get(url, headers={"Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"})
    response.raise_for_status()
    return response.content

async def extract_url(text):
    url_regex = r"(?P<url>https?://[^\s]+)"
    match = re.search(url_regex, text)
    if match:
        return match.group("url")
    return None

def is_image_url(url):
    response = requests.head(url)
    content_type = response.headers.get("Content-Type")
    if content_type is not None and "image" in content_type:
        return True
    elif url.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        return True
    else:
        return False

if __name__ == "__main__":
    uvicorn.run("app:api", host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))