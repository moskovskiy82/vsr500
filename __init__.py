"""The Systemair SAVE VSR integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from pymodbus.client import AsyncModbusSerialClient
from pymodbus.exceptions import ModbusException

from .const import DOMAIN, UPDATE_INTERVAL_SECONDS, SLAVE_ID

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Systemair SAVE VSR from a config entry."""
    hub = SAVEVSRHub(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hub

    # Ensure initial data
    await hub.coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hub: SAVEVSRHub = hass.data[DOMAIN].pop(entry.entry_id)
        hub.client.close()  # Close without await
    return unload_ok

async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry, device: dr.DeviceEntry
) -> dict:
    hub: SAVEVSRHub = hass.data[DOMAIN][entry.entry_id]
    data = hub.coordinator.data or {}
    diagnostics = {k: v for k, v in data.items() if k.startswith("alarm_")}
    return diagnostics



class SAVEVSRHub:
    """Hub for Systemair SAVE VSR Modbus communication."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry

        self.client = AsyncModbusSerialClient(
            port=entry.data["port"],
            baudrate=entry.data["baudrate"],
            stopbits=entry.data["stopbits"],
            bytesize=entry.data["bytesize"],
            parity=entry.data["parity"],
            method="rtu",
        )

        self._device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, "save_vsr_device")},
            name="SAVE VSR Ventilation Unit",
            manufacturer="Systemair",
            model="SAVE VSR500",
        )

        dev_reg = dr.async_get(hass)
        dev_reg.async_get_or_create(config_entry_id=entry.entry_id, **self._device_info)

        self.coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name="save_vsr_coordinator",
            update_method=self._async_update_data,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )

    @property
    def device_info(self) -> dr.DeviceInfo:
        return self._device_info

    async def _ensure_connected(self) -> None:
        """Connect client if not connected."""
        if not self.client.connected:
            _LOGGER.debug("Connecting to Systemair SAVE VSR Modbus RTU...")
            connected = await self.client.connect()
            if not connected:
                raise UpdateFailed("Failed to connect to Systemair SAVE VSR")

    async def _async_update_data(self) -> dict:
        """Fetch data from the VSR unit."""
        await self._ensure_connected()
        data = {}
        try:
            # Define registers to read (simplified for demonstration)
            registers = {
                "temp_supply": (12102, "input", 0.1),
                "target_temp": (2000, "holding", 0.1),
                "mode_main": (1160, "input", 1),
                "mode_speed": (1130, "input", 1),       
                "damper_state": (14003, "holding", 1),
                "cooldown": (1351, "holding", 1),
                "humidity_return": (2146, "holding", 1),
                "humidity_transfer_enabled": (2203, "holding", 1),
                "mode_summerwinter": (1038, "holding", 1),
                "fan_running": (1350, "holding", 1),
                "cooling_recovery": (2133, "holding", 1),
                # Switches              
                "eco_modus": (2504, "holding", 1, "bool"),
                "heater_switch": (3001, "holding", 1, "bool"),
                "rh_switch": (2146, "holding", 1, "bool"),
                # Alarms
                "alarm_typeA": (15900, "holding", 1),
                "alarm_typeB": (15901, "holding", 1),
                "alarm_typeC": (15902, "holding", 1),
                "alarm_saf": (15001, "holding", 1),
                "alarm_fire": (15536, "holding", 1),
                "alarm_eaf": (15008, "holding", 1),
                "alarm_saf_rpm": (15029, "holding", 1),
                "alarm_eaf_rpm": (15036, "holding", 1),
                "alarm_fpt": (15057, "holding", 1),
                "alarm_oat": (15064, "holding", 1),
                "alarm_sat": (15071, "holding", 1),
                "alarm_rat": (15078, "holding", 1),
                "alarm_eat": (15085, "holding", 1),
                "alarm_ect": (15092, "holding", 1),
                "alarm_eft": (15099, "holding", 1),
                "alarm_oht": (15106, "holding", 1),
                "alarm_emt": (15113, "holding", 1),
                "alarm_bys": (15127, "holding", 1),
                "alarm_sec_air": (15134, "holding", 1),
                "alarm_rh": (15162, "holding", 1),
                "alarm_frost_protect": (15015, "holding", 1),
                "alarm_defrosting": (15022, "holding", 1),
                "alarm_low_SAT": (15176, "holding", 1),
                "alarm_pdm_rhs": (15508, "holding", 1),
                "alarm_pdm_eat": (15515, "holding", 1),
                "alarm_man_fan_stop": (15522, "holding", 1),
                "alarm_overheat_temp": (15529, "holding", 1),
                "alarm_filter": (15141, "holding", 1),
                "alarm_filter_warn": (15543, "holding", 1),
                # Sensors
                "test_mode_reg": (1161, "holding", 1),
                "sensor_flow_piggyback_saf": (12402, "holding", 1),
                "sensor_flow_piggyback_eaf": (12403, "holding", 1),
                "temp_outdoor": (12101, "holding", 0.1),
                "temp_extract": (12543, "holding", 0.1),
                "temp_overheat": (12107, "holding", 0.1),
                "humidity": (12135, "holding", 1),
                "humidity_exhaust": (2210, "holding", 1),
                "humidity_intake": (2211, "holding", 1),
                "setpoint_RH_transfer": (2202, "holding", 1),
                "humidity_return_value": (2200, "holding", 1),
                "saf_rpm": (12400, "holding", 1),
                "eaf_rpm": (12401, "holding", 1),
                "fan_supply": (14000, "holding", 1),
                "fan_extract": (14001, "holding", 1),
                "heat_exchanger_state": (14102, "holding", 1),
                "rotor": (14350, "holding", 1),
                "heater": (2148, "holding", 1),
                "filter_replace_month": (7000, "holding", 1),
                "filter_replace_seconds": (7005, "holding", 1),
                "setpoint_eco_offset": (2503, "holding", 0.1),
                "usermode_remain_time": (1110, "holding", 1),
                "cooling_recovery_temp": (2314, "holding", 1),
                "temp_exhaust": (12105, "holding", 0.1),
                "temp_outside": (12102, "holding", 0.1),
                "rotor_rotation_speed": (14350, "holding", 1),
                "heater_percentage": (14101, "holding", 1),
                "supply_fan_speed": (14001, "holding", 1),
                "extract_fan_speed": (14002, "holding", 1),
                "filter_pressure": (12115, "holding", 1),
                "co2_level": (3001, "holding", 1),
                "sfp_supply": (12201, "holding", 1),
                "remaining_filter_time": (7005, "holding", 1),
                "defrost_level": (15022, "holding", 1),
                "exhaust_humidity": (12136, "holding", 1),
                "intake_humidity": (12137, "holding", 1),
                "supply_air_pressure": (12112, "holding", 1),
                "extract_air_pressure": (12113, "holding", 1),
                "energy_consumption": (7006, "holding", 1),
                "heat_recovery_efficiency": (12203, "holding", 1)
            }

            for name, reg_info in registers.items():
                addr, reg_type, scale = reg_info[0], reg_info[1], reg_info[2]
                value_type = reg_info[3] if len(reg_info) > 3 else "normal"

                if reg_type == "holding":
                    rr = await self.client.read_holding_registers(addr, 1, slave=SLAVE_ID)
                else:
                    rr = await self.client.read_input_registers(addr, 1, slave=SLAVE_ID)

                if rr.isError():
                    data[name] = None if value_type != "bool" else False
                else:
                    raw = rr.registers[0]
                    if value_type == "bool":
                        data[name] = raw > 0
                    else:
                        data[name] = raw * scale

            return data
        except ModbusException as err:
            _LOGGER.error("Modbus error: %s", err)
            raise UpdateFailed(err)
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            raise UpdateFailed(err)

    async def async_write_register(self, address: int, value: int, slave: int = SLAVE_ID) -> bool:
        """Async write single register."""
        try:
            await self._ensure_connected()
            wr = await asyncio.wait_for(self.client.write_register(address, value, slave=slave), timeout=3.0)
            if wr.isError():
                _LOGGER.error("Modbus write error at address %s", address)
                return False
            return True
        except asyncio.TimeoutError:
            _LOGGER.error("Modbus write timeout at address %s (no response for 3 seconds)", address)
            return False
        except ModbusException as err:
            _LOGGER.error("Modbus exception during write at address %s: %s", address, err)
            return False
        except Exception as err:
            _LOGGER.error("Unexpected error during write at address %s: %s", address, err)
            return False
