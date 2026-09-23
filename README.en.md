🇫🇷 [Version française](README.md)

# 🌱 ESPHome Proxy for Rain Pure Vision 2.0 Irrigation Controller (2 zones)

Unofficial [ESPHome](https://esphome.io/) / [Home Assistant](https://www.home-assistant.io/) integration for the **Rain Pure Vision 2.0 (2-zone)** irrigation controller, controlled over Bluetooth LE (BLE).

An ESP32 acts as a **proxy**: it maintains the BLE connection to the controller and exposes all the useful functions to Home Assistant through the native ESPHome API (WiFi).

---

## ⚠️ Important disclaimer — please read before using

**I am not a developer and I don't know how to code.** This project came out of a personal need (my Rain Pure Vision controller had no available integration) and was built with the help of several tools and iterative testing.

Concretely, this means:
- The code works **on my own setup**, tested and validated after several rounds of debugging, but it probably doesn't have the rigor, robustness, or elegance a professional developer would have produced.
- I'm not able to explain or justify every line of code in depth — I can vouch for what was observed and tested, not guarantee the correctness of every implementation detail.
- The controller's BLE protocol is **not officially documented**: everything described here comes from analyzing the decompiled JavaScript code of the official app, complemented by empirical testing.

**If you're a developer and you spot bugs, rough edges, or cleaner ways of doing things (better error handling, YAML structuring, BLE connection reliability, etc.), your help is genuinely welcome.**

---

## ⚡ Important note: exclusive BLE connection

**When the ESP32 is connected to the controller over BLE, the controller is no longer accessible via the official Rain Pure Vision app.** The controller only allows a single BLE connection at a time. You may therefore temporarily lose access from the official app while the proxy is connected.

**This is precisely why a Home Assistant blueprint is provided**: scheduling and managing watering programs is much more convenient via Home Assistant and the ESPHome proxy than via the official application, and the blueprint helps avoid conflicts between the two control paths.

---

## 🔧 Features

| Feature | Details |
|---|---|
| **Manual watering** | Start a cycle on the zone and duration of your choice (1 to 60 min) |
| **Close valve immediately** | General "stop" button, all zones |
| **Scheduled pause** | Suspends automatic programs for an adjustable duration (1 to 14 days), with **real confirmation** that the controller actually registered the pause (not just an optimistic local state) |
| **Cancel pause** | Re-enables automatic programs |
| **Valve state** (open/closed) | Derived from the real state of active zones |
| **Currently watering zone** | Number of the active zone during a cycle |
| **Time remaining** | Time remaining on the current cycle (in seconds) |
| **Rain sensor** | State of the controller's rain sensor, if fitted |
| **Pump active** | Detects pump activation (if applicable) |
| **Valve faults** | Detects open-circuit / short-circuit faults on the solenoid valves, overall and per zone |
| **Controller status flags** | Default password not changed, firmware (FW) error, hardware (HW) error, battery charging, watering history full (zones 1 and 2) |
| **ACQUA sensors** | Number of ACQUA sensors detected by the controller (255 = value not refreshed yet) |
| **Battery** | Controller's battery level |
| **BLE connection** | Binary sensor showing real-time connection status |
| **Time sync** | The controller's clock is automatically resynced on every connection and every NTP sync |

All these entities are natively exposed to Home Assistant through the ESPHome integration — no extra configuration needed on the HA side.

---

## 🧰 Hardware requirements

- An **ESP32** board (any basic dev board works), either dedicated or already used by another ESPHome device
- A **Rain Pure Vision 2.0, 2-zone** controller
- [ESPHome](https://esphome.io/) (latest version recommended, `esp-idf` framework)
- Home Assistant, if you want to use the entities (not strictly required — the ESPHome API also works standalone)

---

## 🚀 Installation

All the logic lives in **`rain_pure_vision.yaml`**, an [ESPHome package](https://esphome.io/components/packages/) that your device downloads straight from this GitHub repository on every compile. Two ways to use it:

### Option A — Add the Rain Pure Vision to an existing ESPHome device

If you already have an ESP32 running ESPHome (sensor, Bluetooth proxy...), just add these lines to its configuration:

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

Things to keep in mind:
- The device must be an **ESP32** with Bluetooth (no ESP8266). The `esp-idf` framework is recommended: BLE + Wi-Fi use a lot of memory, especially on an already busy device.
- If the device is also a **Bluetooth proxy** (`bluetooth_proxy:`), the controller uses one extra BLE connection slot. ESPHome will then show a warning: add `max_connections: 4` under `esp32_ble:`.
- The package adds its own SNTP clock (used to set the controller's time), even if the device already has `time: homeassistant`: both coexist without any problem.
- The entities will show up in Home Assistant under that device's name.

### Option B — A dedicated ESP32

1. Start from the example file **`proxy_rain_vision_pure.yml`** (it already contains the `packages:` block above).

2. **Create a `secrets.yaml` file** next to the YAML file, with:
   ```yaml
   wifi_ssid: "YourSSID"
   wifi_password: "YourPassword"
   ap_fallback_password: "a_fallback_password"
   api_encryption_key: "generate a new secret key of your own"
   ```
   To generate a valid API encryption key (32 bytes, base64-encoded), you can use the ESPHome CLI's `esphome secrets` command, or simply let the ESPHome dashboard generate one automatically when creating the device.

3. **Set `rain_mac`** (and `rain_timezone` if needed) in the `substitutions:` block.

### In both cases

- **Controller MAC address**: you can find it with a BLE scanning app (nRF Connect, LightBlue...) by looking for the device matching your Rain Pure Vision, or by letting ESPHome log the device during a discovery scan.
- **Number of zones**: `rain_zones: "2"` corresponds to a 2-zone controller. A controller with more zones hasn't been tested — see the Limitations section.
- **Flash** your ESP32 via ESPHome (CLI, dashboard, or VS Code + ESPHome extension), then add the device to Home Assistant via the ESPHome integration (auto-discovery normally, or manual add by IP otherwise).

### Updates

The package is downloaded again at compile time, at most once a day (`refresh: 1d`): recompiling the device (for instance when updating ESPHome) automatically picks up the latest version. With `ref: main`, you follow the development version. For an irrigation system, you may prefer to pin a published release (e.g. `ref: v1.0.0`, see the repository's *Releases*) and change it when you decide to.

> **Were you using the old all-in-one file?** Replace it with the new `proxy_rain_vision_pure.yml`, keeping the same device name (`proxy-arrosage`): entity names haven't changed, so Home Assistant and the blueprint will keep working without any change.

---

## 🔍 How it works (for the curious)

Since the Rain Pure Vision's BLE protocol isn't documented, this project relies on reverse-engineering the official app's JavaScript code (decompiled from the Ionic/Capacitor app bundle). A few key observations:

- The controller deliberately limits every BLE session to **~60 seconds** (`DisconnectTimer = 60000` in the app's code) — this is not a bug in the proxy, it's intentional firmware behavior. The proxy copes with that by re-establishing connections as needed.
- The current cycle's duration field (`CURR_ZONE_LASTING_TIME`) is expressed in **seconds**, not minutes despite what its name suggests — confirmed empirically by comparing the counter's decrease during a run.
- The clock needs to be periodically rewritten to the controller (`TIME` characteristic) for dated pauses and certain cycles to work correctly.
- The "manual watering" command frame (`MANUAL`) is 64 bytes long (2 bytes per zone, up to 32 zones), even though the controller only handles 2.

---

## 🐞 Known limitations / areas of uncertainty

- **Tested on a single 2-zone Rain Pure Vision controller only.** Behavior on other variants (more zones, other generation) is not guaranteed.
- The exact UUID for the `TIME` characteristic (`0200F004`) was inferred by analogy with other characteristics in the same service, but couldn't be confirmed line-by-line in the source code (the codebase is minified/obfuscated).
- The `STATUS_FLAG` bits (hardware errors, default password not changed, etc.) are decoded based on the official app's `UIntToStatus` function. Their position may vary by controller model and has only been checked on a 2-zone controller. The "history full" flags for zones 3 to 5 are not exposed.
- The 60-second disconnect cycle can occasionally delay a state update (e.g., right after a pause), without preventing normal operation.

---

## 🙏 Calling all developers

If you know ESPHome, C++, or the BLE protocol, this project clearly needs a professional eye: more robust error handling, YAML simplification, better reconnection handling, support for other controller variants, and general code hygiene improvements.

---

## 🤝 Contributing

- **Issues**: describe your problem with as much detail as possible (ESPHome logs at `DEBUG` or `VERBOSE` level, exact controller model, observed vs. expected behavior).
- **Pull requests**: welcome, big or small. Feel free to propose refactors even if they change the file's structure.

---

## 📄 License

This project is published under the [MIT](LICENSE) license — feel free to reuse, modify, and redistribute it.

---

## 🙌 Acknowledgments

- The [ESPHome](https://esphome.io/) and [Home Assistant](https://www.home-assistant.io/) communities
- This project owes a lot to conversational AI assistance (Claude, Grok) for debugging and writing the code — hence the importance of community review mentioned above
