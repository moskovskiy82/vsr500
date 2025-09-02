"""Climate platform for Systemair SAVE VSR."""
from __future__ import annotations

from homeassistant.components.climate import ClimateEntity, HVACMode, HVACAction, ClimateEntityFeature
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SLAVE_ID
from .__init__ import SAVEVSRHub


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    hub: SAVEVSRHub = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SAVEVSRClimate(hub)])


class SAVEVSRClimate(CoordinatorEntity[SAVEVSRHub], ClimateEntity):
    """SAVE VSR climate entity."""

    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE | ClimateEntityFeature.PRESET_MODE
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.AUTO, HVACMode.FAN_ONLY]
    _attr_fan_modes = ["low", "medium", "high"]
    _attr_preset_modes = ["crowded", "refresh", "fireplace", "away", "holiday", "kitchen", "vacuum_cleaner"]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_name = "Vent SAVE VSR"
    _attr_unique_id = "vsr_vent_SAVE_VSR"

    def __init__(self, hub: SAVEVSRHub) -> None:
        super().__init__(hub.coordinator)
        self.hub = hub
        self._attr_device_info = hub.device_info

    @property
    def current_temperature(self):
        return self.coordinator.data.get("temp_supply")

    @property
    def target_temperature(self):
        return self.coordinator.data.get("target_temp")

    @property
    def hvac_mode(self):
        mode = self.coordinator.data.get("mode_main")
        if mode == 6:
            return HVACMode.OFF
        if mode == 0:
            return HVACMode.AUTO
        if mode == 1:
            return HVACMode.FAN_ONLY
        return HVACMode.OFF

    @property
    def hvac_action(self):
        # Use Home Assistant's HVACAction enum
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        return HVACAction.FAN

    async def async_set_hvac_mode(self, hvac_mode: str):
        value: int | None = None
        if hvac_mode == HVACMode.OFF:
            value = 7
        elif hvac_mode == HVACMode.AUTO:
            value = 1
        elif hvac_mode == HVACMode.FAN_ONLY:
            value = 2
        if value is None:
            return
        if await self.hub.async_write_register(1161, value, slave=SLAVE_ID):
            await self.coordinator.async_request_refresh()

    @property
    def fan_mode(self):
        speed = self.coordinator.data.get("mode_speed")
        if speed == 2:
            return "low"
        if speed == 3:
            return "medium"
        if speed == 4:
            return "high"
        return "low"

    async def async_set_fan_mode(self, fan_mode: str):
        mapping = {"low": 2, "medium": 3, "high": 4}
        value = mapping.get(fan_mode)
        if value is None:
            return
        if await self.hub.async_write_register(1130, value, slave=SLAVE_ID):
            await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        value = int(temperature * 10)  # Scale 0.1 °C
        if await self.hub.async_write_register(2000, value, slave=SLAVE_ID):
            await self.coordinator.async_request_refresh()

    @property
    def preset_mode(self):
        mode = self.coordinator.data.get("mode_main")
        mapping = {
            2: "crowded",
            3: "refresh",
            4: "fireplace",
            5: "away",
            6: "holiday",
            7: "kitchen",
            8: "vacuum_cleaner",
        }
        return mapping.get(mode, None)

    async def async_set_preset_mode(self, preset_mode: str):
        mapping = {
            "crowded": 2,
            "refresh": 3,
            "fireplace": 4,
            "away": 5,
            "holiday": 6,
            "kitchen": 7,
            "vacuum_cleaner": 8,
        }
        value = mapping.get(preset_mode)
        if value is None:
            return
        if await self.hub.async_write_register(1161, value, slave=SLAVE_ID):
            await self.coordinator.async_request_refresh()