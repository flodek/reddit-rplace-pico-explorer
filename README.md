# Reddit r/Place canvas pico explorer
A small display that shows a piece of [Reddit's r/place](https://www.reddit.com/r/place/) canvas and allows you to navigate through it.

![Demo](https://raw.githubusercontent.com/flodek/reddit-rplace-pico-explorer/main/explorer.png)

## Hardware
 - Raspberry Pi Pico W
 - Pico Display Pack 2.0

## How to Cook
### Server Side
RP Pico doesn't have enough memory to store the entire canvas. This is why the solution is divided into two parts: the server and the client sides. The server part can be hosted on a Raspberry Pi Zero W using Flask framework:
```python
@app.route('/png', methods=['GET'])
def png():
    x = request.args.get('x', default = 0, type = int)
    y = request.args.get('y', default = 0, type = int)

    img = Image.open('final_2023_place_2x.png', mode='r')
    crp_img = img.crop((x, y, x+320, y+240))

    img_byte_arr = io.BytesIO()
    crp_img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    img.close()

    return send_file(
        img_byte_arr,
        attachment_filename='crop.png',
        mimetype='image/png'
    )
```

### Client Side
Amend ```main.py``` with your WiFi SSID and password, update the server-side URL and save the file on the Pico.

## Demo
https://github.com/flodek/reddit-rplace-pico-explorer/assets/39746698/d9ff9887-8bdf-4062-b3b8-a878b91a77a1
