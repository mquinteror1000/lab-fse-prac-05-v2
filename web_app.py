"""Interfaz web de monitoreo y control mediante MQTT."""
from threading import Lock

import paho.mqtt.client as mqtt
from flask import Flask, jsonify, render_template, request

from settings import (
    BROKER_HOST,
    BROKER_PORT,
    KEEPALIVE,
    TOPIC_FAN_CMD,
    TOPIC_FAN_STATUS,
    TOPIC_TEMP,
    WEB_HOST,
    WEB_PORT,
)

app = Flask(__name__)
lock = Lock()
state = {
    "temperature": None,
    "fan_status": None,
    "mqtt_connected": False,
}

client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="fse-p05-web-interface",
)


def on_connect(mqtt_client, userdata, flags, reason_code, properties):
    with lock:
        state["mqtt_connected"] = not reason_code.is_failure

    if reason_code.is_failure:
        print(f"Error de conexión MQTT: {reason_code}")
        return

    mqtt_client.subscribe([(TOPIC_TEMP, 1), (TOPIC_FAN_STATUS, 1)])
    print("Interfaz conectada al broker MQTT.")


def on_disconnect(mqtt_client, userdata, disconnect_flags, reason_code, properties):
    with lock:
        state["mqtt_connected"] = False


def on_message(mqtt_client, userdata, message):
    payload = message.payload.decode("utf-8").strip()

    with lock:
        if message.topic == TOPIC_TEMP:
            try:
                state["temperature"] = float(payload)
            except ValueError:
                print(f"Temperatura no válida: {payload}")
        elif message.topic == TOPIC_FAN_STATUS:
            if payload.lower() == "true":
                state["fan_status"] = True
            elif payload.lower() == "false":
                state["fan_status"] = False


client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/state")
def get_state():
    with lock:
        return jsonify(state.copy())


@app.post("/api/command")
def send_command():
    data = request.get_json(silent=True) or {}
    value = data.get("value")

    if not isinstance(value, bool):
        return jsonify({"error": "El comando debe ser true o false."}), 400

    if not client.is_connected():
        return jsonify({"error": "No hay conexión con el broker MQTT."}), 503

    command = "true" if value else "false"
    result = client.publish(TOPIC_FAN_CMD, command, qos=1)

    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        return jsonify({"error": "No se pudo publicar el comando."}), 503

    return jsonify({"sent": True, "command": command})


def main():
    client.connect(BROKER_HOST, BROKER_PORT, KEEPALIVE)
    client.loop_start()

    try:
        print(f"Interfaz disponible en http://<IP_RASPBERRY>:{WEB_PORT}")
        app.run(host=WEB_HOST, port=WEB_PORT, debug=False, use_reloader=False)
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
