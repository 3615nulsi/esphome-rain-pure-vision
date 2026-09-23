🇫🇷 [Version française](README.md)

# 🌱 ESPHome Proxy for Rain Pure Vision 2.0 (2 zones)

Unofficial [ESPHome](https://esphome.io/) / [Home Assistant](https://www.home-assistant.io/) integration for the **Rain Pure Vision 2.0 (2-zone)** irrigation controller, controlled over Bluetooth Low Energy (BLE).

An ESP32 acts as a **proxy**: it talks to the controller over BLE and exposes its functions to Home Assistant through the native ESPHome API (Wi-Fi). A Home Assistant **blueprint** is provided to schedule watering.

---

## ⚠️ Disclaimer

**I am not a developer.** This project answers a personal need and was built with the help of AI assistants, from a reverse-engineering of the official Rain Vision app.

- It works **on my setup**, but lacks the rigor of a professional project.
- The controller's BLE protocol is **not documented**: everything comes from analyzing the official app's code and testing on a single controller.

Feedback and contributions are welcome (see [Contributing](#-contributing)).

---

## ⚡ Exclusive BLE connection

The controller accepts **only one BLE connection at a time**: while the ESP32 is connected, the official app cannot connect. To use the app, unplug the ESP32; the proxy reconnects on its own when restarted.

---

## 🔧 Proxy features

| Feature | Details |
|---|---|
| **Manual watering** | Zone and duration of your choice (1 to 60 min). The proxy waits for the BLE connection, **checks that the valve actually opened** on the right zone and retries otherwise (3 attempts) |
| **Close valve** | General "stop" button, with the same check |
| **Pause** | Suspends the programs stored in the controller (1 to 14 days), with **confirmation** read back from the controller |
| **Cancel pause** | Re-enables the controller's programs |
| **Valve state** | Open / closed, based on the zones actually active |
| **Current zone / time remaining** | Zone being watered and time remaining (in seconds) |
| **Rain sensor** | The controller's rain sensor, if fitted |
| **Pump active** | If applicable |
| **Solenoid valve faults** | Open circuit / short circuit, overall and per zone |
| **Controller flags** | Default password, firmware (FW) error, hardware (HW) error, battery charging, history full (zones 1 and 2) |
| **Stored programs** | Number of programs stored in the controller, active or disabled |
| **ACQUA sensors** | Number of sensors detected (255 = not refreshed yet) |
| **Battery** | Controller battery level |
| **BLE connection** | Connection state to the controller |
| **Clock** | Controller clock resynchronized on every connection and every NTP sync |

---

## 🗓️ Scheduling blueprint

`blueprint_rain_pure_vision_esphome_en.yaml` is a Home Assistant automation blueprint (HA ≥ 2024.10), with English texts and notifications. The original French version, with identical logic, is `blueprint_programmation_rain_pure_vision_esphome.yaml`. Import it via **Settings → Automations & scenes → Blueprints → Import blueprint**, using the file's GitHub URL.

- Waters one zone during the time slots of a schedule (Home Assistant *Schedule* helper), closes the valve at the end of the slot.
- Duration adjusted by a seasonal coefficient (`input_number` in %).
- Watering skipped on: electrical fault, controller pause, rain sensor active, **recent rainfall** (accumulation sensor, e.g. a 48 h *Statistics* helper), **forecast rain** over the next hours, soil moist enough.
- Waits for Bluetooth if the controller is temporarily unreachable.
- Opening and closing **verified** against the actual valve state, forced closing if it stays open too long.
- Notifications (start, skip with reason, end, anomalies) via `notify.send_message`.

---

## 🧰 Requirements

- An **ESP32** with Bluetooth (no ESP8266), dedicated or already used by another ESPHome device
- A **Rain Pure Vision 2.0, 2-zone** controller
- [ESPHome](https://esphome.io/), `esp-idf` framework recommended
- Home Assistant (optional for the proxy alone, required for the blueprint)

---

## 🚀 Installation

All the logic lives in **`rain_pure_vision.yaml`**, an [ESPHome package](https://esphome.io/components/packages/) downloaded from this repository at compile time.

### Option A — Existing ESPHome device

Add to its configuration:

```yaml
substitutions:
  rain_mac: "AA:BB:CC:DD:EE:FF"   # BLE MAC address of your controller
  rain_timezone: "Europe/Paris"   # optional (default value)
  rain_zones: "2"                 # optional (default value)

packages:
  rain_pure_vision:
    url: https://github.com/3615nulsi/esphome-rain-pure-vision
    ref: main
    files: [rain_pure_vision.yaml]
    refresh: 1d
```

- If the device is also a **Bluetooth proxy** (`bluetooth_proxy:`), add `max_connections: 4` under `esp32_ble:` (ESPHome flags it with a warning).
- The package adds its own SNTP clock; it coexists fine with `time: homeassistant`.
- The entities show up in Home Assistant under that device's name.

### Option B — Dedicated ESP32

1. Start from the example **`proxy_rain_vision_pure.yml`** (it already contains the `packages:` block).
2. Create a **`secrets.yaml`** next to it:
   ```yaml
   wifi_ssid: "YourSSID"
   wifi_password: "YourPassword"
   ap_fallback_password: "a_fallback_password"
   api_encryption_key: "your key (32 bytes, base64)"
   ```
   The ESPHome dashboard can generate the API key when creating a device.
3. Set **`rain_mac`** (and `rain_timezone` if needed).

### Then

- **MAC address**: find it with a BLE scanning app (nRF Connect, LightBlue…) or in the ESPHome logs.
- **Flash** the ESP32, then add it to Home Assistant via the ESPHome integration (usually auto-discovered).

### English entity names

Entities are named in French by default. For English names, add `langues/en.yaml` **after** the package in `files:`:

```yaml
    files: [rain_pure_vision.yaml, langues/en.yaml]
```

⚠️ Pick the language **at install time**: Home Assistant identifies entities by their name, so switching language later creates new entities (the old ones become unavailable and automations using them must be redone). A single name can also be overridden in the device's `substitutions:` (`rain_nom_…` keys, see the top of `rain_pure_vision.yaml`). The blueprint works whatever the entity language; it comes in English and French (see above).

### Updates

The package is downloaded again at compile time, at most once a day (`refresh: 1d`). With `ref: main`, every recompile picks up the latest version. To choose when you update, pin a published release (e.g. `ref: v1.1.0`, see the [Releases](https://github.com/3615nulsi/esphome-rain-pure-vision/releases)).

---

## 🔍 How it works

The protocol was reconstructed from the official app's JavaScript code (Ionic/Capacitor app), then checked on the hardware. A few notable points:

- The official app closes its BLE sessions after **~60 seconds**; the proxy reconnects automatically if the controller drops the connection.
- The clock is written to the controller (`TIME` characteristic) on every connection, so that dated pauses work.


---

## 🐞 Limitations

- **Tested on a single 2-zone Rain Pure Vision controller.** Behavior on other variants (more zones, other generation) is not guaranteed.
- The `STATUS_FLAG` indicators (errors, default password…) are decoded from the official app and were only checked on a 2-zone controller. 

---

## 🤝 Contributing

If you know ESPHome, C++ or BLE, an outside eye is welcome: robustness, simplification, support for other controller variants…

- **Issues**: include ESPHome logs (`DEBUG` level), the exact controller model and observed / expected behavior.
- **Pull requests**: welcome, big or small, refactors included.

---

## 📄 License

[MIT](LICENSE) — free to reuse, modify and redistribute.

---

## 🙌 Acknowledgments

The [ESPHome](https://esphome.io/) and [Home Assistant](https://www.home-assistant.io/) communities.
