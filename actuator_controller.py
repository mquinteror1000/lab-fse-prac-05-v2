"""Recibe comandos MQTT y controla el actuador mediante GPIO17."""
import paho.mqtt.client as mqtt
from gpiozero import OutputDevice

from settings import (
    BROKER_HOST,
    BROKER_PORT,
    GPIO_PIN,
    KEEPALIVE,
    TOPIC_FAN_CMD,
    TOPIC_FAN_STATUS,
)

actuator = OutputDevice(GPIO_PIN, active_high=True, initial_value=False)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Error de conexión MQTT: {reason_code}")
        return

    print("Controlador conectado al broker MQTT.")
    client.subscribe(TOPIC_FAN_CMD)
    client.publish(TOPIC_FAN_STATUS, "false", qos=1, retain=True)


def on_message(client, userdata, message):
    command = message.payload.decode("utf-8").strip().lower()

    if command == "true":
        actuator.on()
        status = "true"
        print("Actuador encendido.")
    elif command == "false":
        actuator.off()
        status = "false"
        print("Actuador apagado.")
    else:
        print(f"Comando ignorado: {command}")
        return

    client.publish(TOPIC_FAN_STATUS, status, qos=1, retain=True)


def main():
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="fse-p05-actuator-controller",
    )
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER_HOST, BROKER_PORT, KEEPALIVE)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nControlador detenido.")
    finally:
        actuator.off()
        actuator.close()
        client.disconnect()


if __name__ == "__main__":
    main()
