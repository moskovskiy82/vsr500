"""Binary sensor platform for Systemair SAVE VSR."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .__init__ import SAVEVSRHub


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    hub: SAVEVSRHub = hass.data[DOMAIN][entry.entry_id]
    entities = [
        SAVEVSRBinarySensor(hub, "Damper State", "vsr_damper_state", BinarySensorDeviceClass.OPENING, "damper_state"),
        SAVEVSRBinarySensor(hub, "Cooldown", "vsr_cooldown", BinarySensorDeviceClass.COLD, "cooldown"),
        SAVEVSRBinarySensor(hub, "Humidity Return", "vsr_humidity_return", BinarySensorDeviceClass.MOISTURE, "humidity_return"),
        SAVEVSRBinarySensor(hub, "Humidity Transfer Enabled", "vsr_humidity_transfer_enabled", BinarySensorDeviceClass.MOISTURE, "humidity_transfer_enabled"),
        SAVEVSRBinarySensor(hub, "Mode Summer Winter", "vsr_mode_summerwinter", BinarySensorDeviceClass.HEAT, "mode_summerwinter"),
        SAVEVSRBinarySensor(hub, "Fan Running", "vsr_fan_running", BinarySensorDeviceClass.RUNNING, "fan_running"),
        SAVEVSRBinarySensor(hub, "Cooling Recovery", "vsr_cooling_recovery", BinarySensorDeviceClass.COLD, "cooling_recovery"),
        # Operational binary sensors only; alarms moved to diagnostics
    ]
    async_add_entities(entities)


class SAVEVSRBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """SAVE VSR binary sensor."""

    def __init__(self, hub: SAVEVSRHub, name: str, unique_id: str, device_class: BinarySensorDeviceClass, key: str) -> None:
        super().__init__(hub.coordinator)
        self.hub = hub
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_device_class = device_class
        self._key = key
        self._attr_device_info = hub.device_info

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data
        if not data:
            return None
        return bool(data.get(self._key, False))
