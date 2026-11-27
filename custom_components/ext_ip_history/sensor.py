"""External IP sensor."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import ExtIPCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([ExtIPSensor(entry.runtime_data, entry)])


class ExtIPSensor(CoordinatorEntity[ExtIPCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "External IP"
    _attr_icon = "mdi:ip-network"
    # Keep the big tables out of the recorder database
    _unrecorded_attributes = frozenset({"readings_24h", "changes"})

    def __init__(self, coordinator: ExtIPCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_external_ip"

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data["ip"]

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data
        changes = data["changes"]
        return {
            "last_change": changes[0]["ts"] if changes else None,
            "previous_ip": changes[0]["previous"] if changes else None,
            "readings_24h": data["readings"],
            "changes": changes,
        }
