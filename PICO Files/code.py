import os
import board
import busio
import neopixel
import time
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer
import adafruit_pixie
import ipaddress
import mdns
import wifi
import socketpool
from adafruit_httpserver import Server, Request, Response, POST, MIMETypes,FileResponse

neoPixels = False

def pixelDemo():
    while(True):
        print("tick")
        pixels[0] = (0, 255, 0)
        pixels.show()
        time.sleep(0.5)
        pixels[0] = (255, 0, 0)
        pixels.show()
        time.sleep(0.5)
        pixels[0] = (0, 0, 255)
        pixels.show()
        time.sleep(0.5)
        pixels[0] = (255, 255, 255)
        pixels.show()
        time.sleep(0.5)

red=0
blue=0
green=0
master=0
lastColourTickTime = 0
tickIntervalSecs = 1;

def updateColour():
    global red,green,blue,master
    print(red,green,blue,master)
    pixels.fill((int(red),int(green),int(blue)))
    pixels.brightness = int(master)/100
    pixels.show()
   

def colourTick():
    global lastColourTickTime,tickIntervalSecs
    currentTime = time.monotonic()
    interval = currentTime - lastColourTickTime
    if interval > tickIntervalSecs:
        lastColourTickTime = currentTime
        print("tick")
        updateColour()
    
def setColour(r,g,b, m=10):
    global red,green,blue,master
    red=r
    blue=b
    green=g
    master=m
    updateColour()
    
if neoPixels:
    pixelLength = 5
    pixels = neopixel.NeoPixel(board.GP4,pixelLength,auto_write=False)
else:
    uart = busio.UART(tx=board.GP4, rx=board.GP5,baudrate=115200)
    numPixies =1
    pixels = adafruit_pixie.Pixie(uart, numPixies, brightness=0.1  )

setColour(255,0,0,10)

MIMETypes.configure(
    default_to="text/plain",
    # Unregistering unnecessary MIME types can save memory
    keep_for=[".html", ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".ico"],
    # If you need to, you can add additional MIME types
    register={".foo": "text/foo", ".bar": "text/bar"},
)

print()
print("Connecting to WiFi")

#  connect to your SSID
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

print("Connected to WiFi")
setColour(0,255,0,10)

mdns_server = mdns.Server(wifi.radio)
mdns_server.hostname = "flashlight"

pool = socketpool.SocketPool(wifi.radio)

#  prints MAC address to REPL
print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])

#  prints IP address to REPL
print("My IP address is", wifi.radio.ipv4_address)

#  pings Google
ipv4 = ipaddress.ip_address("8.8.4.4")
print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4)*1000))

server = Server(pool, "/site", debug=True)

@server.route("/")
def base(request: Request):  # pylint: disable=unused-argument
    return FileResponse(request, "index.html", "/site")

@server.route("/lights")
def base(request: Request):  # pylint: disable=unused-argument
    red = request.query_params.get("red") or 0
    green = request.query_params.get("green") or 0
    blue = request.query_params.get("blue") or 0
    master = request.query_params.get("master") or 10
    setColour(red,green,blue,master)
    return Response(request, "lights", content_type='text/html')

print("starting server..")

# startup the server
try:
    server.start(str(wifi.radio.ipv4_address))
    print("Listening on http://%s:80" % wifi.radio.ipv4_address)
#  if the server fails to begin, restart the pico w
except OSError:
    time.sleep(5)
    print("restarting..")
    microcontroller.reset()
ping_address = ipaddress.ip_address("8.8.4.4")

setColour(255,255,255,10)

while True:
    try:
        server.poll()
    except Exception as e:
        print(e)
        continue
    colourTick()


