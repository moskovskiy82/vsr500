"""The Systemair SAVE VSR integration."""
from __future__ import annotations

import logging
import asyncio
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
        if hub.client is not None:  # Check for None before closing
            hub.client.close()  # Close without await
    return unload_ok

# async def async_get_device_diagnostics(
#     hass: HomeAssistant, entry: ConfigEntry, device: dr.DeviceEntry
# ) -> dict:
#     hub: SAVEVSRHub = hass.data[DOMAIN][entry.entry_id]
#     data = hub.coordinator.data or {}
#     diagnostics = {
#         "alarm_typeA": data.get("alarm_typeA", False),
#         "alarm_typeB": data.get("alarm_typeB", False),
#         "alarm_typeC": data.get("alarm_typeC", False),
#     }
#     return diagnostics

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
            config_entry=entry,
            update_method=self._async_update_data,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )
        self._lock = asyncio.Lock()

    @property
    def device_info(self) -> dr.DeviceInfo:
        return self._device_info

    async def _ensure_connected(self) -> None:
        """Connect client if not connected."""
        if self.client is None:
            _LOGGER.error("Modbus client is None, reinitializing")
            self.client = AsyncModbusSerialClient(
                port=self.entry.data["port"],
                baudrate=self.entry.data["baudrate"],
                stopbits=self.entry.data["stopbits"],
                bytesize=self.entry.data["bytesize"],
                parity=self.entry.data["parity"],
            )
        if not self.client.connected:
            _LOGGER.debug("Connecting to Systemair SAVE VSR Modbus RTU...")
            try:
                connected = await asyncio.wait_for(self.client.connect(), timeout=5.0)
                if not connected:
                    _LOGGER.error("Failed to connect to Systemair SAVE VSR")
                    raise UpdateFailed("Failed to connect to Systemair SAVE VSR")
            except asyncio.TimeoutError:
                _LOGGER.error("Timeout connecting to Systemair SAVE VSR")
                raise UpdateFailed("Timeout connecting to Systemair SAVE VSR")
            except Exception as err:
                _LOGGER.error("Unexpected error connecting to Systemair SAVE VSR: %s", err)
                raise UpdateFailed(f"Unexpected error connecting: {err}")

    async def _async_update_data(self) -> dict:
        """Fetch data from the VSR unit."""
        # Serialize updates to one at a time
        async with self._lock:
            try:
                await self._ensure_connected()
                data = {}
                
                # Batch read registers where possible to reduce communication overhead
                register_batches = [
                    # Climate (input registers)
                    {"type": "input", "start": 1160, "count": 1, "keys": ["mode_main"], "scales": [1]},
                    {"type": "input", "start": 12102, "count": 1, "keys": ["temp_supply"], "scales": [0.1]},
                    # Climate (holding registers)
                    {"type": "holding", "start": 1130, "count": 1, "keys": ["mode_speed"], "scales": [1]},
                    {"type": "holding", "start": 2000, "count": 1, "keys": ["target_temp"], "scales": [0.1]},
                    # Binary sensors and switches
                    {"type": "holding", "start": 1038, "count": 1, "keys": ["mode_summerwinter"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 1350, "count": 2, "keys": ["fan_running", "cooldown"], "scales": [1, 1], "bool": True},
                    {"type": "holding", "start": 14003, "count": 1, "keys": ["damper_state"], "scales": [1], "bool": True},

                    {"type": "holding", "start": 2133, "count": 1, "keys": ["cooling_recovery"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 2504, "count": 1, "keys": ["eco_modus"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 3001, "count": 1, "keys": ["heater_switch"], "scales": [1], "bool": True},
                    # Alarms (batched where possible)
                    {"type": "holding", "start": 15001, "count": 1, "keys": ["alarm_saf"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15008, "count": 1, "keys": ["alarm_eaf"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15015, "count": 8, "keys": ["alarm_frost_protect", None, None, None, None, None, None, "alarm_defrosting"], "scales": [1]*8, "bool": True},
                    {"type": "holding", "start": 15029, "count": 1, "keys": ["alarm_saf_rpm"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15036, "count": 1, "keys": ["alarm_eaf_rpm"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15057, "count": 1, "keys": ["alarm_fpt"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15064, "count": 1, "keys": ["alarm_oat"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15071, "count": 1, "keys": ["alarm_sat"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15078, "count": 1, "keys": ["alarm_rat"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15085, "count": 1, "keys": ["alarm_eat"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15092, "count": 1, "keys": ["alarm_ect"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15099, "count": 1, "keys": ["alarm_eft"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15106, "count": 1, "keys": ["alarm_oht"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15113, "count": 1, "keys": ["alarm_emt"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15127, "count": 1, "keys": ["alarm_bys"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15134, "count": 1, "keys": ["alarm_sec_air"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15141, "count": 1, "keys": ["alarm_filter"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15162, "count": 1, "keys": ["alarm_rh"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15176, "count": 1, "keys": ["alarm_low_SAT"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15508, "count": 1, "keys": ["alarm_pdm_rhs"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15515, "count": 1, "keys": ["alarm_pdm_eat"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15522, "count": 1, "keys": ["alarm_man_fan_stop"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15529, "count": 1, "keys": ["alarm_overheat_temp"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15536, "count": 1, "keys": ["alarm_fire"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15543, "count": 1, "keys": ["alarm_filter_warn"], "scales": [1], "bool": True},
                    {"type": "holding", "start": 15900, "count": 3, "keys": ["alarm_typeA", "alarm_typeB", "alarm_typeC"], "scales": [1, 1, 1], "bool": True},
                    # Sensors

                    {"type": "holding", "start": 1110, "count": 1, "keys": ["usermode_remain_time"], "scales": [1]},

                    {"type": "holding", "start": 7005, "count": 1, "keys": ["filter_replace_seconds"], "scales": [1]},

                    {"type": "holding", "start": 12101, "count": 2, "keys": ["temp_outdoor", "temp_supply"], "scales": [0.1, 0.1]},
                    {"type": "holding", "start": 12105, "count": 1, "keys": ["temp_exhaust"], "scales": [0.1]},
                    {"type": "holding", "start": 12542, "count": 1, "keys": ["temp_extract"], "scales": [0.1]},

                    {"type": "holding", "start": 12107, "count": 1, "keys": ["temp_overheat"], "scales": [0.1]},
                    {"type": "holding", "start": 12112, "count": 2, "keys": ["supply_air_pressure", "extract_air_pressure"], "scales": [1, 1]},


                    {"type": "holding", "start": 12201, "count": 1, "keys": ["sfp_supply"], "scales": [1]},
                    {"type": "holding", "start": 12203, "count": 1, "keys": ["heat_recovery_efficiency"], "scales": [1]},
                    {"type": "holding", "start": 12400, "count": 2, "keys": ["saf_rpm", "eaf_rpm"], "scales": [1, 1]},

                    {"type": "holding", "start": 14000, "count": 2, "keys": ["fan_supply", "fan_extract"], "scales": [1, 1]},
                    {"type": "holding", "start": 14001, "count": 2, "keys": ["supply_fan_speed", "extract_fan_speed"], "scales": [1, 1]},
                    {"type": "holding", "start": 14101, "count": 1, "keys": ["heater_percentage"], "scales": [1]},
                    {"type": "holding", "start": 14102, "count": 1, "keys": ["heat_exchanger_state"], "scales": [1]},
                    {"type": "holding", "start": 14350, "count": 1, "keys": ["rotor"], "scales": [1]},
                    {"type": "holding", "start": 2148, "count": 1, "keys": ["heater"], "scales": [1]},

                    {"type": "holding", "start": 2314, "count": 1, "keys": ["cooling_recovery_temp"], "scales": [1]},
                    {"type": "holding", "start": 2503, "count": 1, "keys": ["setpoint_eco_offset"], "scales": [0.1]},


                ]

                async def read_with_retry(addr, count, reg_type, max_retries=2):
                    for attempt in range(max_retries):
                        try:
                            if reg_type == "holding":
                                rr = await asyncio.wait_for(
                                    self.client.read_holding_registers(addr, count, slave=SLAVE_ID),
                                    timeout=3.0
                                )
                            else:
                                rr = await asyncio.wait_for(
                                    self.client.read_input_registers(addr, count, slave=SLAVE_ID),
                                    timeout=3.0
                                )
                            if rr.isError() or not rr.registers or len(rr.registers) < count:
                                _LOGGER.warning("Failed to read %s registers at %s (attempt %s/%s)", reg_type, addr, attempt + 1, max_retries)
                                if attempt + 1 < max_retries:
                                    await asyncio.sleep(0.5)
                                continue
                            return rr.registers
                        except asyncio.TimeoutError:
                            _LOGGER.warning("Timeout reading %s registers at %s (attempt %s/%s)", reg_type, addr, attempt + 1, max_retries)
                            if attempt + 1 < max_retries:
                                await asyncio.sleep(0.5)
                        except ModbusException as err:
                            _LOGGER.warning("Modbus error reading %s registers at %s (attempt %s/%s): %s", reg_type, addr, attempt + 1, max_retries, err)
                            if attempt + 1 < max_retries:
                                await asyncio.sleep(0.5)
                        except Exception as err:
                            _LOGGER.warning("Unexpected error reading %s registers at %s (attempt %s/%s): %s", reg_type, addr, attempt + 1, max_retries, err)
                            if attempt + 1 < max_retries:
                                await asyncio.sleep(0.5)
                    return None

                for batch in register_batches:
                    reg_type = batch["type"]
                    addr = batch["start"]
                    count = batch["count"]
                    keys = batch["keys"]
                    scales = batch["scales"]
                    is_bool = batch.get("bool", False)

                    registers = await read_with_retry(addr, count, reg_type)
                    if registers is None:
                        for key in keys:
                            if key:
                                data[key] = False if is_bool else None
                        continue

                    for i, (key, scale) in enumerate(zip(keys, scales)):
                        if key and i < len(registers):
                            try:
                                raw = registers[i]
                                data[key] = (raw > 0) if is_bool else (raw * scale)
                            except (IndexError, TypeError):
                                _LOGGER.warning("Invalid data for key %s at register %s", key, addr + i)
                                data[key] = False if is_bool else None

                return data
            except ModbusException as err:
                _LOGGER.error("Modbus error during update: %s", err)
                raise UpdateFailed(f"Modbus error: {err}")
            except Exception as err:
                _LOGGER.error("Unexpected error during update: %s", err)
                raise UpdateFailed(f"Unexpected error: {err}")
            finally:
                if self.client is not None:
                    try:
                        self.client.close()
                    except Exception as err:
                        _LOGGER.warning("Error closing Modbus client: %s", err)

    async def async_write_register(self, address: int, value: int, slave: int = SLAVE_ID) -> bool:
        """Async write single register."""
        async with self._lock:
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