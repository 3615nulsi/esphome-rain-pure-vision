# Sécurité / Security

🇬🇧 [English below](#-english)

## 🇫🇷 Français

### Versions prises en charge

Seules la dernière version publiée ([Releases](https://github.com/3615nulsi/esphome-rain-pure-vision/releases)) et la branche `main` reçoivent des correctifs.

### Signaler une vulnérabilité

**Ne publiez pas de vulnérabilité dans une issue publique.** Utilisez le signalement privé de GitHub : onglet **Security** → **Report a vulnerability** ([lien direct](https://github.com/3615nulsi/esphome-rain-pure-vision/security/advisories/new)).

Indiquez si possible : le fichier concerné, la version (tag ou commit), les étapes pour reproduire et l'impact possible.

Ce projet est maintenu par un particulier, sur son temps libre : je m'efforce de répondre sous quelques jours, sans pouvoir garantir de délai.

### Périmètre

Concerné : le package ESPHome (`rain_pure_vision.yaml`, `langues/`), l'exemple d'appareil (`proxy_rain_vision_pure.yml`), les blueprints Home Assistant et la CI de ce dépôt.

Non concerné, à signaler directement aux projets correspondants :
- le boîtier Rain Pure Vision, son firmware et son protocole Bluetooth (société RAIN) ;
- [ESPHome](https://github.com/esphome/esphome/security) et [Home Assistant](https://www.home-assistant.io/security/).

### Bonnes pratiques

- Ne publiez jamais votre `secrets.yaml` (mots de passe Wi-Fi, clé de chiffrement de l'API) ni l'adresse MAC de votre boîtier.
- Activez le chiffrement de l'API ESPHome (`api: encryption: key:`), comme dans l'exemple fourni.
- Le proxy se connecte au boîtier sans appairage Bluetooth. La sécurité du protocole Bluetooth du boîtier lui-même relève de la société RAIN (voir Périmètre).

---

## 🇬🇧 English

### Supported versions

Only the latest published release ([Releases](https://github.com/3615nulsi/esphome-rain-pure-vision/releases)) and the `main` branch receive fixes.

### Reporting a vulnerability

**Do not disclose a vulnerability in a public issue.** Use GitHub's private reporting: **Security** tab → **Report a vulnerability** ([direct link](https://github.com/3615nulsi/esphome-rain-pure-vision/security/advisories/new)).

If possible, include: the affected file, the version (tag or commit), steps to reproduce and the possible impact.

This project is maintained by an individual in their spare time: I try to answer within a few days, but cannot guarantee a response time.

### Scope

In scope: the ESPHome package (`rain_pure_vision.yaml`, `langues/`), the example device (`proxy_rain_vision_pure.yml`), the Home Assistant blueprints and this repository's CI.

Out of scope, please report directly to the relevant projects:
- the Rain Pure Vision controller, its firmware and its Bluetooth protocol (RAIN company);
- [ESPHome](https://github.com/esphome/esphome/security) and [Home Assistant](https://www.home-assistant.io/security/).

### Good practices

- Never publish your `secrets.yaml` (Wi-Fi passwords, API encryption key) or your controller's MAC address.
- Enable ESPHome API encryption (`api: encryption: key:`), as in the provided example.
- The proxy connects to the controller without Bluetooth pairing. The security of the controller's own Bluetooth protocol is the RAIN company's responsibility (see Scope).
