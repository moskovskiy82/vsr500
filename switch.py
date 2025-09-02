"""Switch platform for Systemair SAVE VSR."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SLAVE_ID
from .__init__ import SAVEVSRHub


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up SAVE VSR switches from a config entry."""
    hub: SAVEVSRHub = hass.data[DOMAIN][entry.entry_id]

    entities = [
        SAVEVSRSwitch(hub, "ECO Mode", "vsr_eco_modus", 2504, 1, 0, "eco_modus"),
        SAVEVSRSwitch(hub, "Heater Switch", "vsr_heater_switch", 3001, 1, 0, "heater_switch"),
        # SAVEVSRSwitch(hub, "RH Switch", "vsr_rh_switch", 2203, 1, 0, "humidity_transfer_enabled"),  # Updated verify_key to match command address
    ]
    async_add_entities(entities)


class SAVEVSRSwitch(CoordinatorEntity, SwitchEntity):
    """SAVE VSR switch using Modbus writes."""

    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(
        self,
        hub: SAVEVSRHub,
        name: str,
        unique_id: str,
        command_address: int,
        command_on: int,
        command_off: int,
        verify_key: str,
    ) -> None:
        super().__init__(hub.coordinator)
        self.hub = hub
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._command_address = command_address
        self._command_on = command_on
        self._command_off = command_off
        self._verify_key = verify_key
        self._attr_device_info = hub.device_info

    @property
    def is_on(self) -> bool | None:
        """Return the current state of the switch from the coordinator data."""
        data = self.coordinator.data
        if not data:
            return None
        return bool(data.get(self._verify_key, False))

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on by writing to the command address."""
        if await self.hub.async_write_register(self._command_address, self._command_on):
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off by writing to the command address."""
        if await self.hub.async_write_register(self._command_address, self._command_off):
            await self.coordinator.async_request_refresh()