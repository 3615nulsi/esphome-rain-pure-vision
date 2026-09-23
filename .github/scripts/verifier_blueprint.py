"""Vérification statique des blueprints Home Assistant (français et anglais).

- le YAML se charge (avec la balise !input propre aux blueprints) ;
- chaque !input utilisé correspond à une entrée déclarée ;
- chaque entrée déclarée est utilisée ;
- chaque template Jinja a une syntaxe valide (les filtres propres à HA ne
  sont vérifiés qu'à l'exécution, pas ici) ;
- la version anglaise a exactement la même logique que la version française
  (seuls les textes affichés peuvent différer : noms, descriptions, alias,
  titres et messages de notification, textes affichés entre guillemets
  simples dans les templates).
"""

import re
import sys

import jinja2
import yaml

FICHIER_FR = "blueprint_programmation_rain_pure_vision_esphome.yaml"
FICHIER_EN = "blueprint_rain_pure_vision_esphome_en.yaml"

# Clés dont la valeur est un texte affiché, libre de différer entre langues.
CLES_TEXTE = {"name", "description", "alias", "title", "message", "stop",
              "msg_prefix", "pluie_prevue_libelle"}


class Input(str):
    pass


class Chargeur(yaml.SafeLoader):
    pass


Chargeur.add_constructor("!input", lambda loader, node: Input(loader.construct_scalar(node)))


def parcourir(noeud, chemin="racine"):
    if isinstance(noeud, dict):
        for cle, valeur in noeud.items():
            yield from parcourir(valeur, f"{chemin}.{cle}")
    elif isinstance(noeud, list):
        for i, valeur in enumerate(noeud):
            yield from parcourir(valeur, f"{chemin}[{i}]")
    else:
        yield chemin, noeud


def charger(fichier):
    with open(fichier, encoding="utf-8") as f:
        return yaml.load(f, Loader=Chargeur)


def verifier(fichier, doc):
    erreurs = []
    declarees = set(doc["blueprint"]["input"])
    utilisees = set()
    env = jinja2.Environment(extensions=["jinja2.ext.loopcontrols"])

    for chemin, valeur in parcourir({k: v for k, v in doc.items() if k != "blueprint"}):
        if isinstance(valeur, Input):
            utilisees.add(str(valeur))
            if valeur not in declarees:
                erreurs.append(f"{fichier} : {chemin} : !input {valeur} n'est pas déclaré")
        elif isinstance(valeur, str) and ("{{" in valeur or "{%" in valeur):
            try:
                env.parse(valeur)
            except jinja2.TemplateSyntaxError as e:
                erreurs.append(f"{fichier} : {chemin} : template invalide ({e.message}, ligne {e.lineno})")

    for nom in sorted(declarees - utilisees):
        erreurs.append(f"{fichier} : entrée « {nom} » déclarée mais jamais utilisée")
    return erreurs


def logique(noeud, cle=None):
    """Structure du blueprint sans les textes affichés."""
    if isinstance(noeud, dict):
        return {k: logique(v, k) for k, v in noeud.items()}
    if isinstance(noeud, list):
        return [logique(v, cle) for v in noeud]
    if isinstance(noeud, str) and not isinstance(noeud, Input):
        if "{{" in noeud or "{%" in noeud:
            # Ne garder que le code Jinja, sans ses textes affichés : chaînes
            # '…' contenant un espace ou un caractère non ASCII (emoji,
            # accent). Les valeurs techniques ('on', 'none', '|||'…) restent.
            blocs = re.findall(r"\{\{.*?\}\}|\{%.*?%\}", noeud, re.S)
            return [re.sub(r"'[^']*(?:\s|[^\x00-\x7f])[^']*'", "'<texte>'", " ".join(b.split()))
                    for b in blocs]
        if cle in CLES_TEXTE:
            return "<texte>"
    return noeud


def comparer(a, b, chemin="racine"):
    if type(a) is not type(b):
        return [f"{chemin} : types différents"]
    if isinstance(a, dict):
        if a.keys() != b.keys():
            return [f"{chemin} : clés différentes ({sorted(a.keys() ^ b.keys())})"]
        return [e for k in a for e in comparer(a[k], b[k], f"{chemin}.{k}")]
    if isinstance(a, list):
        if len(a) != len(b):
            return [f"{chemin} : longueurs différentes"]
        return [e for i, (x, y) in enumerate(zip(a, b)) for e in comparer(x, y, f"{chemin}[{i}]")]
    return [] if a == b else [f"{chemin} : {a!r} ≠ {b!r}"]


def main():
    fr, en = charger(FICHIER_FR), charger(FICHIER_EN)
    erreurs = verifier(FICHIER_FR, fr) + verifier(FICHIER_EN, en)
    erreurs += [f"FR/EN différents : {e}" for e in comparer(logique(fr), logique(en))]

    if erreurs:
        print("\n".join(erreurs))
        sys.exit(1)
    print(f"Blueprints OK : {len(fr['blueprint']['input'])} entrées, toutes utilisées ; "
          "même logique en français et en anglais.")


if __name__ == "__main__":
    main()
