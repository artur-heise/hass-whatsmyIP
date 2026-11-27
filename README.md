# External IP History for Home Assistant

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=artur-heise&repository=ext-ip-history&category=integration)

Polls your external IP address (default every 60 minutes), keeps a history, and writes a log file.

- `sensor.external_ip` – current external IP
- attribute `readings_24h` – all readings from the last 24 hours (newest first)
- attribute `changes` – last 50 IP changes with the previous address (newest first)
- log file `ext_ip_history.log` in the HA config folder (rotates at ~1 MB)

## Install via HACS

1. Click the badge above (or in HACS: ⋮ → **Custom repositories** → add
   `https://github.com/artur-heise/ext-ip-history`, type **Integration**).
2. Click **Download**, then restart Home Assistant.
3. **Settings → Devices & Services → Add Integration → External IP History**.
   Set the URL (default `https://myexternalip.com/raw`, must return the IP as plain text) and the interval.

## Dashboard tables

Add a Manual card with the contents of [`examples/dashboard_cards.yaml`](examples/dashboard_cards.yaml).
If your entity is not called `sensor.external_ip`, change it in the YAML.

## Log format

```
2026-11-27T10:00:00+00:00 OK 203.0.113.7
2026-11-27T11:00:00+00:00 CHANGED 198.51.100.4 (was 203.0.113.7)
2026-11-27T12:00:00+00:00 ERROR Cannot connect to host ...
```

## Author

Artur Heise – <https://github.com/artur-heise/>
