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
        SAVEVSRSwitch(hub, "ECO Mode", "vsr_eco_modus", "eco_modus", 1, 0, 2504),
        SAVEVSRSwitch(hub, "Heater Switch", "vsr_heater_switch", "heater_switch", 1, 0, 3001),
        SAVEVSRSwitch(hub, "RH Switch", "vsr_rh_switch", "rh_switch", 1, 0, 2203),
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
        key: str,
        command_on: int,
        command_off: int,
        verify_address: int,
    ) -> None:
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
    def is_on(self) -> bool | None:
        """Return the current state of the switch."""
        data = self.coordinator.data
        if not data:
            return None
        return bool(data.get(self._key, False))

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on using Modbus."""
        success = await self.hub.async_write_register(
            self._verify_address, self._command_on, slave=SLAVE_ID
        )
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off using Modbus."""
        success = await self.hub.async_write_register(
            self._verify_address, self._command_off, slave=SLAVE_ID
        )
        if success:
            await self.coordinator.async_request_refresh()
