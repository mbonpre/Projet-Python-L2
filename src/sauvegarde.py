"""
Module sauvegarde.py
====================
Bloc 4 — Persistance des données avec JSON.
Bloc 5 — Gestion des exceptions ajoutée.
"""

import json
import os

FICHIER_SAUVEGARDE = "sauvegarde.json"


def sauvegarder_partie(hero):
    """Sauvegarde l'état complet du héros dans un fichier JSON."""
    try:
        donnees = {
            "nom": hero.nom,
            "hp": hero.hp,
            "level": hero.level,
            "experience": hero.experience,
            "arme_actuelle": {
                "nom": hero.arme_actuelle.nom,
                "degats": hero.arme_actuelle.degats,
                "munitions": hero.arme_actuelle.munitions
            },
            "inventaire": {
                "potions": [
                    {"nom": p.nom, "soin": p.soin}
                    for p in hero.inventaire.objets
                ],
                "armes": [
                    {"nom": a.nom, "degats": a.degats, "munitions": a.munitions}
                    for a in hero.inventaire.armes
                ]
            }
        }
        with open(FICHIER_SAUVEGARDE, 'w', encoding='utf-8') as f:
            json.dump(donnees, f, ensure_ascii=False, indent=4)
        print(f"  Partie sauvegardée dans '{FICHIER_SAUVEGARDE}' !")

    except PermissionError:
        print("  Erreur : impossible d'écrire le fichier de sauvegarde (permission refusée).")
    except OSError as e:
        print(f"  Erreur système lors de la sauvegarde : {e}")


def charger_partie():
    """Charge les données de sauvegarde depuis le fichier JSON."""
    try:
        if not sauvegarde_existe():
            return None
        with open(FICHIER_SAUVEGARDE, 'r', encoding='utf-8') as f:
            donnees = json.load(f)
        return donnees

    except json.JSONDecodeError:
        print("  Erreur : fichier de sauvegarde corrompu.")
        return None
    except PermissionError:
        print("  Erreur : impossible de lire le fichier de sauvegarde.")
        return None
    except OSError as e:
        print(f"  Erreur système lors du chargement : {e}")
        return None


def sauvegarde_existe():
    """Vérifie si un fichier de sauvegarde existe."""
    return os.path.exists(FICHIER_SAUVEGARDE)


def supprimer_sauvegarde():
    """Supprime le fichier de sauvegarde."""
    try:
        if sauvegarde_existe():
            os.remove(FICHIER_SAUVEGARDE)
    except PermissionError:
        print("  Erreur : impossible de supprimer le fichier de sauvegarde.")
    except OSError as e:
        print(f"  Erreur système lors de la suppression : {e}")
