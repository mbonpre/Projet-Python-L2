"""
Module test_jeu.py
==================
Bloc 5 — Tests unitaires avec Pytest.
Bloc 5 — Tests des exceptions ajoutés.
Pour lancer les tests : pytest test_jeu.py -v
"""

import os
import json
import pytest
from objets import Arme, Potion, Inventaire
from personnages import Hero, Monstre
from sauvegarde import (
    sauvegarder_partie,
    charger_partie,
    sauvegarde_existe,
    supprimer_sauvegarde,
)

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def arme_base():
    return Arme("Épée", 10, 5)

@pytest.fixture
def potion_base():
    return Potion("Petite potion", 30)

@pytest.fixture
def hero_base(arme_base):
    return Hero("Arthur", 100, 1, arme_base)

@pytest.fixture
def monstre_base():
    return Monstre("Gobelin", 50, 1, 20, Arme("Dague", 5, 10))

@pytest.fixture(autouse=True)
def nettoyer_sauvegarde():
    supprimer_sauvegarde()
    yield
    supprimer_sauvegarde()


# =============================================================================
# TESTS — Arme
# =============================================================================

class TestArme:

    def test_creation_arme(self, arme_base):
        assert arme_base.nom == "Épée"
        assert arme_base.degats == 10
        assert arme_base.munitions == 5

    def test_arme_avec_munitions(self, arme_base):
        assert arme_base.munitions > 0

    def test_arme_sans_munitions(self):
        arme_vide = Arme("Pistolet vide", 20, 0)
        assert arme_vide.munitions == 0

    # --- Tests exceptions ---
    def test_arme_degats_negatifs(self):
        """Créer une arme avec des dégâts négatifs doit lever ValueError."""
        with pytest.raises(ValueError):
            Arme("Épée", -5, 10)

    def test_arme_munitions_negatives(self):
        """Créer une arme avec des munitions négatives doit lever ValueError."""
        with pytest.raises(ValueError):
            Arme("Épée", 10, -1)

    def test_arme_nom_vide(self):
        """Créer une arme avec un nom vide doit lever ValueError."""
        with pytest.raises(ValueError):
            Arme("", 10, 5)


# =============================================================================
# TESTS — Potion
# =============================================================================

class TestPotion:

    def test_creation_potion(self, potion_base):
        assert potion_base.nom == "Petite potion"
        assert potion_base.soin == 30

    def test_soin_positif(self, potion_base):
        assert potion_base.soin > 0

    # --- Tests exceptions ---
    def test_potion_soin_negatif(self):
        """Créer une potion avec un soin négatif doit lever ValueError."""
        with pytest.raises(ValueError):
            Potion("Potion", -10)

    def test_potion_nom_vide(self):
        """Créer une potion avec un nom vide doit lever ValueError."""
        with pytest.raises(ValueError):
            Potion("", 30)


# =============================================================================
# TESTS — Inventaire
# =============================================================================

class TestInventaire:

    def test_inventaire_vide(self):
        inv = Inventaire()
        assert inv.objets == []
        assert inv.armes == []

    def test_ajouter_potion(self, potion_base):
        inv = Inventaire()
        inv.ajouter_objet(potion_base)
        assert len(inv.objets) == 1
        assert inv.objets[0].nom == "Petite potion"

    def test_ajouter_arme(self, arme_base):
        inv = Inventaire()
        inv.ajouter_arme(arme_base)
        assert len(inv.armes) == 1

    def test_ajouter_plusieurs_potions(self, potion_base):
        inv = Inventaire()
        inv.ajouter_objet(potion_base)
        inv.ajouter_objet(Potion("Grande potion", 60))
        assert len(inv.objets) == 2

    # --- Tests exceptions ---
    def test_ajouter_objet_invalide(self):
        """Ajouter autre chose qu'une Potion doit lever TypeError."""
        inv = Inventaire()
        with pytest.raises(TypeError):
            inv.ajouter_objet("pas une potion")

    def test_ajouter_arme_invalide(self):
        """Ajouter autre chose qu'une Arme doit lever TypeError."""
        inv = Inventaire()
        with pytest.raises(TypeError):
            inv.ajouter_arme(42)


# =============================================================================
# TESTS — Hero
# =============================================================================

