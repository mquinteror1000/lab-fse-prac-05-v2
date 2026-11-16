const temperatureElement = document.getElementById("temperature");
const fanStatusElement = document.getElementById("fan-status");
const connectionElement = document.getElementById("connection");
const messageElement = document.getElementById("message");

async function updateState() {
  try {
    const response = await fetch("/api/state", { cache: "no-store" });
    const data = await response.json();

    connectionElement.textContent = data.mqtt_connected
      ? "Conectado al broker MQTT"
      : "Sin conexión con MQTT";

    temperatureElement.textContent = data.temperature === null
      ? "--"
      : Number(data.temperature).toFixed(2);

    if (data.fan_status === true) {
      fanStatusElement.textContent = "ENCENDIDO";
    } else if (data.fan_status === false) {
      fanStatusElement.textContent = "APAGADO";
    } else {
      fanStatusElement.textContent = "Sin información";
    }
  } catch (error) {
    connectionElement.textContent = "No se pudo consultar el servidor";
  }
}

async function sendCommand(value) {
  messageElement.textContent = "Enviando comando...";

  try {
    const response = await fetch("/api/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ value })
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "No se pudo enviar el comando.");
    }

    messageElement.textContent = "Comando enviado; esperando estado del controlador.";
  } catch (error) {
    messageElement.textContent = error.message;
  }

  updateState();
}

document.getElementById("turn-on").addEventListener("click", () => sendCommand(true));
document.getElementById("turn-off").addEventListener("click", () => sendCommand(false));

updateState();
setInterval(updateState, 1000);
