#!/usr/bin/env python3
import os
from ebooklib import epub
from PyPDF2 import PdfReader

class base_livre:
    """Classe de base représentant un livre."""
    def __init__(self, titre, auteur, type_fichier, chemin):
        self._titre = titre
        self._auteur = auteur
        self._type_fichier = type_fichier  # PDF ou EPUB
        self._chemin = chemin

    def titre(self):
        return self._titre

    def auteur(self):
        return self._auteur

    def type(self):
        return self._type_fichier

    def chemin(self):
        return self._chemin


class base_bibli:
    """Classe abstraite représentant une bibliothèque."""
    def __init__(self, path):
        """Path désigne le répertoire contenant les livres de cette bibliothèque."""
        raise NotImplementedError("à définir dans les sous-classes")

    def ajouter(self, livre):
        """Ajoute le livre à la bibliothèque."""
        raise NotImplementedError("à définir dans les sous-classes")

    def rapport_livres(self, format, fichier):
        """
        Génère un état des livres de la bibliothèque.
        """
        raise NotImplementedError("à définir dans les sous-classes")

    def rapport_auteurs(self, format, fichier):
        """
        Génère un état des auteurs des livres de la bibliothèque.
        """
        raise NotImplementedError("à définir dans les sous-classes")


class simple_bibli(base_bibli):
    """Bibliothèque simple stockant des livres locaux."""
    def __init__(self, path):
        """
        Initialise la bibliothèque avec un chemin vers le répertoire
        contenant les livres.
        """
        if not os.path.isdir(path):
            raise ValueError(f"Le chemin spécifié n'est pas valide : {path}")
        self.path = path  # Chemin du répertoire des livres
        self.livres = []  # Liste pour stocker les livres

        self._charger_livres()  # Charger les livres depuis le répertoire

    def _charger_livres(self):
        """Charge les livres depuis le répertoire spécifié."""
        for root, _, files in os.walk(self.path):
            for file in files:
                chemin_complet = os.path.join(root, file)
                if file.endswith('.pdf'):
                    self._ajouter_pdf(chemin_complet)
                elif file.endswith('.epub'):
                    self._ajouter_epub(chemin_complet)

    def _ajouter_pdf(self, chemin):
        """Ajoute un fichier PDF comme livre."""
        try:
            reader = PdfReader(chemin)
            titre = reader.metadata.title if reader.metadata.title else os.path.basename(chemin)
            auteur = reader.metadata.author if reader.metadata.author else "Auteur inconnu"
            livre = base_livre(titre, auteur, "PDF", chemin)
            self.ajouter(livre)
        except Exception as e:
            print(f"Erreur lors du traitement du fichier PDF {chemin} : {e}")

    def _ajouter_epub(self, chemin):
        """Ajoute un fichier EPUB comme livre."""
        try:
            book = epub.read_epub(chemin)
            titre = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else os.path.basename(chemin)
            auteur = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else "Auteur inconnu"
            livre = base_livre(titre, auteur, "EPUB", chemin)
            self.ajouter(livre)
        except Exception as e:
            print(f"Erreur lors du traitement du fichier EPUB {chemin} : {e}")

    def ajouter(self, livre):
        """Ajoute un livre à la bibliothèque."""
        if isinstance(livre, base_livre):
            self.livres.append(livre)
            print(f"Livre ajouté : {livre.titre()} ({livre.type()})")
        else:
            print("Erreur : l'objet ajouté n'est pas un type de livre valide.")

    def rapport_livres(self, format, fichier):
        """Génère un rapport des livres dans la bibliothèque."""
        with open(fichier, 'w', encoding='utf-8') as f:
            f.write(f"Rapport des livres ({format}):\n")
            for livre in self.livres:
                f.write(f"- Titre : {livre.titre()}, Auteur : {livre.auteur()}, Type : {livre.type()}, Fichier : {livre.chemin()}\n")
        print(f"Rapport des livres généré : {fichier}")

    def rapport_auteurs(self, format, fichier):
        """Génère un rapport des auteurs et de leurs livres."""
        auteurs = {}
        for livre in self.livres:
            if livre.auteur() not in auteurs:
                auteurs[livre.auteur()] = []
            auteurs[livre.auteur()].append(livre)

        with open(fichier, 'w', encoding='utf-8') as f:
            f.write(f"Rapport des auteurs ({format}):\n")
            for auteur, livres in auteurs.items():
                f.write(f"Auteur : {auteur}\n")
                for livre in livres:
                    f.write(f"    - Titre : {livre.titre()}, Type : {livre.type()}, Fichier : {livre.chemin()}\n")
        print(f"Rapport des auteurs généré : {fichier}")

if __name__ == "__main__":
    chemin_livres = r"/home/ousmane/Projet_POO/Livre"
    bibliotheque = simple_bibli(chemin_livres)

    # Générer un rapport des livres
    rapport_livres_fichier = r"/home/ousmane/Projet_POO/Livre/rapport_livres.txt"
    bibliotheque.rapport_livres("TXT", rapport_livres_fichier)

    # Générer un rapport des auteurs
    rapport_auteurs_fichier = r"/home/ousmane/Projet_POO/Livre/rapport_auteurs.txt"
    bibliotheque.rapport_auteurs("TXT", rapport_auteurs_fichier)

    print("Les rapports ont été générés avec succès !")
