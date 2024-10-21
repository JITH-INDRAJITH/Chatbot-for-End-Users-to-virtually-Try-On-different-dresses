from flask import Flask, request, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
from gradio_client import Client, handle_file
import requests
from urllib.parse import urlparse
from requests.auth import HTTPBasicAuth
import os
from twilio.rest import Client as TwilioClient
import time

app = Flask(__name__)
# Hugging Face client
hf_client = Client("Nymbo/Virtual-Try-On")

# Initialize dictionaries to store images and user actions
images = {}
user_last_action = {}

# Twilio account credentials(Update your credentials)
TWILIO_ACCOUNT_SID = '<TWILIO_ACCOUNT_SID>'
TWILIO_AUTH_TOKEN = '<TWILIO_AUTH_TOKEN>'
WHATSAPP_NUMBER = 'whatsapp:<WHATSAPP_NUMBER>'

# Output directory for processed images
OUTPUT_DIR = 'C:/Users/HP/Desktop/chatbot/output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Route to serve images
@app.route('/output/<filename>', methods=['GET'])
def serve_image(filename):
    return send_from_directory(OUTPUT_DIR, filename)

# Home route
@app.route('/')
def home():
    return "Welcome to the Virtual Try-On Chatbot!"

# Endpoint for Twilio webhook
@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip().lower()
    media_url = request.values.get('MediaUrl0', None)
    from_number = request.values.get('From', '').split(':')[1]

    if media_url:
        if from_number not in images:
            images[from_number] = {}

        last_action = user_last_action.get(from_number)

        if last_action != 'person':
            images[from_number]['person'] = download_image(media_url, f"person_{from_number}.jpg")
            user_last_action[from_number] = 'person'
            response_msg = "Image saved as Person. Now send me the garment (type 'G')."
            return send_whatsapp_message(response_msg, from_number)

        elif last_action == 'person':
            images[from_number]['garment'] = download_image(media_url, f"garment_{from_number}.jpg")
            user_last_action[from_number] = 'garment'
            response_msg = "Processing your request... Please wait."
            result_image_filename = process_images(images[from_number]['person'], images[from_number]['garment'])
            del images[from_number]
            del user_last_action[from_number]
            send_image_via_whatsapp(result_image_filename, from_number)
            return send_whatsapp_message("Your virtual try-on result has been sent!", from_number)

    if incoming_msg in ['p', 'g']:
        if incoming_msg == 'p' and 'person' in images.get(from_number, {}):
            return send_whatsapp_message("Person image already uploaded. Please upload the garment.", from_number)
        elif incoming_msg == 'g' and 'garment' in images.get(from_number, {}):
            return send_whatsapp_message("Garment image already uploaded. Please process your images.", from_number)
        else:
            return send_whatsapp_message("Please upload an image and specify 'P' for Person or 'G' for Garment.", from_number)

    return send_whatsapp_message("Please upload an image and specify 'P' for Person or 'G' for Garment.", from_number)

def process_images(person_image_path, garment_image_path):
    try:
        result = hf_client.predict(
            dict={
                "background": handle_file(person_image_path),
                "layers": [],
                "composite": None
            },
            garm_img=handle_file(garment_image_path),
            garment_des="Virtual Try-On Request",
            is_checked=True,
            is_checked_crop=False,
            denoise_steps=30,
            seed=42,
            api_name="/tryon"
        )

        if result and len(result) > 0:
            result_image_temp_path = result[0]
            output_image_path = os.path.join(OUTPUT_DIR, f"virtual_try_on_result_{time.time()}.png")
            os.rename(result_image_temp_path, output_image_path)
            return os.path.basename(output_image_path)
        else:
            return "Failed to process the images. Please try again."
    except Exception as e:
        print(f"Error during image processing: {e}")
        return "An error occurred while processing your images."

def download_image(url, file_name):
    parsed_url = urlparse(url)
    if not all([parsed_url.scheme, parsed_url.netloc]):
        raise Exception("Invalid image URL.")

    try:
        response = requests.get(url, auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        if response.status_code == 200:
            with open(file_name, 'wb') as f:
                f.write(response.content)
            return file_name
        else:
            raise Exception("Failed to download image: " + response.reason)
    except Exception as e:
        print(f"Error downloading image: {e}")
        raise

def send_image_via_whatsapp(image_filename, to_number):
    try:
        twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        flask_image_url = f'<Your-Public_ngrok_url>/output/{image_filename}'  #Update with your ngrok URL

        message = twilio_client.messages.create(
            from_=WHATSAPP_NUMBER,
            to=f'whatsapp:{to_number}',
            media_url=[flask_image_url],
            body="Here is your virtual try-on result!"
        )
        print(f"Image sent successfully with SID: {message.sid}")
    except Exception as e:
        print(f"Error sending image via WhatsApp: {e}")

def send_whatsapp_message(message, to_number):
    resp = MessagingResponse()
    resp.message(message)
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
