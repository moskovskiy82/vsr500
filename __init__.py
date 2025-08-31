"""The Systemair SAVE VSR integration."""
from __future__ import annotations

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

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.BINARY_SENSOR, Platform.SENSOR, Platform.SWITCH]

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
        await hub.client.close()
    return unload_ok

async def async_get_device_diagnostics(hass: HomeAssistant, entry: ConfigEntry, device: dr.DeviceEntry) -> dict:
    hub: SAVEVSRHub = hass.data[DOMAIN][entry.entry_id]
    data = hub.coordinator.data or {}
    diagnostics = {
        "alarm_typeA": data.get("alarm_typeA", False),
        "alarm_typeB": data.get("alarm_typeB", False),
        "alarm_typeC": data.get("alarm_typeC", False),
        "alarm_saf": data.get("alarm_saf", False),
        "alarm_fire": data.get("alarm_fire", False),
        "alarm_eaf": data.get("alarm_eaf", False),
        "alarm_saf_rpm": data.get("alarm_saf_rpm", False),
        "alarm_eaf_rpm": data.get("alarm_eaf_rpm", False),
        "alarm_fpt": data.get("alarm_fpt", False),
        "alarm_oat": data.get("alarm_oat", False),
        "alarm_sat": data.get("alarm_sat", False),
        "alarm_rat": data.get("alarm_rat", False),
        "alarm_eat": data.get("alarm_eat", False),
        "alarm_ect": data.get("alarm_ect", False),
        "alarm_eft": data.get("alarm_eft", False),
        "alarm_oht": data.get("alarm_oht", False),
        "alarm_emt": data.get("alarm_emt", False),
        "alarm_bys": data.get("alarm_bys", False),
        "alarm_sec_air": data.get("alarm_sec_air", False),
        "alarm_rh": data.get("alarm_rh", False),
        "alarm_frost_protect": data.get("alarm_frost_protect", False),
        "alarm_defrosting": data.get("alarm_defrosting", False),
        "alarm_low_SAT": data.get("alarm_low_SAT", False),
        "alarm_pdm_rhs": data.get("alarm_pdm_rhs", False),
        "alarm_pdm_eat": data.get("alarm_pdm_eat", False),
        "alarm_man_fan_stop": data.get("alarm_man_fan_stop", False),
        "alarm_overheat_temp": data.get("alarm_overheat_temp", False),
        "alarm_filter": data.get("alarm_filter", False),
        "alarm_filter_warn": data.get("alarm_filter_warn", False),
        # Add more alarms if needed
    }
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

    async def _async_update_data(self) -> dict:
        async def update_data():
            data = {}
            try:
                await self._ensure_connected()
                # Climate
                rr = await self.client.read_input_registers(12102, 1, slave=SLAVE_ID)
                data["temp_supply"] = rr.registers[0] * 0.1 if not rr.isError() else None
                rr = await self.client.read_holding_registers(2000, 1, slave=SLAVE_ID)
                data["target_temp"] = rr.registers[0] * 0.1 if not rr.isError() else None
                rr = await self.client.read_input_registers(1160, 1, slave=SLAVE_ID)
                data["mode_main"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(1130, 1, slave=SLAVE_ID)
                data["mode_speed"] = rr.registers[0] if not rr.isError() else None
                # Binary sensors (operational)
                rr = await self.client.read_holding_registers(14003, 1, slave=SLAVE_ID)
                data["damper_state"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(1351, 1, slave=SLAVE_ID)
                data["cooldown"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(2146, 1, slave=SLAVE_ID)
                data["humidity_return"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(2203, 1, slave=SLAVE_ID)
                data["humidity_transfer_enabled"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(1038, 1, slave=SLAVE_ID)
                data["mode_summerwinter"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(1350, 1, slave=SLAVE_ID)
                data["fan_running"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(2133, 1, slave=SLAVE_ID)
                data["cooling_recovery"] = rr.registers[0] > 0 if not rr.isError() else False
                # Alarms (for diagnostics)
                rr = await self.client.read_holding_registers(15900, 1, slave=SLAVE_ID)
                data["alarm_typeA"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15901, 1, slave=SLAVE_ID)
                data["alarm_typeB"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15902, 1, slave=SLAVE_ID)
                data["alarm_typeC"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15001, 1, slave=SLAVE_ID)
                data["alarm_saf"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15536, 1, slave=SLAVE_ID)
                data["alarm_fire"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15008, 1, slave=SLAVE_ID)
                data["alarm_eaf"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15029, 1, slave=SLAVE_ID)
                data["alarm_saf_rpm"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15036, 1, slave=SLAVE_ID)
                data["alarm_eaf_rpm"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15057, 1, slave=SLAVE_ID)
                data["alarm_fpt"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15064, 1, slave=SLAVE_ID)
                data["alarm_oat"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15071, 1, slave=SLAVE_ID)
                data["alarm_sat"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15078, 1, slave=SLAVE_ID)
                data["alarm_rat"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15085, 1, slave=SLAVE_ID)
                data["alarm_eat"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15092, 1, slave=SLAVE_ID)
                data["alarm_ect"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15099, 1, slave=SLAVE_ID)
                data["alarm_eft"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15106, 1, slave=SLAVE_ID)
                data["alarm_oht"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15113, 1, slave=SLAVE_ID)
                data["alarm_emt"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15127, 1, slave=SLAVE_ID)
                data["alarm_bys"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15134, 1, slave=SLAVE_ID)
                data["alarm_sec_air"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15162, 1, slave=SLAVE_ID)
                data["alarm_rh"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15015, 1, slave=SLAVE_ID)
                data["alarm_frost_protect"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15022, 1, slave=SLAVE_ID)
                data["alarm_defrosting"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15176, 1, slave=SLAVE_ID)
                data["alarm_low_SAT"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15508, 1, slave=SLAVE_ID)
                data["alarm_pdm_rhs"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15515, 1, slave=SLAVE_ID)
                data["alarm_pdm_eat"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15522, 1, slave=SLAVE_ID)
                data["alarm_man_fan_stop"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15529, 1, slave=SLAVE_ID)
                data["alarm_overheat_temp"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15141, 1, slave=SLAVE_ID)
                data["alarm_filter"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(15543, 1, slave=SLAVE_ID)
                data["alarm_filter_warn"] = rr.registers[0] > 0 if not rr.isError() else False
                # Sensors
                rr = await self.client.read_holding_registers(1161, 1, slave=SLAVE_ID)
                data["test_mode_reg"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(12402, 1, slave=SLAVE_ID)
                data["sensor_flow_piggyback_saf"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(12403, 1, slave=SLAVE_ID)
                data["sensor_flow_piggyback_eaf"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(1130, 1, slave=SLAVE_ID)
                data["mode_speed"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(1160, 1, slave=SLAVE_ID)
                data["mode_main"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(12101, 1, slave=SLAVE_ID)
                data["temp_outdoor"] = rr.registers[0] * 0.1 if not rr.isError() else None
                rr = await self.client.read_holding_registers(12102, 1, slave=SLAVE_ID)
                data["temp_supply"] = rr.registers[0] * 0.1 if not rr.isError() else None
                rr = await self.client.read_holding_registers(12543, 1, slave=SLAVE_ID)
                data["temp_extract"] = rr.registers[0] * 0.1 if not rr.isError() else None
                rr = await self.client.read_holding_registers(12107, 1, slave=SLAVE_ID)
                data["temp_overheat"] = rr.registers[0] * 0.1 if not rr.isError() else None
                rr = await self.client.read_holding_registers(12135, 1, slave=SLAVE_ID)
                data["humidity"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(2210, 1, slave=SLAVE_ID)
                data["humidity_exhaust"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(2211, 1, slave=SLAVE_ID)
                data["humidity_intake"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(2202, 1, slave=SLAVE_ID)
                data["setpoint_RH_transfer"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(2200, 1, slave=SLAVE_ID)
                data["humidity_return_value"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(12400, 1, slave=SLAVE_ID)
                data["saf_rpm"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(12401, 1, slave=SLAVE_ID)
                data["eaf_rpm"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(14000, 1, slave=SLAVE_ID)
                data["fan_supply"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(14001, 1, slave=SLAVE_ID)
                data["fan_extract"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(14102, 1, slave=SLAVE_ID)
                data["heat_exchanger_state"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(14350, 1, slave=SLAVE_ID)
                data["rotor"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(2148, 1, slave=SLAVE_ID)
                data["heater"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(7000, 1, slave=SLAVE_ID)
                data["filter_replace_month"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(7005, 1, slave=SLAVE_ID)
                data["filter_replace_seconds"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(2503, 1, slave=SLAVE_ID)
                data["setpoint_eco_offset"] = rr.registers[0] * 0.1 if not rr.isError() else None
                rr = await self.client.read_holding_registers(1110, 1, slave=SLAVE_ID)
                data["usermode_remain_time"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(2314, 1, slave=SLAVE_ID)
                data["cooling_recovery_temp"] = rr.registers[0] if not rr.isError() else None
                # Added sensors
                rr = await self.client.read_holding_registers(12105, 1, slave=SLAVE_ID)
                data["temp_exhaust"] = rr.registers[0] * 0.1 if not rr.isError() else None
                rr = await self.client.read_holding_registers(12102, 1, slave=SLAVE_ID)
                data["temp_outside"] = rr.registers[0] * 0.1 if not rr.isError() else None
                rr = await self.client.read_holding_registers(14350, 1, slave=SLAVE_ID)
                data["rotor_rotation_speed"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(14101, 1, slave=SLAVE_ID)
                data["heater_percentage"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(14001, 1, slave=SLAVE_ID)
                data["supply_fan_speed"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(14002, 1, slave=SLAVE_ID)
                data["extract_fan_speed"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(12115, 1, slave=SLAVE_ID)
                data["filter_pressure"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(3001, 1, slave=SLAVE_ID)
                data["co2_level"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(12201, 1, slave=SLAVE_ID)
                data["sfp_supply"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(7005, 1, slave=SLAVE_ID)
                data["remaining_filter_time"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(15022, 1, slave=SLAVE_ID)
                data["defrost_level"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(12136, 1, slave=SLAVE_ID)
                data["exhaust_humidity"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(12137, 1, slave=SLAVE_ID)
                data["intake_humidity"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(12112, 1, slave=SLAVE_ID)
                data["supply_air_pressure"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(12113, 1, slave=SLAVE_ID)
                data["extract_air_pressure"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(7006, 1, slave=SLAVE_ID)
                data["energy_consumption"] = rr.registers[0] if not rr.isError() else None
                rr = await self.client.read_holding_registers(12203, 1, slave=SLAVE_ID)
                data["heat_recovery_efficiency"] = rr.registers[0] if not rr.isError() else None
                # Switches
                rr = await self.client.read_holding_registers(2504, 1, slave=SLAVE_ID)
                data["eco_modus"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(3001, 1, slave=SLAVE_ID)
                data["heater_switch"] = rr.registers[0] > 0 if not rr.isError() else False
                rr = await self.client.read_holding_registers(2146, 1, slave=SLAVE_ID)
                data["rh_switch"] = rr.registers[0] > 0 if not rr.isError() else False
                return data
            finally:
                await self.client.close()

        return await update_data()

    async def _ensure_connected(self) -> None:
        if not self.client.connected:
            _LOGGER.debug("Connecting to Systemair SAVE VSR Modbus RTU...")
            connected = await self.client.connect()
            if not connected:
                raise UpdateFailed("Failed to connect to Systemair SAVE VSR")

    async def async_write_register(self, address: int, value: int, slave: int = SLAVE_ID) -> bool:
        """Async write single register."""
        try:
            await self._ensure_connected()
            wr = await self.client.write_register(address, value, slave=slave)
            return not wr.isError()
        except Exception as err:
            _LOGGER.error("Write failed (addr=%s, val=%s): %s", address, value, err)
            return False
