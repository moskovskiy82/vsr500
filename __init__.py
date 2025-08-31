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

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.BINARY_SENSOR, Platform.SENSOR, Platform.SWITCH]

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
        await hub.client.close()
    return unload_ok

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

    async def _async_update_data(self) -> dict:
        async def update_data():
            data = {}
            try:
                await self._ensure_connected()
                # Climate
                rr = await self.client.read_input_registers(12102, 1, slave=SLAVE_ID)
                data["temp_supply"] = rr.registers[0] * 0.1 if not rr.isError() else None
                rr = await self.client.read_holding_registers(2000, 1, slave=SLAVE_ID)
                data["target_temp"] = rr.registers[0] * 0.1 if not rr.isError() else None
                rr = await self.client.read_input_registers(1160, 1, slave=SLAVE_ID)
                data["mode_main"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(1130, 1, slave=SLAVE_ID)
                data["mode_speed"] = rr.registers[0] if not rr.isError() else None
                # Binary sensors (example, add all)
                rr = await self.client.read_holding_registers(14003, 1, slave=SLAVE_ID)
                data["damper_state"] = rr.registers[0] > 0 if not rr.isError() else False
                # ... (add all binary, alarms)
                # Sensors (example, add all)
                rr = await self.client.read_holding_registers(12101, 1, slave=SLAVE_ID)
                data["temp_outdoor"] = rr.registers[0] * 0.1 if not rr.isError() else None
                # ... (add all temps, humidity, RPMs, etc.)
                # Switches (read for state)
                rr = await self.client.read_holding_registers(2504, 1, slave=1)
                data["eco_modus"] = rr.registers[0] > 0 if not rr.isError() else False
                # ... (add for heater, RH)
                return data
            finally:
                await self.client.close()

        return await update_data()

    async def _ensure_connected(self) -> None:
        if not self.client.connected:
            _LOGGER.debug("Connecting to SAVE VSR Modbus RTU...")
            connected = await self.client.connect()
            if not connected:
                raise UpdateFailed("Failed to connect to SAVE VSR")

    async def async_write_register(self, address: int, value: int, slave: int = SLAVE_ID) -> bool:
        """Async write single register."""
        try:
            await self._ensure_connected()
            wr = await self.client.write_register(address, value, slave=slave)
            return not wr.isError()
        except Exception as err:
            _LOGGER.error("Write failed (addr=%s, val=%s): %s", address, value, err)
            return False
