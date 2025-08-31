"""Sensor platform for Systemair SAVE VSR."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, PERCENTAGE, REVOLUTIONS_PER_MINUTE, TIME_MONTHS, TIME_SECONDS, "Pa", "ppm", "W/m³/h"
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .__init__ import SAVEVSRHub


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    hub: SAVEVSRHub = hass.data[DOMAIN][entry.entry_id]
    entities = [
        SAVEVSRSensor(hub, "Test Mode Reg", "vsr_test_mode_reg", None, None, None, "test_mode_reg"),
        SAVEVSRSensor(hub, "Sensor Flow Piggyback SAF", "vsr_sensor_flow_piggyback_saf", None, SensorStateClass.MEASUREMENT, None, "sensor_flow_piggyback_saf"),
        SAVEVSRSensor(hub, "Sensor Flow Piggyback EAF", "vsr_sensor_flow_piggyback_eaf", None, SensorStateClass.MEASUREMENT, None, "sensor_flow_piggyback_eaf"),
        SAVEVSRSensor(hub, "Mode Speed", "vsr_mode_speed", None, SensorStateClass.MEASUREMENT, None, "mode_speed"),
        SAVEVSRSensor(hub, "Mode Main", "vsr_mode_main", None, SensorStateClass.MEASUREMENT, None, "mode_main"),
        SAVEVSRSensor(hub, "Temp Outdoor", "vsr_temp_outdoor", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_outdoor"),
        SAVEVSRSensor(hub, "Temp Supply", "vsr_temp_supply", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_supply"),
        SAVEVSRSensor(hub, "Temp Extract", "vsr_temp_extract", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_extract"),
        SAVEVSRSensor(hub, "Temp Overheat", "vsr_temp_overheat", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_overheat"),
        SAVEVSRSensor(hub, "Humidity", "vsr_humidity", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT, PERCENTAGE, "humidity"),
        SAVEVSRSensor(hub, "Humidity Exhaust", "vsr_humidity_exhaust", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT, PERCENTAGE, "humidity_exhaust"),
        SAVEVSRSensor(hub, "Humidity Intake", "vsr_humidity_intake", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT, PERCENTAGE, "humidity_intake"),
        SAVEVSRSensor(hub, "Setpoint RH Transfer", "vsr_setpoint_RH_transfer", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT, PERCENTAGE, "setpoint_RH_transfer"),
        SAVEVSRSensor(hub, "Humidity Return Value", "vsr_humidity_return_value", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT, PERCENTAGE, "humidity_return_value"),
        SAVEVSRSensor(hub, "SAF RPM", "vsr_saf_rpm", None, SensorStateClass.MEASUREMENT, REVOLUTIONS_PER_MINUTE, "saf_rpm"),
        SAVEVSRSensor(hub, "EAF RPM", "vsr_eaf_rpm", None, SensorStateClass.MEASUREMENT, REVOLUTIONS_PER_MINUTE, "eaf_rpm"),
        SAVEVSRSensor(hub, "Fan Supply", "vsr_fan_supply", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "fan_supply"),
        SAVEVSRSensor(hub, "Fan Extract", "vsr_fan_extract", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "fan_extract"),
        SAVEVSRSensor(hub, "Heat Exchanger State", "vsr_heat_exchanger_state", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "heat_exchanger_state"),
        SAVEVSRSensor(hub, "Rotor", "vsr_rotor", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "rotor"),
        SAVEVSRSensor(hub, "Heater", "vsr_heater", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "heater"),
        SAVEVSRSensor(hub, "Filter Replace Month", "vsr_filter_replace_month", None, SensorStateClass.MEASUREMENT, TIME_MONTHS, "filter_replace_month"),
        SAVEVSRSensor(hub, "Filter Replace Seconds", "vsr_filter_replace_seconds", None, SensorStateClass.MEASUREMENT, TIME_SECONDS, "filter_replace_seconds"),
        SAVEVSRSensor(hub, "Setpoint ECO Offset", "vsr_setpoint_eco_offset", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "setpoint_eco_offset"),
        SAVEVSRSensor(hub, "Usermode Remain Time", "vsr_usermode_remain_time", None, SensorStateClass.MEASUREMENT, TIME_SECONDS, "usermode_remain_time"),
        SAVEVSRSensor(hub, "Cooling Recovery Temp", "vsr_cooling_recovery_temp", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "cooling_recovery_temp"),
        # Added from conversation and manual
        SAVEVSRSensor(hub, "Temp Exhaust", "vsr_temp_exhaust", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_exhaust"),
        SAVEVSRSensor(hub, "Temp Outside", "vsr_temp_outside", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_outside"),
        SAVEVSRSensor(hub, "Rotor Rotation Speed", "vsr_rotor_rotation_speed", None, SensorStateClass.MEASUREMENT, REVOLUTIONS_PER_MINUTE, "rotor_rotation_speed"),
        SAVEVSRSensor(hub, "Heater Percentage", "vsr_heater_percentage", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "heater_percentage"),
        SAVEVSRSensor(hub, "Supply Fan Speed", "vsr_supply_fan_speed", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "supply_fan_speed"),
        SAVEVSRSensor(hub, "Extract Fan Speed", "vsr_extract_fan_speed", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "extract_fan_speed"),
        SAVEVSRSensor(hub, "Filter Pressure", "vsr_filter_pressure", SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT, "Pa", "filter_pressure"),
        SAVEVSRSensor(hub, "CO2 Level", "vsr_co2_level", SensorDeviceClass.CO2, SensorStateClass.MEASUREMENT, "ppm", "co2_level"),
        SAVEVSRSensor(hub, "SFP Supply", "vsr_sfp_supply", None, SensorStateClass.MEASUREMENT, "W/m³/h", "sfp_supply"),
        SAVEVSRSensor(hub, "Remaining Filter Time", "vsr_remaining_filter_time", None, SensorStateClass.MEASUREMENT, TIME_SECONDS, "remaining_filter_time"),
        SAVEVSRSensor(hub, "Defrost Level", "vsr_defrost_level", None, SensorStateClass.MEASUREMENT, None, "defrost_level"),
        # Additional from manual
        SAVEVSRSensor(hub, "Exhaust Humidity", "vsr_exhaust_humidity", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT, PERCENTAGE, "exhaust_humidity"),
        SAVEVSRSensor(hub, "Intake Humidity", "vsr_intake_humidity", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT, PERCENTAGE, "intake_humidity"),
        SAVEVSRSensor(hub, "Supply Air Pressure", "vsr_supply_air_pressure", SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT, "Pa", "supply_air_pressure"),
        SAVEVSRSensor(hub, "Extract Air Pressure", "vsr_extract_air_pressure", SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT, "Pa", "extract_air_pressure"),
        SAVEVSRSensor(hub, "Energy Consumption", "vsr_energy_consumption", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, "kWh", "energy_consumption"),
        SAVEVSRSensor(hub, "Heat Recovery Efficiency", "vsr_heat_recovery_efficiency", None, SensorStateClass.MEASUREMENT, PERCENTAGE, "heat_recovery_efficiency"),
    ]
    async_add_entities(entities)


class SAVEVSRSensor(CoordinatorEntity, SensorEntity):
    """SAVE VSR sensor."""

    def __init__(self, hub: SAVEVSRHub, name: str, unique_id: str, device_class: SensorDeviceClass | None, state_class: SensorStateClass | None, unit: str | None, key: str) -> None:
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
