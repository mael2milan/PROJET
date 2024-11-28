import os
import PyPDF2
import requests
from ebooklib import epub
from bs4 import BeautifulSoup


class base_bibli:
    """
    Classe de base pour la gestion d'une bibliothèque.
    """

    def __init__(self, path):
        """path désigne le répertoire contenant les livres de cette bibliothèque."""
        raise NotImplementedError("À définir dans les sous-classes")

    def ajouter(self, livre):
        """
        Ajoute un livre à la bibliothèque.
        """
        raise NotImplementedError("À définir dans les sous-classes")

    def rapport_livres(self, format, fichier):
        """
        Génère un rapport sur les livres.
        """
        raise NotImplementedError("À définir dans les sous-classes")

    def rapport_auteurs(self, format, fichier):
        """
        Génère un rapport sur les auteurs.
        """
        raise NotImplementedError("À définir dans les sous-classes")


class simple_bibli(base_bibli):
    """
    Une implémentation simplifiée de base_bibli.
    """

    def __init__(self, path):
        """
        Initialise la bibliothèque avec le répertoire contenant les fichiers.
        """
        self.path = path
        self.livres = []
        self.charger_livres()

    def charger_livres(self):
        """
        Parcourt le répertoire et ajoute les livres détectés.
        """
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Le chemin spécifié n'existe pas : {self.path}")

        for fichier in os.listdir(self.path):
            chemin_complet = os.path.join(self.path, fichier)
            if fichier.endswith(".pdf"):
                livre = LivrePDF(chemin_complet)
                self.ajouter(livre)
            elif fichier.endswith(".epub"):
                livre = LivreEPUB(chemin_complet)
                self.ajouter(livre)

    def ajouter(self, livre):
        """
        Ajoute un livre à la liste des livres.
        """
        self.livres.append(livre)

    def rapport_livres(self, format, fichier):
        """
        Génère un rapport contenant les titres, auteurs, types et noms de fichiers.
        """
        with open(fichier, "w", encoding="utf-8") as f:
            f.write("Rapport des livres\n")
            f.write("===================\n")
            for livre in self.livres:
                f.write(
                    f"Titre : {livre.titre()}, Auteur : {livre.auteur()}, Type : {livre.type()}, Fichier : {livre.fichier}\n"
                )

    def rapport_auteurs(self, format, fichier):
        """
        Génère un rapport listant les auteurs et leurs livres.
        """
        auteurs = {}
        for livre in self.livres:
            if livre.auteur() not in auteurs:
                auteurs[livre.auteur()] = []
            auteurs[livre.auteur()].append(livre)

        with open(fichier, "w", encoding="utf-8") as f:
            f.write("Rapport des auteurs\n")
            f.write("====================\n")
            for auteur, livres in auteurs.items():
                f.write(f"Auteur : {auteur}\n")
                for livre in livres:
                    f.write(
                        f"    - Titre : {livre.titre()}, Type : {livre.type()}, Fichier : {livre.fichier}\n"
                    )




class base_livre:
    """
    Classe de base pour un livre.
    """

    def __init__(self, fichier):
        self.fichier = fichier

    def titre(self):
        raise NotImplementedError

    def auteur(self):
        raise NotImplementedError

    def type(self):
        raise NotImplementedError


class LivrePDF(base_livre):
    """
    Représente un livre au format PDF.
    """

    def __init__(self, fichier):
        super().__init__(fichier)
        self._titre = "Titre inconnu"
        self._auteur = "Auteur inconnu"
        self.extraire_metadonnees()

    def extraire_metadonnees(self):
        try:
            with open(self.fichier, "rb") as f:
                lecteur = PyPDF2.PdfReader(f)
                info = lecteur.metadata
                if info:
                    self._titre = info.get("/Title", "Titre inconnu")
                    self._auteur = info.get("/Author", "Auteur inconnu")
        except Exception as e:
            print(f"Erreur lors de la lecture du PDF {self.fichier} : {e}")

    def titre(self):
        return self._titre

    def auteur(self):
        return self._auteur

    def type(self):
        return "PDF"


class LivreEPUB(base_livre):
    """
    Représente un livre au format EPUB.
    """

    def __init__(self, fichier):
        super().__init__(fichier)
        self._titre = "Titre inconnu"
        self._auteur = "Auteur inconnu"
        self.extraire_metadonnees()

    def extraire_metadonnees(self):
        try:
            book = epub.read_epub(self.fichier)
            self._titre = next(iter(book.get_metadata("DC", "title", default=["Titre inconnu"])), "Titre inconnu")
            self._auteur = next(iter(book.get_metadata("DC", "creator", default=["Auteur inconnu"])), "Auteur inconnu")
        except Exception as e:
            print(f"Erreur lors de la lecture de l'EPUB {self.fichier} : {e}")

    def titre(self):
        return self._titre

    def auteur(self):
        return self._auteur

    def type(self):
        return "EPUB"
    





class bibli(simple_bibli):
    """
    Classe bibliothèque avec une méthode pour ajouter des livres référencés sur une page web.
    """

    def alimenter(self, url):
        """
        Ajoute les livres PDF et EPUB référencés sur la page web spécifiée.
        """
        try:
            # Récupérer le contenu de la page
            response = requests.get(url)
            response.raise_for_status()
            page_content = response.text

            # Analyse du contenu HTML avec BeautifulSoup
            soup = BeautifulSoup(page_content, "html.parser")
            links = soup.find_all("a", href=True)

            # Parcours des liens pour détecter les fichiers PDF et EPUB
            for link in links:
                href = link["href"]
                if href.endswith(".pdf") or href.endswith(".epub"):
                    # Télécharger le fichier
                    fichier_local = os.path.join(self.path, os.path.basename(href))
                    self.telecharger_fichier(href, fichier_local)

                    # Ajouter à la bibliothèque
                    if href.endswith(".pdf"):
                        livre = LivrePDF(fichier_local)
                    elif href.endswith(".epub"):
                        livre = LivreEPUB(fichier_local)
                    else:
                        continue

                    self.ajouter(livre)

        except Exception as e:
            print(f"Erreur lors de l'alimentation depuis l'URL {url} : {e}")

    def telecharger_fichier(self, url, chemin):
        """
        Télécharge un fichier depuis une URL et le sauvegarde à l'emplacement spécifié.
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(chemin, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Fichier téléchargé : {url} -> {chemin}")
        except Exception as e:
            print(f"Erreur lors du téléchargement du fichier {url} : {e}")





