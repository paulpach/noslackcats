# NoSlackCats
The NoSlackCats bot is a Python-based Slack bot that identifies cat images shared in a Slack channel using the Clarifai gPRC API.

This Slack Bolt app will handle the `file_shared` and `message` event or parse a message for an image URL. 
## Requirements
- Python 3.6 or later
- Slack Bolt Framework, API key, Signing secret and OAuth scopes
- Clarifai API key and permissions

### Required Slack Bot Token Scopes
- chat.write
- channels.read
- im.history
- files.read
- (others)

## Installation
1. Clone the repository to your local machine.
1. Install the required dependencies using pip install -r requirements.txt.
1. Set up your Slack app and obtain your Slack API key and OAuth scopes.
1. Set up your Clarifai account and obtain your Clarifai API key and permissions.
2. Set your API keys and tokens in a .env file.
3. Run the bot using the command python app.py.

## Usage
- NoSlackCats will automatically listen for files shared in the Slack channel where it has been installed. 
- If an image is detected, the bot will reply to the message with a message indicating that the image is a cat.
- We could obviously do more here - preferably deleting the image - but this is a proof of concept... :wink:

## Contributing
Contributions to the NoSlackCat bot are welcome! To contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes and test them locally.
4. Create a pull request on the main repository.

License
The NoSlackCat bot is released under the Apache 2.0 License. See the [LICENSE](./LICENSE) file for more information.