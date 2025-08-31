"""Binary sensor platform for VSR500."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .__init__ import VSR500Hub


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    hub: VSR500Hub = hass.data[DOMAIN][entry.entry_id]
    entities = [
        VSR500BinarySensor(hub, "Damper State", "vsr_damper_state", BinarySensorDeviceClass.OPENING, "damper_state"),
        VSR500BinarySensor(hub, "Cooldown", "vsr_cooldown", BinarySensorDeviceClass.COLD, "cooldown"),
        VSR500BinarySensor(hub, "Humidity Return", "vsr_humidity_return", BinarySensorDeviceClass.MOISTURE, "humidity_return"),
        VSR500BinarySensor(hub, "Humidity Transfer Enabled", "vsr_humidity_transfer_enabled", BinarySensorDeviceClass.MOISTURE, "humidity_transfer_enabled"),
        VSR500BinarySensor(hub, "Mode Summer Winter", "vsr_mode_summerwinter", BinarySensorDeviceClass.HEAT, "mode_summerwinter"),
        VSR500BinarySensor(hub, "Fan Running", "vsr_fan_running", BinarySensorDeviceClass.RUNNING, "fan_running"),
        VSR500BinarySensor(hub, "Cooling Recovery", "vsr_cooling_recovery", BinarySensorDeviceClass.COLD, "cooling_recovery"),
        VSR500BinarySensor(hub, "Alarm Type A", "vsr_alarm_typeA", BinarySensorDeviceClass.PROBLEM, "alarm_typeA"),
        VSR500BinarySensor(hub, "Alarm Type B", "vsr_alarm_typeB", BinarySensorDeviceClass.PROBLEM, "alarm_typeB"),
        VSR500BinarySensor(hub, "Alarm Type C", "vsr_alarm_typeC", BinarySensorDeviceClass.PROBLEM, "alarm_typeC"),
        VSR500BinarySensor(hub, "Alarm SAF", "vsr_alarm_saf", BinarySensorDeviceClass.PROBLEM, "alarm_saf"),
        VSR500BinarySensor(hub, "Alarm Fire", "vsr_alarm_fire", BinarySensorDeviceClass.PROBLEM, "alarm_fire"),
        VSR500BinarySensor(hub, "Alarm EAF", "vsr_alarm_eaf", BinarySensorDeviceClass.PROBLEM, "alarm_eaf"),
        VSR500BinarySensor(hub, "Alarm SAF RPM", "vsr_alarm_saf_rpm", BinarySensorDeviceClass.PROBLEM, "alarm_saf_rpm"),
        VSR500BinarySensor(hub, "Alarm EAF RPM", "vsr_alarm_eaf_rpm", BinarySensorDeviceClass.PROBLEM, "alarm_eaf_rpm"),
        VSR500BinarySensor(hub, "Alarm FPT", "vsr_alarm_fpt", BinarySensorDeviceClass.PROBLEM, "alarm_fpt"),
        VSR500BinarySensor(hub, "Alarm OAT", "vsr_alarm_oat", BinarySensorDeviceClass.PROBLEM, "alarm_oat"),
        VSR500BinarySensor(hub, "Alarm SAT", "vsr_alarm_sat", BinarySensorDeviceClass.SAFETY, "alarm_sat"),
        VSR500BinarySensor(hub, "Alarm RAT", "vsr_alarm_rat", BinarySensorDeviceClass.SAFETY, "alarm_rat"),
        VSR500BinarySensor(hub, "Alarm EAT", "vsr_alarm_eat", BinarySensorDeviceClass.SAFETY, "alarm_eat"),
        VSR500BinarySensor(hub, "Alarm ECT", "vsr_alarm_ect", BinarySensorDeviceClass.SAFETY, "alarm_ect"),
        VSR500BinarySensor(hub, "Alarm EFT", "vsr_alarm_eft", BinarySensorDeviceClass.PROBLEM, "alarm_eft"),
        VSR500BinarySensor(hub, "Alarm OHT", "vsr_alarm_oht", BinarySensorDeviceClass.PROBLEM, "alarm_oht"),
        VSR500BinarySensor(hub, "Alarm EMT", "vsr_alarm_emt", BinarySensorDeviceClass.PROBLEM, "alarm_emt"),
        VSR500BinarySensor(hub, "Alarm BYS", "vsr_alarm_bys", BinarySensorDeviceClass.PROBLEM, "alarm_bys"),
        VSR500BinarySensor(hub, "Alarm Sec Air", "vsr_alarm_sec_air", BinarySensorDeviceClass.PROBLEM, "alarm_sec_air"),
        VSR500BinarySensor(hub, "Alarm RH", "vsr_alarm_rh", BinarySensorDeviceClass.PROBLEM, "alarm_rh"),
        VSR500BinarySensor(hub, "Alarm Frost Protect", "vsr_alarm_frost_protect", BinarySensorDeviceClass.COLD, "alarm_frost_protect"),
        VSR500BinarySensor(hub, "Alarm Defrosting", "vsr_alarm_defrosting", BinarySensorDeviceClass.RUNNING, "alarm_defrosting"),
        VSR500BinarySensor(hub, "Alarm Low SAT", "vsr_alarm_low_SAT", BinarySensorDeviceClass.PROBLEM, "alarm_low_SAT"),
        VSR500BinarySensor(hub, "Alarm PDM RHS", "vsr_alarm_pdm_rhs", BinarySensorDeviceClass.PROBLEM, "alarm_pdm_rhs"),
        VSR500BinarySensor(hub, "Alarm PDM EAT", "vsr_alarm_pdm_eat", BinarySensorDeviceClass.PROBLEM, "alarm_pdm_eat"),
        VSR500BinarySensor(hub, "Alarm Man Fan Stop", "vsr_alarm_man_fan_stop", BinarySensorDeviceClass.RUNNING, "alarm_man_fan_stop"),
        VSR500BinarySensor(hub, "Alarm Overheat Temp", "vsr_alarm_overheat_temp", BinarySensorDeviceClass.SAFETY, "alarm_overheat_temp"),
        VSR500BinarySensor(hub, "Alarm Filter", "vsr_alarm_filter", BinarySensorDeviceClass.PROBLEM, "alarm_filter"),
        VSR500BinarySensor(hub, "Alarm Filter Warn", "vsr_alarm_filter_warn", BinarySensorDeviceClass.PROBLEM, "alarm_filter_warn"),
    ]
    async_add_entities(entities)


class VSR500BinarySensor(CoordinatorEntity, BinarySensorEntity):
    """VSR500 binary sensor."""

    def __init__(self, hub: VSR500Hub, name: str, unique_id: str, device_class: BinarySensorDeviceClass, key: str) -> None:
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
