"""Lee la temperatura del sensor LM75B mediante I2C."""
from smbus2 import SMBus

from settings import I2C_BUS, LM75B_ADDRESS, LM75B_TEMP_REGISTER


def read_temperature() -> float:
    """Devuelve la temperatura en grados Celsius."""
    with SMBus(I2C_BUS) as bus:
        data = bus.read_i2c_block_data(
            LM75B_ADDRESS,
            LM75B_TEMP_REGISTER,
            2,
        )

    # El LM75B entrega 11 bits de temperatura en complemento a dos.
    raw = ((data[0] << 8) | data[1]) >> 5
    if raw & 0x400:
        raw -= 0x800

    return raw * 0.125
