## Practica 5 Laboratorio de Fundamentos de Sistemas Embebidos

### Objetivo

Integrar una aplicación IoT utilizando una Raspberry Pi como plataforma embebida. Mediante la comunicación entre diferentes componentes de software atravez del protocolo MQTT.

El sistema deberá adquirir una medición de temperatura, publicarla mediante MQTT y permitir el monitoreo y control de un actuador mediante una interfaz web.

### Material utilizado

- Raspberry Pi 3B+ proporcionada por el profesor.

- LM75B

- L293D

- Motor DC

- Led Resistencias

- Fuente de poder 5V

### Arquitectura del sistema

Compuesto por los siguientes elementos y sus respectivas funciones:

1. **Publicador de temperatura:** Adquirir y publicar las mediciones del sensor.

2. **Controlador del actuador:** Modificar el estado de la salida en base a los comandos MQTT recibidos.

3. **Interfaz WEB:** Muestra la temperatura y permite enviar comandos de encendido/apagado 

## Desarrollo

#### 1 - Preparar el entorno y realizar una prueba

Se instalan las librerías necesarias y se habilita el servicio

```bash
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto
sudo systemctl status mosquitto
```

el servicio se encuentra funcionando

```shellsession
alumno@raspberrypi:~/p05 $ sudo systemctl status mosquitto
● mosquitto.service - Mosquitto MQTT Broker
     Loaded: loaded (/lib/systemd/system/mosquitto.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-11-09 12:54:36 CST; 1 week 0 days ago
       Docs: man:mosquitto.conf(5)

```

Procedemos a realizar una prueba

en una terminal

```shellsession
alumno@raspberrypi:~/p05 $ mosquitto_sub -h localhost -t /iot/temp
20.7
1500.4
```

En otra terminal

```shellsession
alumno@raspberrypi:~ $ mosquitto_pub -h localhost -t /iot/temp -m "20.7"
alumno@raspberrypi:~ $ mosquitto_pub -h localhost -t /iot/temp -m "1500.4"
```

Se observa que efectivamente se comunican atravez de MQTT

### Publicador de temperaruta

Primero leemos la temperatura del LM75B y la publicamos en el topico **/iot/temp**

```python
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

```


