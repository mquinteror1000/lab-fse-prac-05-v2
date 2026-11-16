"""Publica la temperatura del LM75B en /iot/temp cada segundo."""
import time

import paho.mqtt.client as mqtt

from sensor_reader import read_temperature
from settings import BROKER_HOST, BROKER_PORT, KEEPALIVE, TOPIC_TEMP


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Error de conexión MQTT: {reason_code}")
    else:
        print("Publicador conectado al broker MQTT.")


def main():
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="fse-p05-temperature-publisher",
    )
    client.on_connect = on_connect
    client.connect(BROKER_HOST, BROKER_PORT, KEEPALIVE)
    client.loop_start()

    try:
        while True:
            temperature = read_temperature()
            payload = str(round(temperature, 3))
            result = client.publish(TOPIC_TEMP, payload, qos=1)
            result.wait_for_publish()
            print(f"Temperatura: {payload} °C")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nPublicador detenido.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
