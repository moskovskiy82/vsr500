"""Sensor platform for Systemair SAVE VSR."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    TEMP_CELSIUS,
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    TIME_MONTHS,
    TIME_SECONDS,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .__init__ import SAVEVSRHub

# Additional units not defined in HA constants
UNIT_PRESSURE_PA = "Pa"
UNIT_CO2_PPM = "ppm"
UNIT_SFP = "W/m³/h"
UNIT_KWH = "kWh"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up SAVE VSR sensors based on a config entry."""
    hub: SAVEVSRHub = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        SAVEVSRSensor(hub, "Test Mode Reg", "vsr_test_mode_reg", None, None, None, "test_mode_reg"),
        SAVEVSRSensor(hub, "Sensor Flow Piggyback SAF", "vsr_sensor_flow_piggyback_saf", None, SensorStateClass.MEASUREMENT, None, "sensor_flow_piggyback_saf"),
        SAVEVSRSensor(hub, "Sensor Flow Piggyback EAF", "vsr_sensor_flow_piggyback_eaf", None, SensorStateClass.MEASUREMENT, None, "sensor_flow_piggyback_eaf"),
        SAVEVSRSensor(hub, "Mode Speed", "vsr_mode_speed", None, SensorStateClass.MEASUREMENT, None, "mode_speed"),
        SAVEVSRSensor(hub, "Mode Main", "vsr_mode_main", None, SensorStateClass.MEASUREMENT, None, "mode_main"),
        SAVEVSRSensor(hub, "Temp Outdoor", "vsr_temp_outdoor", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, TEMP_CELSIUS, "temp_outdoor"),
        SAVEVSRSensor(hub, "Temp Supply", "vsr_temp_supply", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, TEMP_CELSIUS, "temp_supply"),
        SAVEVSRSensor(hub, "Temp Extract", "vsr_temp_extract", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, TEMP_CELSIUS, "temp_extract"),
        SAVEVSRSensor(hub, "Temp Overheat", "vsr_temp_overheat", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, TEMP_CELSIUS, "temp_overheat"),
        SAVEVSRSensor(hub, "Humidity", "vsr_humidity", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT, PERCENTAGE, "humidity"),
        SAVEVSRSensor(hub, "SAF RPM", "vsr_saf_rpm", None, SensorStateClass.MEASUREMENT, REVOLUTIONS_PER_MINUTE, "saf_rpm"),
        SAVEVSRSensor(hub, "EAF RPM", "vsr_eaf_rpm", None, SensorStateClass.MEASUREMENT, REVOLUTIONS_PER_MINUTE, "eaf_rpm"),
        SAVEVSRSensor(hub, "Filter Replace Month", "vsr_filter_replace_month", None, SensorStateClass.MEASUREMENT, TIME_MONTHS, "filter_replace_month"),
        SAVEVSRSensor(hub, "Filter Replace Seconds", "vsr_filter_replace_seconds", None, SensorStateClass.MEASUREMENT, TIME_SECONDS, "filter_replace_seconds"),
        SAVEVSRSensor(hub, "Filter Pressure", "vsr_filter_pressure", SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT, UNIT_PRESSURE_PA, "filter_pressure"),
        SAVEVSRSensor(hub, "CO2 Level", "vsr_co2_level", SensorDeviceClass.CO2, SensorStateClass.MEASUREMENT, UNIT_CO2_PPM, "co2_level"),
        SAVEVSRSensor(hub, "SFP Supply", "vsr_sfp_supply", None, SensorStateClass.MEASUREMENT, UNIT_SFP, "sfp_supply"),
        SAVEVSRSensor(hub, "Energy Consumption", "vsr_energy_consumption", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, UNIT_KWH, "energy_consumption"),
        # ...add all other sensors using the same pattern
    ]

    async_add_entities(sensors)

class SAVEVSRSensor(CoordinatorEntity, SensorEntity):
    """Representation of a SAVE VSR sensor."""

    def __init__(
        self,
        hub: SAVEVSRHub,
        name: str,
        unique_id: str,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
        unit: str | None,
        key: str,
    ) -> None:
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
        """Return the current value of the sensor."""
        data = self.coordinator.data
        if not data:
            return None
        return data.get(self._key)
