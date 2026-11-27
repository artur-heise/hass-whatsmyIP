"""Polls the external IP, keeps history, writes a log file."""
from __future__ import annotations

import asyncio
import ipaddress
import logging
import os
from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    CONF_INTERVAL,
    CONF_URL,
    DOMAIN,
    HISTORY_HOURS,
    LOG_FILE,
    MAX_CHANGES,
    MAX_LOG_BYTES,
    STORAGE_VERSION,
)

_LOGGER = logging.getLogger(__name__)


def _append_log(path: str, line: str) -> None:
    """Append one line to the log file (blocking, run in executor)."""
    try:
        if os.path.exists(path) and os.path.getsize(path) > MAX_LOG_BYTES:
            os.replace(path, path + ".1")
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError as err:
        _LOGGER.warning("Cannot write %s: %s", path, err)


class ExtIPCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator holding the current IP and its history (newest first)."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(minutes=entry.data[CONF_INTERVAL]),
        )
        self._url: str = entry.data[CONF_URL]
        self._store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}")
        self._log_path = hass.config.path(LOG_FILE)
        self._readings: list[dict] = []
        self._changes: list[dict] = []
        self._last_ip: str | None = None

    async def async_load(self) -> None:
        stored = await self._store.async_load()
        if stored:
            self._readings = stored.get("readings", [])
            self._changes = stored.get("changes", [])
            self._last_ip = stored.get("last_ip")

    async def _async_update_data(self) -> dict:
        now = dt_util.utcnow()
        ts = now.isoformat(timespec="seconds")

        try:
            session = async_get_clientsession(self.hass)
            async with asyncio.timeout(15):
                resp = await session.get(self._url)
                resp.raise_for_status()
                text = (await resp.text()).strip()
            ip = str(ipaddress.ip_address(text))
        except (TimeoutError, aiohttp.ClientError, ValueError) as err:
            await self.hass.async_add_executor_job(
                _append_log, self._log_path, f"{ts} ERROR {err}"
            )
            raise UpdateFailed(f"Cannot read external IP: {err}") from err

        previous = self._last_ip
        changed = ip != previous

        self._readings.insert(0, {"ts": ts, "ip": ip})
        cutoff = now - timedelta(hours=HISTORY_HOURS)
        self._readings = [
            r
            for r in self._readings
            if (dt := dt_util.parse_datetime(r["ts"])) is not None and dt >= cutoff
        ]

        if changed:
            self._changes.insert(0, {"ts": ts, "ip": ip, "previous": previous})
            self._changes = self._changes[:MAX_CHANGES]
            self._last_ip = ip
            _LOGGER.info("External IP changed: %s -> %s", previous, ip)
            line = f"{ts} CHANGED {ip} (was {previous or 'n/a'})"
        else:
            line = f"{ts} OK {ip}"

        await self.hass.async_add_executor_job(_append_log, self._log_path, line)
        await self._store.async_save(
            {
                "readings": self._readings,
                "changes": self._changes,
                "last_ip": self._last_ip,
            }
        )

        return {
            "ip": ip,
            "readings": list(self._readings),
            "changes": list(self._changes),
        }