class TestHero:

    def test_creation_hero(self, hero_base):
        assert hero_base.nom == "Arthur"
        assert hero_base.hp == 100
        assert hero_base.level == 1
        assert hero_base.experience == 0

    def test_gagner_experience(self, hero_base):
        hero_base.gagner_experience(50)
        assert hero_base.experience == 50

    def test_montee_de_niveau(self, hero_base):
        hero_base.gagner_experience(100)
        assert hero_base.level == 2
        assert hero_base.experience == 0

    def test_attaque_reduit_hp_monstre(self, hero_base, monstre_base):
        hp_avant = monstre_base.hp
        hero_base.attaquer(monstre_base)
        assert monstre_base.hp < hp_avant

    def test_attaque_consomme_munition(self, hero_base, monstre_base):
        munitions_avant = hero_base.arme_actuelle.munitions
        hero_base.attaquer(monstre_base)
        assert hero_base.arme_actuelle.munitions == munitions_avant - 1

    def test_attaque_sans_munitions(self, hero_base, monstre_base):
        hero_base.arme_actuelle.munitions = 0
        hp_avant = monstre_base.hp
        hero_base.attaquer(monstre_base)
        assert monstre_base.hp == hp_avant

    def test_ajouter_potion_inventaire(self, hero_base, potion_base):
        hero_base.ajouter_objet_inventaire(potion_base)
        assert len(hero_base.inventaire.objets) == 1

    # --- Tests exceptions ---
    def test_hero_hp_negatif(self, arme_base):
        """Créer un héros avec HP négatifs doit lever ValueError."""
        with pytest.raises(ValueError):
            Hero("Arthur", -10, 1, arme_base)

    def test_hero_xp_negative(self, hero_base):
        """Donner de l'XP négative doit lever ValueError."""
        with pytest.raises(ValueError):
            hero_base.gagner_experience(-50)

    def test_hero_arme_invalide(self):
        """Créer un héros avec une arme invalide doit lever TypeError."""
        with pytest.raises(TypeError):
            Hero("Arthur", 100, 1, "pas une arme")


# =============================================================================
# TESTS — Monstre
# =============================================================================

class TestMonstre:

    def test_creation_monstre(self, monstre_base):
        assert monstre_base.nom == "Gobelin"
        assert monstre_base.hp == 50
        assert monstre_base.xp_gagne == 20

    def test_attaque_reduit_hp_hero(self, monstre_base, hero_base):
        hp_avant = hero_base.hp
        monstre_base.attaquer(hero_base)
        assert hero_base.hp < hp_avant

    def test_direction_initiale(self, monstre_base):
        assert monstre_base.face == True

    # --- Tests exceptions ---
    def test_monstre_xp_negative(self, arme_base):
        """Créer un monstre avec XP négative doit lever ValueError."""
        with pytest.raises(ValueError):
            Monstre("Gobelin", 50, 1, -10, arme_base)

    def test_monstre_arme_invalide(self):
        """Créer un monstre avec une arme invalide doit lever TypeError."""
        with pytest.raises(TypeError):
            Monstre("Gobelin", 50, 1, 20, "pas une arme")


# =============================================================================
# TESTS — Sauvegarde
# =============================================================================

class TestSauvegarde:

    def test_sauvegarde_cree_fichier(self, hero_base):
        sauvegarder_partie(hero_base)
        assert sauvegarde_existe()

    def test_sauvegarde_contient_bonnes_donnees(self, hero_base):
        sauvegarder_partie(hero_base)
        donnees = charger_partie()
        assert donnees["nom"] == "Arthur"
        assert donnees["hp"] == 100
        assert donnees["level"] == 1
        assert donnees["experience"] == 0

    def test_charger_partie_sans_fichier(self):
        assert charger_partie() is None

    def test_supprimer_sauvegarde(self, hero_base):
        sauvegarder_partie(hero_base)
        supprimer_sauvegarde()
        assert not sauvegarde_existe()

    def test_sauvegarde_avec_xp(self, hero_base):
        hero_base.gagner_experience(75)
        sauvegarder_partie(hero_base)
        donnees = charger_partie()
        assert donnees["experience"] == 75

    def test_sauvegarde_inventaire_potions(self, hero_base, potion_base):
        hero_base.ajouter_objet_inventaire(potion_base)
        sauvegarder_partie(hero_base)
        donnees = charger_partie()
        assert len(donnees["inventaire"]["potions"]) == 1
        assert donnees["inventaire"]["potions"][0]["nom"] == "Petite potion"

    # --- Tests exceptions ---
    def test_fichier_json_corrompu(self):
        """Un fichier JSON corrompu doit retourner None sans planter."""
        with open("sauvegarde.json", "w") as f:
            f.write("ceci n'est pas du json valide !!!")
        resultat = charger_partie()
        assert resultat is None
