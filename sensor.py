"""Sensor platform for Systemair SAVE VSR."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, PERCENTAGE, REVOLUTIONS_PER_MINUTE, TIME_MONTHS, TIME_SECONDS
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .__init__ import VSR500Hub


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    hub: VSR500Hub = hass.data[DOMAIN][entry.entry_id]
    entities = [
        VSR500Sensor(hub, "Test Mode Reg", "vsr_test_mode_reg", None, None, None, "test_mode_reg"),
        VSR500Sensor(hub, "Sensor Flow Piggyback SAF", "vsr_sensor_flow_piggyback_saf", None, SensorStateClass.MEASUREMENT, None, "sensor_flow_piggyback_saf"),
        VSR500Sensor(hub, "Sensor Flow Piggyback EAF", "vsr_sensor_flow_piggyback_eaf", None, SensorStateClass.MEASUREMENT, None, "sensor_flow_piggyback_eaf"),
        VSR500Sensor(hub, "Mode Speed", "vsr_mode_speed", None, SensorStateClass.MEASUREMENT, None, "mode_speed"),
        VSR500Sensor(hub, "Mode Main", "vsr_mode_main", None, SensorStateClass.MEASUREMENT, None, "mode_main"),
        VSR500Sensor(hub, "Temp Outdoor", "vsr_temp_outdoor", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_outdoor"),
        VSR500Sensor(hub, "Temp Supply", "vsr_temp_supply", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_supply"),
        VSR500Sensor(hub, "Temp Extract", "vsr_temp_extract", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_extract"),
        VSR500Sensor(hub, "Temp Overheat", "vsr_temp_overheat", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_overheat"),
        VSR500Sensor(hub, "Humidity", "vsr_humidity", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT, PERCENTAGE, "humidity"),
        VSR500Sensor(hub, "Humidity Exhaust", "vsr_humidity_exhaust", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT, PERCENTAGE, "humidity_exhaust"),
        VSR500Sensor(hub, "Humidity Intake", "vsr_humidity_intake", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT, PERCENTAGE, "humidity_intake"),
        VSR500Sensor(hub, "Setpoint RH Transfer", "vsr_setpoint_RH_transfer", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT, PERCENTAGE, "setpoint_RH_transfer"),
        VSR500Sensor(hub, "Humidity Return Value", "vsr_humidity_return_value", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT, PERCENTAGE, "humidity_return_value"),
        VSR500Sensor(hub, "SAF RPM", "vsr_saf_rpm", None, SensorStateClass.MEASUREMENT, REVOLUTIONS_PER_MINUTE, "saf_rpm"),
        VSR500Sensor(hub, "EAF RPM", "vsr_eaf_rpm", None, SensorStateClass.MEASUREMENT, REVOLUTIONS_PER_MINUTE, "eaf_rpm"),
        VSR500Sensor(hub, "Fan Supply", "vsr_fan_supply", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "fan_supply"),
        VSR500Sensor(hub, "Fan Extract", "vsr_fan_extract", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "fan_extract"),
        VSR500Sensor(hub, "Heat Exchanger State", "vsr_heat_exchanger_state", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "heat_exchanger_state"),
        VSR500Sensor(hub, "Rotor", "vsr_rotor", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "rotor"),
        VSR500Sensor(hub, "Heater", "vsr_heater", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "heater"),
        VSR500Sensor(hub, "Filter Replace Month", "vsr_filter_replace_month", None, SensorStateClass.MEASUREMENT, TIME_MONTHS, "filter_replace_month"),
        VSR500Sensor(hub, "Filter Replace Seconds", "vsr_filter_replace_seconds", None, SensorStateClass.MEASUREMENT, TIME_SECONDS, "filter_replace_seconds"),
        VSR500Sensor(hub, "Setpoint ECO Offset", "vsr_setpoint_eco_offset", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "setpoint_eco_offset"),
        VSR500Sensor(hub, "Usermode Remain Time", "vsr_usermode_remain_time", None, SensorStateClass.MEASUREMENT, TIME_SECONDS, "usermode_remain_time"),
        VSR500Sensor(hub, "Cooling Recovery Temp", "vsr_cooling_recovery_temp", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "cooling_recovery_temp"),
        # Added from conversation and manual
        VSR500Sensor(hub, "Temp Exhaust", "vsr_temp_exhaust", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_exhaust"),
        VSR500Sensor(hub, "Temp Outside", "vsr_temp_outside", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_outside"),
        VSR500Sensor(hub, "Rotor Rotation Speed", "vsr_rotor_rotation_speed", SensorDeviceClass.SPEED, SensorStateClass.MEASUREMENT, REVOLUTIONS_PER_MINUTE, "rotor_rotation_speed"),
        VSR500Sensor(hub, "Heater Percentage", "vsr_heater_percentage", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "heater_percentage"),
        VSR500Sensor(hub, "Supply Fan Speed", "vsr_supply_fan_speed", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "supply_fan_speed"),
        VSR500Sensor(hub, "Extract Fan Speed", "vsr_extract_fan_speed", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "extract_fan_speed"),
        VSR500Sensor(hub, "Filter Pressure", "vsr_filter_pressure", SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT, "Pa", "filter_pressure"),
        VSR500Sensor(hub, "CO2 Level", "vsr_co2_level", SensorDeviceClass.CO2, SensorStateClass.MEASUREMENT, "ppm", "co2_level"),
        VSR500Sensor(hub, "SFP Supply", "vsr_sfp_supply", None, SensorStateClass.MEASUREMENT, "W/m³/h", "sfp_supply"),
        VSR500Sensor(hub, "Remaining Filter Time", "vsr_remaining_filter_time", None, SensorStateClass.MEASUREMENT, TIME_SECONDS, "remaining_filter_time"),
        VSR500Sensor(hub, "Defrost Level", "vsr_defrost_level", None, SensorStateClass.MEASUREMENT, None, "defrost_level"),
    ]
    async_add_entities(entities)


class VSR500Sensor(CoordinatorEntity, SensorEntity):
    """VSR500 sensor."""

    def __init__(self, hub: VSR500Hub, name: str, unique_id: str, device_class: SensorDeviceClass | None, state_class: SensorStateClass | None, unit: str | None, key: str) -> None:
        super().__init__(hub.coordinator)
        self.hub = hub
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit
        self._key = key
        self._attr_device_info = hub.device_info

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data:
            return None
        return data.get(self._key)
