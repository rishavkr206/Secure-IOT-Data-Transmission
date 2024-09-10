import adafruit_dht
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
import socketio
from Crypto.Cipher import AES
import base64
import json
import board

DHT_SENSOR = adafruit_dht.DHT11(board.D4)
POWER_PIN = 12
RAIN_SENSOR_PIN = 7

GPIO.setmode(GPIO.BCM)
GPIO.setup(POWER_PIN, GPIO.OUT)  # Ensure POWER_PIN is set up as output
GPIO.setup(RAIN_SENSOR_PIN, GPIO.IN)

key = b'This is a key123'
iv = b'This is an IV456'

def pad(data):
    return data + (16 - len(data) % 16) * chr(16 - len(data) % 16)

def encrypt(data):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(cipher.encrypt(pad(data).encode()))

def read_sensor():
    try:
        humidity, temperature = DHT_SENSOR.humidity, DHT_SENSOR.temperature
    except RuntimeError as error:
        print(f"Error reading DHT11 sensor: {error}")
        return None

    GPIO.output(POWER_PIN, GPIO.HIGH)
    time.sleep(0.01)  # Brief delay to ensure sensor powers up
    rain_detected = GPIO.input(RAIN_SENSOR_PIN)
    rain_status = "No" if rain_detected else "Yes"
    GPIO.output(POWER_PIN, GPIO.LOW)

    if humidity is not None and temperature is not None:
        return {
            "temperature": temperature,
            "humidity": humidity,
            "rain": rain_status
        }
    return None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

def send_mqtt_data(client, data):
    encrypted_data = {
        'temperature': encrypt(str(data['temperature'])).decode('utf-8'),
        'humidity': encrypt(str(data['humidity'])).decode('utf-8'),
        'rain': encrypt(data['rain']).decode('utf-8')
    }
    client.publish("weather/data", json.dumps(encrypted_data))
    print("Data sent to MQTT broker")

def send_socket_data(sio, data):
    encrypted_data = {
        'temperature': encrypt(str(data['temperature'])).decode('utf-8'),
        'humidity': encrypt(str(data['humidity'])).decode('utf-8'),
        'rain': encrypt(data['rain']).decode('utf-8')
    }
    sio.emit('weather_data', encrypted_data)
    print("Data sent via socket")

mqtt_broker = "localhost"
client = mqtt.Client()
client.on_connect = on_connect
client.connect(mqtt_broker, 1883, 60)
client.loop_start()

sio = socketio.Client()
sio.connect('http://localhost:5000')

try:
    while True:
        data = read_sensor()
        if data:
            print(f"Temperature: {data['temperature']}C, Humidity: {data['humidity']}%, Rain: {data['rain']}")
            send_mqtt_data(client, data)
            send_socket_data(sio, data)
        time.sleep(5)
except KeyboardInterrupt:
    GPIO.cleanup()
