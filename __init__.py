"""The Systemair SAVE VSR integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from pymodbus.client import AsyncModbusSerialClient
from pymodbus.exceptions import ModbusException

from .const import DOMAIN, UPDATE_INTERVAL_SECONDS, SLAVE_ID

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Systemair SAVE VSR from a config entry."""
    hub = SAVEVSRHub(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hub

    # Ensure initial data
    await hub.coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hub: SAVEVSRHub = hass.data[DOMAIN].pop(entry.entry_id)
        hub.client.close()  # Close without await
    return unload_ok

async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry, device: dr.DeviceEntry
) -> dict:
    hub: SAVEVSRHub = hass.data[DOMAIN][entry.entry_id]
    data = hub.coordinator.data or {}
    diagnostics = {k: v for k, v in data.items() if k.startswith("alarm_")}
    return diagnostics

class SAVEVSRHub:
    """Hub for Systemair SAVE VSR Modbus communication."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry

        self.client = AsyncModbusSerialClient(
            port=entry.data["port"],
            baudrate=entry.data["baudrate"],
            stopbits=entry.data["stopbits"],
            bytesize=entry.data["bytesize"],
            parity=entry.data["parity"],
            method="rtu",
        )

        self._device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, "save_vsr_device")},
            name="SAVE VSR Ventilation Unit",
            manufacturer="Systemair",
            model="SAVE VSR500",
        )

        dev_reg = dr.async_get(hass)
        dev_reg.async_get_or_create(config_entry_id=entry.entry_id, **self._device_info)

        self.coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name="save_vsr_coordinator",
            update_method=self._async_update_data,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )

    @property
    def device_info(self) -> dr.DeviceInfo:
        return self._device_info

    async def _ensure_connected(self) -> None:
        """Connect client if not connected."""
        if not self.client.connected:
            _LOGGER.debug("Connecting to Systemair SAVE VSR Modbus RTU...")
            connected = await self.client.connect()
            if not connected:
                raise UpdateFailed("Failed to connect to Systemair SAVE VSR")

    async def _async_update_data(self) -> dict:
        """Fetch data from the VSR unit."""
        await self._ensure_connected()
        data = {}
        try:
            # Define registers to read (simplified for demonstration)
            registers = {
                "temp_supply": (12102, "input", 0.1),
                "target_temp": (2000, "holding", 0.1),
                "mode_main": (1160, "input", 1),
                "fan_running": (1350, "holding", 1),
                "eco_modus": (2504, "holding", 1, "bool"),
                "heater_switch": (3001, "holding", 1, "bool"),
                "rh_switch": (2146, "holding", 1, "bool"),
                # Add more registers here as needed...
            }

            for name, reg_info in registers.items():
                addr, reg_type, scale = reg_info[0], reg_info[1], reg_info[2]
                value_type = reg_info[3] if len(reg_info) > 3 else "normal"

                if reg_type == "holding":
                    rr = await self.client.read_holding_registers(addr, 1, slave=SLAVE_ID)
                else:
                    rr = await self.client.read_input_registers(addr, 1, slave=SLAVE_ID)

                if rr.isError():
                    data[name] = None if value_type != "bool" else False
                else:
                    raw = rr.registers[0]
                    if value_type == "bool":
                        data[name] = raw > 0
                    else:
                        data[name] = raw * scale

            return data
        except ModbusException as err:
            _LOGGER.error("Modbus error: %s", err)
            raise UpdateFailed(err)
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            raise UpdateFailed(err)

    async def async_write_register(self, address: int, value: int, slave: int = SLAVE_ID) -> bool:
        """Async write single register."""
        try:
            await self._ensure_connected()
            wr = await self.client.write_register(address, value, slave=slave)
            return not wr.isError()
        except Exception as err:
            _LOGGER.error("Write failed (addr=%s, val=%s): %s", address, value, err)
            return False
