# Virtual Try-On Chatbot with WhatsApp Integration:

This project demonstrates a virtual try-on chatbot built with Flask, Twilio, and the Nymbo Virtual Try-On API. Users can send images of themselves and garments via WhatsApp, and the chatbot will return the try-on result as an image.

# Features
Chatbot that interacts via WhatsApp
Virtual try-on functionality using the Nymbo Virtual Try-On API
Image processing and response sending via Twilio API
Dynamic image hosting with Flask for easy access to processed results
# Requirements
To run this project, you need to install the following dependencies:
Python 
Flask
Twilio
Requests
Gradio Client


# You can install the dependencies by running:
pip install -r requirements.txt

# Installation:

# Install the required Python packages:
pip install -r requirements.txt
Set up your Twilio account:

# Sign up at Twilio.
Get your Twilio Account SID, Auth Token, and WhatsApp number from the Twilio Console.

TWILIO_ACCOUNT_SID = '<TWILIO_ACCOUNT_SID>'
TWILIO_AUTH_TOKEN = '<TWILIO_AUTH_TOKEN>'
WHATSAPP_NUMBER = 'whatsapp:<WHATSAPP_NUMBER>'

Update the Flask app to serve images publicly
# Use ngrok to create a secure tunnel to your local Flask app.
Replace <Public_ngrok_url>  with the public URL from ngrok.
Run the Flask app from local.

# Use ngrok to expose the Flask server:
ngrok http 5000

# Set up Twilio webhook:
Go to the Twilio Console and configure the webhook for incoming WhatsApp messages.
Use the ngrok URL followed by /whatsapp as the webhook URL. Example: https://<ngrok-url>/whatsapp.

## Usage:
Send an image of yourself to the WhatsApp number you configured.
The chatbot will ask you to upload a garment image.
After sending the garment image, the chatbot will process the images and return the try-on result.
