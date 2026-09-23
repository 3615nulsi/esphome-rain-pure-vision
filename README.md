🇬🇧 [English version](README.en.md)

# 🌱 Proxy ESPHome pour Rain Pure Vision 2.0 (2 zones)

Intégration [ESPHome](https://esphome.io/) / [Home Assistant](https://www.home-assistant.io/) non officielle pour le boîtier d'irrigation **Rain Pure Vision 2.0 (2 zones)**, piloté en Bluetooth Low Energy (BLE).

Un ESP32 sert de **proxy** : il dialogue en BLE avec le boîtier et expose ses fonctions à Home Assistant via l'API native ESPHome (Wi-Fi). Un **blueprint** Home Assistant est fourni pour programmer les arrosages.

---

## ⚠️ Avertissement

**Je ne suis pas développeur.** Ce projet répond à un besoin personnel et a été construit avec l'aide d'assistants IA, à partir d'une rétro-ingénierie de l'application officielle Rain Vision.

- Il fonctionne **sur mon installation**, mais n'a pas la rigueur d'un projet professionnel.
- Le protocole BLE du boîtier n'est **pas documenté** : tout vient de l'analyse du code de l'application officielle et de tests sur un seul boîtier.

Les retours et contributions sont les bienvenus (voir [Contribuer](#-contribuer)).

---

## ⚡ Connexion BLE exclusive

Le boîtier n'accepte qu'**une seule connexion BLE à la fois** : tant que l'ESP32 y est connecté, l'application officielle ne peut pas s'y connecter. Pour utiliser l'app, débranchez l'ESP32 ; le proxy se reconnectera tout seul au redémarrage.

---

## 🔧 Fonctionnalités du proxy

| Fonctionnalité | Détail |
|---|---|
| **Arrosage manuel** | Zone et durée au choix (1 à 60 min). Le proxy attend la connexion BLE, **vérifie que la vanne s'est réellement ouverte** sur la bonne zone et réessaie sinon (3 tentatives) |
| **Fermeture de la vanne** | Bouton « stop » général, avec la même vérification |
| **Pause** | Suspend les programmes enregistrés dans le boîtier (1 à 14 jours), avec **confirmation** relue sur le boîtier |
| **Annulation de pause** | Réactive les programmes du boîtier |
| **État de la vanne** | Ouverte / fermée, d'après les zones réellement actives |
| **Zone en cours / temps restant** | Zone qui arrose et temps restant (en secondes) |
| **Capteur de pluie** | Capteur de pluie du boîtier, si équipé |
| **Pompe active** | Le cas échéant |
| **Défauts électrovanne** | Circuit ouvert / court-circuit, globalement et par zone |
| **Indicateurs du boîtier** | Mot de passe par défaut, erreur logicielle (FW), erreur matérielle (HW), charge de la batterie, historique plein (zones 1 et 2) |
| **Programmes enregistrés** | Nombre de programmes stockés dans le boîtier, actifs ou désactivés |
| **Sondes ACQUA** | Nombre de sondes détectées (255 = pas encore rafraîchi) |
| **Batterie** | Niveau de batterie du boîtier |
| **Connexion BLE** | État de la connexion au boîtier |
| **Heure** | Heure du boîtier resynchronisée à chaque connexion et à chaque synchro NTP |

---

## 🗓️ Blueprint de programmation

Le fichier `blueprint_programmation_rain_pure_vision_esphome.yaml` est un blueprint d'automatisation Home Assistant (HA ≥ 2024.10). À importer via **Paramètres → Automatisations et scènes → Blueprints → Importer un blueprint**, avec l'URL du fichier sur GitHub.

- Arrosage d'une zone pendant les créneaux d'un planning (entrée *Planning* de Home Assistant), vanne fermée en fin de créneau.
- Durée ajustée par un coefficient saisonnier (`input_number` en %).
- Arrosage annulé en cas de : défaut électrique, pause du boîtier, capteur de pluie actif, **pluie tombée récemment** (capteur de cumul, ex. entrée *Statistiques* sur 48 h), **pluie prévue** sur les prochaines heures, sol assez humide.
- Attente du Bluetooth si le boîtier est momentanément injoignable.
- Ouverture et fermeture **vérifiées** sur l'état réel de la vanne, fermeture forcée si elle reste ouverte trop longtemps.
- Notifications (démarrage, annulation avec motif, fin, anomalies) via `notify.send_message`.

---

## 🧰 Prérequis

- Un **ESP32** avec Bluetooth (pas d'ESP8266), dédié ou déjà utilisé par un autre appareil ESPHome
- Un boîtier **Rain Pure Vision 2.0, 2 zones**
- [ESPHome](https://esphome.io/), framework `esp-idf` recommandé
- Home Assistant (facultatif pour le proxy seul, nécessaire pour le blueprint)

---

## 🚀 Installation

Toute la logique est dans **`rain_pure_vision.yaml`**, un [package ESPHome](https://esphome.io/components/packages/) téléchargé depuis ce dépôt à la compilation.

### Option A — Appareil ESPHome existant

Ajoutez à sa configuration :

```yaml
substitutions:
  rain_mac: "AA:BB:CC:DD:EE:FF"   # adresse MAC BLE de votre boîtier
  rain_timezone: "Europe/Paris"   # facultatif (valeur par défaut)
  rain_zones: "2"                 # facultatif (valeur par défaut)

packages:
  rain_pure_vision:
    url: https://github.com/3615nulsi/esphome-rain-pure-vision
    ref: main
    files: [rain_pure_vision.yaml]
    refresh: 1d
```

- Si l'appareil est aussi un **proxy Bluetooth** (`bluetooth_proxy:`), ajoutez `max_connections: 4` sous `esp32_ble:` (ESPHome le signale par un avertissement).
- Le package ajoute sa propre horloge SNTP ; elle cohabite sans problème avec `time: homeassistant`.
- Les entités apparaissent dans Home Assistant sous le nom de cet appareil.

### Option B — ESP32 dédié

1. Partez de l'exemple **`proxy_rain_vision_pure.yml`** (il contient déjà le bloc `packages:`).
2. Créez un **`secrets.yaml`** à côté :
   ```yaml
   wifi_ssid: "VotreSSID"
   wifi_password: "VotreMotDePasse"
   ap_fallback_password: "un_mot_de_passe_de_secours"
   api_encryption_key: "votre clé (32 octets en base64)"
   ```
   Le tableau de bord ESPHome peut générer la clé API à la création d'un appareil.
3. Renseignez **`rain_mac`** (et si besoin `rain_timezone`).

### Ensuite

- **Adresse MAC** : trouvable avec une appli de scan BLE (nRF Connect, LightBlue…) ou dans les logs ESPHome.
- **Flashez** l'ESP32, puis ajoutez-le à Home Assistant via l'intégration ESPHome (découverte automatique en général).

### Mises à jour

Le package est re-téléchargé à la compilation, au plus une fois par jour (`refresh: 1d`). Avec `ref: main`, chaque recompilation récupère la dernière version. Pour choisir le moment des mises à jour, figez une version publiée (ex. `ref: v1.1.0`, voir les [Releases](https://github.com/3615nulsi/esphome-rain-pure-vision/releases)).

---

## 🔍 Comment ça marche

Le protocole a été reconstitué à partir du code JavaScript de l'application officielle, puis vérifié sur le matériel. Quelques points notables :

- L'application officielle coupe ses sessions BLE au bout de **~60 secondes** ; le proxy se reconnecte automatiquement si le boîtier coupe la connexion.
- L'heure est réécrite dans le boîtier (caractéristique `TIME`) à chaque connexion, pour que les pauses datées fonctionnent.

---

## 🐞 Limitations

- **Testé sur un seul boîtier Rain Pure Vision 2 zones.** Le comportement sur d'autres variantes (plus de zones, autre génération) n'est pas garanti.
- Les indicateurs `STATUS_FLAG` (erreurs, mot de passe par défaut…) sont décodés d'après l'application officielle et n'ont été vérifiés que sur un boîtier 2 zones. 

---

## 🤝 Contribuer

Si vous connaissez ESPHome, le C++ ou le BLE, un regard extérieur est le bienvenu : robustesse, simplification, support d'autres variantes du boîtier…

- **Issues** : joignez les logs ESPHome (niveau `DEBUG`), le modèle exact du boîtier et le comportement observé / attendu.
- **Pull requests** : bienvenues, petites ou grosses, y compris des refactors.

---

## 📄 Licence

[MIT](LICENSE) — libre de réutiliser, modifier et redistribuer.

---

## 🙌 Remerciements

Les communautés [ESPHome](https://esphome.io/) et [Home Assistant](https://www.home-assistant.io/).
