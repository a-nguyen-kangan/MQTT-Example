# main.py -- put your code here!
from machine import Pin
# from time import sleep
import socket
import urequests
from umqtt.simple import MQTTClient
import time
import machine
import ssl
from time import sleep

led = Pin(2, Pin.OUT)

db_url = 'https://xmutyxjqddxwqqacfxwt.supabase.co/rest/v1/LedInfo'
apikey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtdXR5eGpxZGR4d3FxYWNmeHd0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDEwNDI3MDUsImV4cCI6MjAxNjYxODcwNX0.p2Rk9nFxWAtwVPSOL7VKnq6T0JnJzcoazPBJU3frRvU'

def handle_interrupt_on(pin):
  print("handle_interrupt on", led.value())
  

def handle_interrupt_off(pin):
  print("handle_interrupt off", led.value())

led.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt_on) 

def sub_cb(topic, msg):
  print((topic, msg))
  if msg == b'on':
    print('on')
    led.value(1)
    led.irq(trigger=Pin.IRQ_FALLING, handler=handle_interrupt_off)
    urequests.post(db_url, json={"state": False}, headers={"apikey": apikey})
  elif msg == b'off':
    print('off')
    led.value(0)
    led.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt_on)
    urequests.post(db_url, json={"state": True}, headers={"apikey": apikey})


def connect_and_subscribe():
  global mqtt_server, topic_sub, client_id, mqtt_port, cacert
  print(mqtt_server)
  print(client_id)
  # sslparams = {'server_side': False,
  #            'key': None,
  #            'cert': None,
  #            'cert_reqs': ssl.CERT_REQUIRED,
  #            'cadata': cacert,
  #            'server_hostname': mqtt_server}
  context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
  context.verify_mode = ssl.CERT_NONE
  MQTT_PORT     = 8883
  MQTT_SSL      = context
  try:
    client = MQTTClient(client_id=client_id, 
                      server=mqtt_server, 
                      port=MQTT_PORT, 
                      user='anguyen', 
                      password='Abcd1234', 
                      keepalive=3600, 
                      ssl=MQTT_SSL)
  #   client = MQTTClient(client_id=client_id,
  #       server=mqtt_server,
  #       port=0,
  #       user=b"anguyen",
  #       password=b"Abcd1234",
  #       keepalive=7200,
  #       ssl=True,
  #       ssl_params={'server_hostname':'fe6076df55bd4037a34ea51f278949bf.s1.eu.hivemq.cloud'}
  # )
    client.connect()
    client.set_callback(sub_cb)
    client.subscribe(topic_sub)
    print("Connected to %s, subscribed to %s topic" % (mqtt_server, topic_sub))
    return client
  except Exception as e:
    print ("Error:-> %s" % e)
    machine.reset()


def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  connect_and_subscribe()


# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind(('', 80))
# s.listen(5)


# response = urequests.get('http://jsonplaceholder.typicode.com/albums/1')
# text = response.text
# parsed = response.json()
# print(parsed['id'])
# print(parsed['title'])
# print(parsed['userId'])
# print("Fucken Hell")

try:
  client = connect_and_subscribe()
except:
  machine.reset()

while True:
  last_message = 0
  message_interval = 5
  counter = 0
  
  try:
    res = client.check_msg()
    if (time.time() - last_message) > message_interval:
      msg = 'Hello #%d' % counter
  except OSError as e:
    restart_and_reconnect() 
  




 

