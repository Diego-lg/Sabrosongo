from flask import Flask, send_file, jsonify, request

import json, requests, io, base64
from PIL import Image, PngImagePlugin
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
images = []
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE, PUT')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response

def generate_images():
    data = request.json  # Get JSON data from the POST request
    input_value = data.get('input')  # Extract the input value
    print("PROMPT: "+input_value)
    print("Generating images...")
    url = "http://127.0.0.1:7860"

    payload = {
        "prompt": input_value +", detailed, 8k uhd, high quality, octane render, ((masterpiece, best quality)), <lora:add_detail:1.5> ",
        "negative_prompt": "easy negative",
        "steps": 20,
        "width": 512,
        "height": 512,
        "sampler_index": "Euler a",
        "cfg_scale": 7
    }
    option_payload = {
        "sd_model_checkpoint": "dreamshaper_5BakedVae.safetensors"
    }
    response = requests.post(url=f'{url}/sdapi/v1/options', json=option_payload)
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

    r = response.json()
    if 'images' in r:
        for i in r['images']:
            image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))

            png_payload = {
                "image": "data:image/png;base64," + i
            }
            response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", response2.json().get("info"))
            image.save('creations/output.png', pnginfo=pnginfo)

            images.append(image)  # Append the processed image to the images list
    else:
        print("'images' key not found in the dictionary.")
        print(r)
    print("Images generated.")
    return send_file('creations/output.png', mimetype='image/png')  # Return the complete list of images after processing all of them

@app.route('/generate', methods=['POST'])
def imgProcess():
    generate_images()  # Move this line inside the route
    image_path = 'creations/output.png'
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
    img_io = io.BytesIO(image_data)
    print(image_path)

    return send_file(image_path)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)


