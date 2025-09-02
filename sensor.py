"""Sensor platform for Systemair SAVE VSR."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    EntityCategory,
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfVolume,
    UnitOfMass,
    UnitOfEnergy,
    UnitOfTime,
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
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
# TIME_MONTHS = "months"  # Define the missing constant here**
# TIME_SECONDS = "s"      # And this one as well**

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up SAVE VSR sensors based on a config entry."""
    hub: SAVEVSRHub = hass.data[DOMAIN][entry.entry_id]

    sensors = [
#Modes

        SAVEVSRSensor(hub, "Mode Speed", "vsr_mode_speed", None, SensorStateClass.MEASUREMENT, None, "mode_speed"),
        SAVEVSRSensor(hub, "Mode Main", "vsr_mode_main", None, SensorStateClass.MEASUREMENT, None, "mode_main"),
#Temperatures
        SAVEVSRSensor(hub, "Temp Outdoor", "vsr_temp_outdoor", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_outdoor"),
        SAVEVSRSensor(hub, "Temp Supply", "vsr_temp_supply", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_supply"),
        SAVEVSRSensor(hub, "Temp Extract", "vsr_temp_extract", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_extract"),
        SAVEVSRSensor(hub, "Temp Overheat", "vsr_temp_overheat", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "temp_overheat"),

#Humidity data
        SAVEVSRSensor(hub, "Humidity", "vsr_humidity", SensorDeviceClass.HUMIDITY, SensorStateClass.MEASUREMENT, PERCENTAGE, "humidity"),

#Fan speeds
        SAVEVSRSensor(hub, "FAN SAF", "vsr_saf_rpm", None, SensorStateClass.MEASUREMENT, REVOLUTIONS_PER_MINUTE, "saf_rpm"),
        SAVEVSRSensor(hub, "FAN EAF", "vsr_eaf_rpm", None, SensorStateClass.MEASUREMENT, REVOLUTIONS_PER_MINUTE, "eaf_rpm"),
        SAVEVSRSensor(hub, "Fan Supply", "vsr_fan_supply", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "fan_supply"),
        SAVEVSRSensor(hub, "Fan Extract", "vsr_fan_extract", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "fan_extract"),

# Heater Rotor		
        SAVEVSRSensor(hub, "Heat Exchanger State", "vsr_heat_exchanger_state", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "heat_exchanger_state"),
        SAVEVSRSensor(hub, "Rotor", "vsr_rotor", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "rotor"),
        SAVEVSRSensor(hub, "Heater", "vsr_heater", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, PERCENTAGE, "heater"),
        SAVEVSRSensor(hub, "Setpoint ECO Offset", "vsr_setpoint_eco_offset", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "setpoint_eco_offset"),
        SAVEVSRSensor(hub, "Cooling Recovery Temp", "vsr_cooling_recovery_temp", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, UnitOfTemperature.CELSIUS, "cooling_recovery_temp"),		

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
