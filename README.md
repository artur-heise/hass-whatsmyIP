# External IP History for Home Assistant

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=artur-heise&repository=hass-whatsmyIP&category=integration)

Polls your external IP address (default every 60 minutes), keeps a history, and writes a log file.

- `sensor.external_ip` – current external IP
- attribute `readings_24h` – all readings from the last 24 hours (newest first)
- attribute `changes` – last 50 IP changes with the previous address (newest first)
- attributes `previous_ip` and `last_change` – the most recent change
- log file `ext_ip_history.log` in the HA config folder (rotates at ~1 MB)

## Install via HACS

1. Click the badge above (or in HACS: ⋮ → **Custom repositories** → add
   `https://github.com/artur-heise/hass-whatsmyIP`, type **Integration**).
2. Click **Download**, then restart Home Assistant.
3. **Settings → Devices & Services → Add Integration → External IP History**.
   Set the URL (default `https://myexternalip.com/raw`, must return the IP as plain text) and the interval.

## Displaying the attributes

If your sensor is not called `sensor.external_ip`, replace the name in all YAML below.
You can check it under **Developer Tools → States**.

### 1. The two tables

`readings_24h` and `changes` are lists, so a Markdown card is what renders them as tables.
Add it with **Edit dashboard → Add card → Manual** (also available as
[`examples/dashboard_cards.yaml`](examples/dashboard_cards.yaml)):

```yaml
type: vertical-stack
cards:
  - type: markdown
    title: External IP – last 24 h
    content: |
      **Current:** `{{ states('sensor.external_ip') }}`

      | Time | IP |
      |---|---|
      {% for r in state_attr('sensor.external_ip', 'readings_24h') or [] -%}
      | {{ as_timestamp(r.ts) | timestamp_custom('%d.%m %H:%M') }} | {{ r.ip }} |
      {% endfor %}
  - type: markdown
    title: Last 50 IP changes
    content: |
      | When | New IP | Previous IP |
      |---|---|---|
      {% for r in state_attr('sensor.external_ip', 'changes') or [] -%}
      | {{ as_timestamp(r.ts) | timestamp_custom('%d.%m.%Y %H:%M') }} | {{ r.ip }} | {{ r.previous or '—' }} |
      {% endfor %}
```

To show the tables side by side instead of stacked, change `type: vertical-stack` to `type: horizontal-stack`.

### 2. A full-screen panel in the sidebar

1. **Settings → Dashboards → Add dashboard → New dashboard from scratch.** Give it a title and an icon, and keep **Show in sidebar** on.
2. Open the new dashboard, click the pencil, then the view's settings, and set the view type to **Panel (1 card)**.
3. Add the stacked or side-by-side Markdown card from section 1 as the view's only card. It then fills the whole screen.

### 3. Single-value attributes as rows

`previous_ip` and `last_change` work well in an entities card:

```yaml
type: entities
title: External IP
entities:
  - entity: sensor.external_ip
    name: Current IP
  - type: attribute
    entity: sensor.external_ip
    attribute: previous_ip
    name: Previous IP
  - type: attribute
    entity: sensor.external_ip
    attribute: last_change
    name: Last change
    format: datetime
```

Do not use this for `readings_24h` and `changes`: an attribute row would show them as a raw blob of text.

## Log format

```
2026-11-27T10:00:00+00:00 OK 203.0.113.7
2026-11-27T11:00:00+00:00 CHANGED 198.51.100.4 (was 203.0.113.7)
2026-11-27T12:00:00+00:00 ERROR Cannot connect to host ...
```

## Author

Artur Heise – <https://github.com/artur-heise/>
