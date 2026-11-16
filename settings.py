"""Configuración compartida de la Práctica 5."""

BROKER_HOST = "localhost"
BROKER_PORT = 1883
KEEPALIVE = 60

TOPIC_TEMP = "/iot/temp"
TOPIC_FAN_CMD = "/iot/fan/cmd"
TOPIC_FAN_STATUS = "/iot/fan/status"

# Raspberry Pi 3B+: GPIO17 (BCM), pin físico 11.
GPIO_PIN = 17

# LM75B: bus I2C 1 y dirección habitual 0x48.
I2C_BUS = 1
LM75B_ADDRESS = 0x48
LM75B_TEMP_REGISTER = 0x00

WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
