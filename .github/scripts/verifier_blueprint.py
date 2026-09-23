"""Vérification statique du blueprint Home Assistant.

- le YAML se charge (avec la balise !input propre aux blueprints) ;
- chaque !input utilisé correspond à une entrée déclarée ;
- chaque entrée déclarée est utilisée ;
- chaque template Jinja a une syntaxe valide (les filtres propres à HA ne
  sont vérifiés qu'à l'exécution, pas ici).
"""

import sys

import jinja2
import yaml

FICHIER = "blueprint_programmation_rain_pure_vision_esphome.yaml"


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


def main():
    with open(FICHIER, encoding="utf-8") as f:
        doc = yaml.load(f, Loader=Chargeur)

    erreurs = []
    declarees = set(doc["blueprint"]["input"])
    utilisees = set()
    env = jinja2.Environment(extensions=["jinja2.ext.loopcontrols"])

    for chemin, valeur in parcourir({k: v for k, v in doc.items() if k != "blueprint"}):
        if isinstance(valeur, Input):
            utilisees.add(str(valeur))
            if valeur not in declarees:
                erreurs.append(f"{chemin} : !input {valeur} n'est pas déclaré")
        elif isinstance(valeur, str) and ("{{" in valeur or "{%" in valeur):
            try:
                env.parse(valeur)
            except jinja2.TemplateSyntaxError as e:
                erreurs.append(f"{chemin} : template invalide ({e.message}, ligne {e.lineno})")

    for nom in sorted(declarees - utilisees):
        erreurs.append(f"entrée « {nom} » déclarée mais jamais utilisée")

    if erreurs:
        print("\n".join(erreurs))
        sys.exit(1)
    print(f"Blueprint OK : {len(declarees)} entrées, toutes utilisées.")


if __name__ == "__main__":
    main()
