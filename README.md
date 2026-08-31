🇬🇧 [English version](README.en.md)

# 🌱 Proxy ESPHome pour boîtier d'irrigation Rain Pure Vision 2.0 (2 zones)

Intégration [ESPHome](https://esphome.io/) / [Home Assistant](https://www.home-assistant.io/) non officielle pour le boîtier d'irrigation **Rain Pure Vision 2.0 (2 zones)**, piloté en Bluetooth Low Energy (BLE). Cette intégration n'existait pas jusqu'à présent. Ce dépôt tente de combler ce manque.

Un ESP32 fait office de **proxy** : il maintient la connexion BLE avec le boîtier et expose toutes les fonctions utiles côté Home Assistant via l'API native ESPHome (WiFi).

---

## ⚠️ Avertissement important — lisez avant d'utiliser

**Je ne suis pas développeur et je ne sais pas coder.** Ce projet est né d'un besoin personnel (mon boîtier Rain Pure Vision n'avait aucune intégration disponible) et a été construit avec l'aide de plusieurs assistants IA (Claude, Grok), à partir d'un travail de rétro-ingénierie de l'application officielle Rain Vision.

Concrètement, cela veut dire :
- Le code fonctionne **sur mon installation**, testé et validé après plusieurs itérations de débogage, mais il n'a probablement pas la rigueur, la robustesse ou l'élégance qu'un développeur professionnel aurait produites.
- Je ne suis pas en mesure d'expliquer ou de justifier chaque ligne de code en profondeur — je peux témoigner de ce qui a été observé et testé, pas garantir la justesse de chaque détail d'implémentation.
- Le protocole BLE du boîtier n'est **pas documenté officiellement** : tout ce qui est décrit ici vient d'une analyse du code JavaScript décompilé de l'application officielle, complétée par des tests empiriques (captures de logs, comparaison de valeurs avec le comportement réel de l'appareil).

