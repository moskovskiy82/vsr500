"""Sensor platform for Systemair SAVE VSR (VSR500)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .__init__ import SAVEVSRHub


# -----------------------------
# ENUM MAPPINGS
# -----------------------------

# Speed/mode labels (adjust if your unit uses different naming)
MODE_SPEED_MAP: Final[dict[int, str]] = {
    0: "Off",
    1: "Low",
    2: "Medium",
    3: "High",
    4: "Boost",
}

MODE_MAIN_MAP: Final[dict[int, str]] = {
    0: "Away",
    1: "Home",
    2: "High",
    3: "Cooling",
    4: "Manual",
}

# Many Systemair alarms are 0..3 in official docs.
# Your current hub marks a lot of them as bool (0/1). We map both:
ALARM_STATE_MAP: Final[dict[int, str]] = {
    0: "Inactive",
    1: "Active",
    2: "Waiting",
    3: "Cleared Error Active",
}


# -----------------------------
# Entity Description with mapping
# -----------------------------

@dataclass(frozen=True, kw_only=True)
class SAVEVSRSensorDescription(SensorEntityDescription):
    """Describes a Systemair SAVE VSR sensor with optional value mapping."""
    coordinator_key: str
    value_map: dict[int, str] | None = None  # raw register -> label


# -----------------------------
# Operational sensors (temperatures, pressures, speeds, percentages)
# -----------------------------

SENSORS: tuple[SAVEVSRSensorDescription, ...] = (
    # Modes (ENUM)
    SAVEVSRSensorDescription(
        key="vsr_mode_speed",
        name="Mode Speed",
        device_class=SensorDeviceClass.ENUM,
        options=list(MODE_SPEED_MAP.values()),
        value_map=MODE_SPEED_MAP,
        coordinator_key="mode_speed",
    ),
    SAVEVSRSensorDescription(
        key="vsr_mode_main",
        name="Mode Main",
        device_class=SensorDeviceClass.ENUM,
        options=list(MODE_MAIN_MAP.values()),
        value_map=MODE_MAIN_MAP,
        coordinator_key="mode_main",
    ),

    # Temperatures
    SAVEVSRSensorDescription(
        key="vsr_temp_outdoor",
        name="Temp Outdoor",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        coordinator_key="temp_outdoor",
    ),
    SAVEVSRSensorDescription(
        key="vsr_temp_supply",
        name="Temp Supply",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        coordinator_key="temp_supply",
    ),
    SAVEVSRSensorDescription(
        key="vsr_temp_extract",
        name="Temp Extract",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        coordinator_key="temp_extract",
    ),
    SAVEVSRSensorDescription(
        key="vsr_temp_exhaust",
        name="Temp Exhaust",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        coordinator_key="temp_exhaust",
    ),
    SAVEVSRSensorDescription(
        key="vsr_temp_overheat",
        name="Temp Overheat",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        coordinator_key="temp_overheat",
    ),

    # Pressures
    SAVEVSRSensorDescription(
        key="vsr_supply_air_pressure",
        name="Supply Air Pressure",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.PA,
        coordinator_key="supply_air_pressure",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_extract_air_pressure",
        name="Extract Air Pressure",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.PA,
        coordinator_key="extract_air_pressure",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    # Efficiency / SFP
    SAVEVSRSensorDescription(
        key="vsr_heat_recovery_efficiency",
        name="Heat Recovery Efficiency",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        coordinator_key="heat_recovery_efficiency",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_sfp_supply",
        name="SFP Supply",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="W/m³/h",
        coordinator_key="sfp_supply",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    # Fan RPM (keep device_class None; rpm is not a standard HA speed device class)
    SAVEVSRSensorDescription(
        key="vsr_saf_rpm",
        name="FAN SAF RPM",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        coordinator_key="saf_rpm",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_eaf_rpm",
        name="FAN EAF RPM",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        coordinator_key="eaf_rpm",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    # Fan Percentages / Speeds
    SAVEVSRSensorDescription(
        key="vsr_fan_supply",
        name="Fan Supply %",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        coordinator_key="fan_supply",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_fan_extract",
        name="Fan Extract %",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        coordinator_key="fan_extract",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_supply_fan_speed",
        name="Supply Fan Speed %",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        coordinator_key="supply_fan_speed",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_extract_fan_speed",
        name="Extract Fan Speed %",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        coordinator_key="extract_fan_speed",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    # Heater / Rotor / HX
    SAVEVSRSensorDescription(
        key="vsr_heater_percentage",
        name="Heater %",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        coordinator_key="heater_percentage",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_heat_exchanger_state",
        name="Heat Exchanger State %",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        coordinator_key="heat_exchanger_state",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_rotor",
        name="Rotor %",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        coordinator_key="rotor",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    # Some firmwares expose an extra 'heater' percentage (keep if present)
    SAVEVSRSensorDescription(
        key="vsr_heater",
        name="Heater (Alt) %",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        coordinator_key="heater",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    # ECO / Cooling
    SAVEVSRSensorDescription(
        key="vsr_setpoint_eco_offset",
        name="Setpoint ECO Offset",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        coordinator_key="setpoint_eco_offset",
    ),
    SAVEVSRSensorDescription(
        key="vsr_cooling_recovery_temp",
        name="Cooling Recovery Temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        coordinator_key="cooling_recovery_temp",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    # Timers / Filter lifetime (if present)
    SAVEVSRSensorDescription(
        key="vsr_usermode_remain_time",
        name="Usermode Remaining Time",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        coordinator_key="usermode_remain_time",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_filter_replace_seconds",
        name="Filter Remaining Time",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        coordinator_key="filter_replace_seconds",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    # Optional: humidity (only if provided by coordinator; otherwise stays Unknown)
    SAVEVSRSensorDescription(
        key="vsr_humidity",
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        coordinator_key="humidity",
    ),
)


# -----------------------------
# Alarm sensors (ENUM, Diagnostic)
# -----------------------------

ALARM_SENSORS: tuple[SAVEVSRSensorDescription, ...] = (
    # Type A/B/C
    SAVEVSRSensorDescription(
        key="vsr_alarm_typeA",
        name="Alarm Type A",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_typeA",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_typeB",
        name="Alarm Type B",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_typeB",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_typeC",
        name="Alarm Type C",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_typeC",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    # Individual alarms (mapped; bool will map to Inactive/Active)
    SAVEVSRSensorDescription(
        key="vsr_alarm_saf",
        name="Alarm SAF",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_saf",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_eaf",
        name="Alarm EAF",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_eaf",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_frost_protect",
        name="Alarm Frost Protect",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_frost_protect",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_defrosting",
        name="Alarm Defrosting",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_defrosting",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    SAVEVSRSensorDescription(
        key="vsr_alarm_saf_rpm",
        name="Alarm SAF RPM",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_saf_rpm",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_eaf_rpm",
        name="Alarm EAF RPM",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_eaf_rpm",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    SAVEVSRSensorDescription(
        key="vsr_alarm_fpt",
        name="Alarm FPT",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_fpt",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_oat",
        name="Alarm OAT Sensor",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_oat",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_sat",
        name="Alarm SAT Sensor",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_sat",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_rat",
        name="Alarm RAT Sensor",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_rat",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_eat",
        name="Alarm EAT Sensor",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_eat",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_ect",
        name="Alarm ECT Sensor",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_ect",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_eft",
        name="Alarm EFT Sensor",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_eft",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_oht",
        name="Alarm OHT Sensor",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_oht",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_emt",
        name="Alarm EMT Sensor",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_emt",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    SAVEVSRSensorDescription(
        key="vsr_alarm_bys",
        name="Alarm Bypass/Damper",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_bys",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_sec_air",
        name="Alarm Sec Air",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_sec_air",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    SAVEVSRSensorDescription(
        key="vsr_alarm_filter",
        name="Alarm Filter",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_filter",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_filter_warn",
        name="Alarm Filter Warn",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_filter_warn",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    SAVEVSRSensorDescription(
        key="vsr_alarm_rh",
        name="Alarm RH/Humidity",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_rh",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_low_SAT",
        name="Alarm Low SAT",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_low_SAT",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    SAVEVSRSensorDescription(
        key="vsr_alarm_pdm_rhs",
        name="Alarm PDM RHS",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_pdm_rhs",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_pdm_eat",
        name="Alarm PDM EAT",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_pdm_eat",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_man_fan_stop",
        name="Alarm Manual Fan Stop",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_man_fan_stop",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SAVEVSRSensorDescription(
        key="vsr_alarm_overheat_temp",
        name="Alarm Overheat Temp",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_overheat_temp",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    SAVEVSRSensorDescription(
        key="vsr_alarm_fire",
        name="Alarm Fire",
        device_class=SensorDeviceClass.ENUM,
        options=list(ALARM_STATE_MAP.values()),
        value_map=ALARM_STATE_MAP,
        coordinator_key="alarm_fire",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


# -----------------------------
# Setup
# -----------------------------

async def async_setup_entry(hass, entry, async_add_entities) -> None:
    hub: SAVEVSRHub = hass.data[DOMAIN][entry.entry_id]
    entities: list[SAVEVSRSensor] = [
        SAVEVSRSensor(hub, desc) for desc in (*SENSORS, *ALARM_SENSORS)
    ]
    async_add_entities(entities)


# -----------------------------
# Entity
# -----------------------------

class SAVEVSRSensor(CoordinatorEntity, SensorEntity):
    """Representation of a SAVE VSR sensor."""

    _attr_has_entity_name = False  # Keep your explicit names

    entity_description: SAVEVSRSensorDescription

    def __init__(self, hub: SAVEVSRHub, description: SAVEVSRSensorDescription) -> None:
        super().__init__(hub.coordinator)
        self._hub = hub
        self.entity_description = description

        # Keep your previous unique_id stable to avoid entity duplication
        self._attr_unique_id = description.key
        self._attr_name = description.name
        self._attr_device_info = hub.device_info

        # Ensure HA sees enum options (for SensorDeviceClass.ENUM)
        if description.device_class == SensorDeviceClass.ENUM and description.options:
            self._attr_options = list(description.options)

        # Pass-through description-defined properties (device_class, unit, state_class, category)
        self._attr_device_class = description.device_class
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_state_class = description.state_class
        self._attr_entity_category = description.entity_category

    @staticmethod
    def _map_value(raw: object, value_map: dict[int, str] | None) -> object | None:
        """Map raw register (int/bool) to label using value_map; tolerate bools."""
        if raw is None or not value_map:
            return raw
        try:
            if isinstance(raw, bool):
                normalized = 1 if raw else 0
            else:
                normalized = int(raw)
        except (ValueError, TypeError):
            return raw
        return value_map.get(normalized, raw)

    @property
    def native_value(self):
        """Return the current value."""
        data = self.coordinator.data or {}
        raw = data.get(self.entity_description.coordinator_key)

        # Apply mapping for ENUMs or any description with a value_map
        mapped = self._map_value(raw, self.entity_description.value_map)
        return mapped
