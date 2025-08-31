"""Switch platform for Systemair SAVE VSR."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SLAVE_ID
from .__init__ import VSR500Hub


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    hub: VSR500Hub = hass.data[DOMAIN][entry.entry_id]
    entities = [
        VSR500Switch(hub, "ECO Mode", "vsr_eco_modus", "eco_modus", 1, 0, 2504),
        VSR500Switch(hub, "Heater Switch", "vsr_heater_switch", "heater_switch", 1, 0, 3001),
        VSR500Switch(hub, "RH Switch", "vsr_rh_switch", "rh_switch", 1, 0, 2203),
    ]
    async_add_entities(entities)


class VSR500Switch(CoordinatorEntity, SwitchEntity):
    """VSR500 switch using Modbus writes."""

    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, hub: VSR500Hub, name: str, unique_id: str, key: str, command_on: int, command_off: int, verify_address: int) -> None:
        super().__init__(hub.coordinator)
        self.hub = hub
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._key = key
        self._command_on = command_on
        self._command_off = command_off
        self._verify_address = verify_address
        self._attr_device_info = hub.device_info

    @property
    def is_on(self):
        data = self.coordinator.data
        if not data:
            return None
        return bool(data.get(self._key, False))

    async def async_turn_on(self, **kwargs):
        if await self.hub.async_write_register(self._verify_address, self._command_on, slave=SLAVE_ID):
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        if await self.hub.async_write_register(self._verify_address, self._command_off, slave=SLAVE_ID):
            await self.coordinator.async_request_refresh()