**Si vous êtes développeur⋅euse et que vous repérez des erreurs, des approximations, ou des façons plus propres de faire les choses (gestion d'erreurs, structuration du YAML, fiabilité de la connexion BLE, etc.), votre aide est la bienvenue et sincèrement appréciée.** Ouvrez une issue, une pull request, ou dites-moi simplement ce qui cloche — je préfère un projet imparfait mais qui s'améliore avec la communauté qu'un projet figé.

---

## ⚡ Note importante : connexion BLE exclusive

**Lorsque l'ESP32 est connecté au boîtier en BLE, celui-ci n'est plus accessible via l'application officielle Rain Pure Vision.** Le boîtier gère une seule connexion BLE à la fois. Vous pouvez rétablir la connexion avec l'app officielle en débranchant simplement l'ESP32 ; la reconnexion du proxy se fera automatiquement au redémarrage de l'ESP.

**C'est précisément pour cette raison qu'un blueprint Home Assistant est fourni** : la programmation des arrosages est nettement plus pratique via Home Assistant et le proxy ESPHome que via l'application officielle limitée. Ce projet offre ainsi une meilleure expérience utilisateur pour la gestion quotidienne de votre système d'arrosage.

---

## 🔧 Fonctionnalités

| Fonctionnalité | Détail |
|---|---|
| **Arrosage manuel** | Démarrage d'un cycle sur la zone et la durée de votre choix (1 à 60 min) |
| **Fermeture immédiate de la vanne** | Bouton "stop" général, toutes zones |
| **Pause programmée** | Suspend les programmes automatiques pour une durée réglable (1 à 14 jours), avec **vérification réelle** que le boîtier a bien pris en compte la pause |
| **Annulation de pause** | Réactive les programmes automatiques |
| **État de la vanne** (ouverte/fermée) | Déduit de l'état réel des zones actives |
| **Zone en cours d'arrosage** | Numéro de la zone active pendant un cycle |
| **Temps restant** | Temps restant sur le cycle en cours (en secondes) |
| **Capteur de pluie** | État du capteur de pluie du boîtier, si équipé |
| **Pompe active** | Détection d'activation de la pompe (le cas échéant) |
| **Défauts électrovanne** | Détection de circuit ouvert / court-circuit sur les électrovannes |
| **Batterie** | Niveau de batterie du boîtier |
| **Connexion BLE** | Capteur binaire diagnostiquant l'état de la connexion en temps réel |
| **Synchronisation de l'heure** | L'heure du boîtier est automatiquement resynchronisée à chaque connexion et à chaque synchro NTP |

Toutes ces entités sont exposées nativement à Home Assistant via l'intégration ESPHome — aucune configuration supplémentaire n'est nécessaire côté HA.

---

## 🧰 Prérequis matériel

- Un **ESP32 générique** (n'importe quelle carte de dev basique convient)
- Un boîtier **Rain Pure Vision 2.0, version 2 zones**
- [ESPHome](https://esphome.io/) (dernière version recommandée, framework `esp-idf`)
- Home Assistant, si vous voulez exploiter les entités (pas strictement obligatoire — l'API ESPHome fonctionne aussi seule)

---

## 🚀 Installation

1. **Récupérez l'adresse MAC BLE de votre boîtier.** Vous pouvez la trouver avec une appli de scan BLE (nRF Connect, LightBlue...) en cherchant l'appareil correspondant à votre Rain Pure Vision, ou en laissant ESPHome logguer les appareils détectés à proximité.

2. **Créez un fichier `secrets.yaml`** à côté du fichier YAML, avec :
   ```yaml
   wifi_ssid: "VotreSSID"
   wifi_password: "VotreMotDePasse"
   ap_fallback_password: "un_mot_de_passe_de_secours"
   api_encryption_key: "générer une nouvelle clé secrete qui vous est propre"
   ```
   Pour générer une clé de chiffrement API valide (32 octets encodés en base64), vous pouvez utiliser la commande `esphome secrets` de la CLI ESPHome, ou simplement demander au dashboard ESPHome de la générer automatiquement lors de la création d'un nouvel appareil.

3. **Modifiez l'adresse MAC** dans le bloc `ble_client:` du fichier YAML pour qu'elle corresponde à votre boîtier.

4. **Adaptez le nombre de zones** si nécessaire : `max_value: 2` sous `number: Zone à arroser` correspond à un boîtier 2 zones. Un boîtier avec plus de zones n'a pas été testé — voir la section Limitations.

5. **Flashez** votre ESP32 via ESPHome (CLI, dashboard, ou VS Code + extension ESPHome).

6. Ajoutez l'appareil dans Home Assistant via l'intégration ESPHome (découverte automatique normalement, sinon ajout manuel par IP).

---

## 🔍 Comment ça marche (pour les curieux)

Le protocole BLE du Rain Pure Vision n'étant pas documenté, ce projet s'appuie sur une rétro-ingénierie du code JavaScript de l'application officielle (décompilé depuis le bundle de l'app Ionic/Capacitor). Quelques points clés découverts pendant le développement :

- Le boîtier limite volontairement chaque session BLE à **~60 secondes** (`DisconnectTimer = 60000` dans le code de l'app) — ce n'est pas un bug du proxy, c'est un comportement voulu du firmware. Le proxy se reconnecte automatiquement.
- Le champ de durée du cycle en cours (`CURR_ZONE_LASTING_TIME`) est exprimé en **secondes**, pas en minutes malgré ce que son nom suggère — confirmé empiriquement en comparant la décroissance du compteur à un chronomètre réel sur un cycle programmé.
- L'heure doit être régulièrement réécrite dans le boîtier (caractéristique `TIME`) pour que les pauses datées et certains cycles fonctionnent correctement.
- La trame de commande "arrosage manuel" (`MANUAL`) fait 64 octets (2 octets par zone, jusqu'à 32 zones), même si le boîtier n'en gère que 2.

---

## 🐞 Limitations connues / zones d'incertitude

*Testé uniquement sur un seul boîtier Rain Pure Vision 2 zones.** Le comportement sur d'autres variantes (plus de zones, autre génération) n'est pas garanti.
- L'UUID exact de la caractéristique `TIME` (`0200F004`) a été déduit par analogie avec les autres caractéristiques du même service, mais n'a pas pu être confirmé ligne à ligne dans le code source (la fonction correspondante référence le nom `'TIME'`, pas l'UUID brut). Ça fonctionne dans mes tests, mais à surveiller.
- Les bits `STATUS_FLAG` (erreurs matérielles, mot de passe par défaut non changé, etc.) ne sont **pas** exposés : leur position exacte dépend du modèle de boîtier et n'a pas pu être confirmée avec certitude.
- Le cycle de déconnexion à 60 secondes peut occasionnellement retarder la remontée d'un état (ex. juste après une pause), sans empêcher le fonctionnement.
  
---

## 🙏 Appel aux développeurs

Si vous maîtrisez ESPHome, le C++, ou le protocole BLE, ce projet a clairement besoin d'un regard professionnel : gestion d'erreurs plus robuste, simplification du YAML, meilleure gestion de la reconnexion, support d'autres variantes du boîtier (plus de zones)... Toute contribution, review, ou simple retour d'expérience est la bienvenue. Merci d'avance à qui voudra bien y jeter un œil !

---

## 🤝 Contribuer

- **Issues** : décrivez votre problème avec autant de détails que possible (logs ESPHome en niveau `DEBUG` ou `VERBOSE`, modèle exact de boîtier, comportement observé vs attendu).
- **Pull requests** : bienvenues, petites ou grosses. N'hésitez pas à proposer des refactors même s'ils changent la structure du fichier.

---

## 📄 Licence

Ce projet est publié sous licence [MIT](LICENSE) — libre à vous de le réutiliser, modifier et redistribuer.

---

## 🙌 Remerciements

- La communauté [ESPHome](https://esphome.io/) et [Home Assistant](https://www.home-assistant.io/)
- Ce projet doit beaucoup à l'assistance d'IA conversationnelles (Claude, Grok) pour le débogage et la rédaction du code — d'où l'importance de la relecture communautaire mentionnée plus haut
