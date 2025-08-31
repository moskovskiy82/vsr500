"""Config flow for Systemair SAVE VSR integration."""
from __future__ import annotations

import logging

from homeassistant import config_entries
from homeassistant.helpers import selector
from pymodbus.client import ModbusSerialClient as ModbusClient
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("port", default="/dev/ttyUSB0"): str,
        vol.Required("baudrate", default=9600): selector.NumberSelector(
            selector.NumberSelectorConfig(min=9600, max=19200, step=9600, mode=selector.NumberSelectorMode.BOX)
        ),
        vol.Required("stopbits", default=1): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1, max=2, step=1, mode=selector.NumberSelectorMode.BOX)
        ),
        vol.Required("bytesize", default=8): selector.NumberSelector(
            selector.NumberSelectorConfig(min=5, max=8, step=1, mode=selector.NumberSelectorMode.BOX)
        ),
        vol.Required("parity", default="N"): selector.SelectSelector(
            selector.SelectSelectorConfig(options=["N", "E", "O"], mode=selector.SelectSelectorMode.DROPDOWN)
        ),
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Systemair SAVE VSR."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            client = ModbusClient(
                port=user_input["port"],
                baudrate=user_input["baudrate"],
                stopbits=user_input["stopbits"],
                bytesize=user_input["bytesize"],
                parity=user_input["parity"],
                method="rtu",
            )
            try:
                if await self.hass.async_add_executor_job(client.connect):
                    await self.hass.async_add_executor_job(client.close)
                    return self.async_create_entry(title="Systemair SAVE VSR Ventilation", data=user_input)
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Connection test failed")
                errors["base"] = "unknown"

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)
