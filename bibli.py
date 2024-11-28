import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from ebooklib import epub
from PyPDF2 import PdfReader
from urllib3.exceptions import InsecureRequestWarning
import urllib3


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


class bibli(base_bibli):
    """Bibliothèque simple dotée d'une méthode d'alimentation via URL."""
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
            titre = reader.metadata.title if reader.metadata and reader.metadata.title else os.path.basename(chemin)
            auteur = reader.metadata.author if reader.metadata and reader.metadata.author else "Auteur inconnu"
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

    def alimenter(self, url, disable_ssl=False):
        """Ajoute tous les livres référencés dans la page web spécifiée."""
        try:
            # Désactiver la vérification SSL si demandé
            if disable_ssl:
                urllib3.disable_warnings(category=InsecureRequestWarning)
                response = requests.get(url, timeout=10, verify=False)
            else:
                response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Erreur lors de l'alimentation depuis l'URL {url} : {e}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('a', href=True):
            file_url = urljoin(url, link['href'])
            parsed_url = urlparse(file_url)
            if parsed_url.path.endswith('.pdf') or parsed_url.path.endswith('.epub'):
                local_path = os.path.join(self.path, os.path.basename(parsed_url.path))
                try:
                    self._telecharger_fichier(file_url, local_path, disable_ssl)
                    if local_path.endswith('.pdf'):
                        self._ajouter_pdf(local_path)
                    elif local_path.endswith('.epub'):
                        self._ajouter_epub(local_path)
                except Exception as e:
                    print(f"Erreur lors du téléchargement ou ajout du fichier {file_url} : {e}")

    def _telecharger_fichier(self, file_url, local_path, disable_ssl):
        """Télécharge un fichier depuis une URL vers un chemin local."""
        try:
            if disable_ssl:
                response = requests.get(file_url, stream=True, timeout=10, verify=False)
            else:
                response = requests.get(file_url, stream=True, timeout=10)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Téléchargé : {file_url} -> {local_path}")
        except requests.RequestException as e:
            raise RuntimeError(f"Erreur lors du téléchargement de {file_url} : {e}")


if __name__ == "__main__":
    # Remplacez par un chemin valide sur votre système
    chemin_bibliotheque = r"C:\Users\diaou\OneDrive\Bureau\Pyhon M1 DS\Collecte_de_livres\Bibliothèque"
    
    # Vérification que le chemin existe ou création automatique
    if not os.path.exists(chemin_bibliotheque):
        os.makedirs(chemin_bibliotheque)
        print(f"Le répertoire {chemin_bibliotheque} a été créé.")

    # Initialisation de la bibliothèque
    ma_bibli = bibli(chemin_bibliotheque)

    # URL pour tester l'alimentation
    url_test = "https://math.univ-angers.fr/~jaclin/biblio/livres/"
    ma_bibli.alimenter(url_test, disable_ssl=True)

    # Génération du rapport des livres
    ma_bibli.rapport_livres("TXT", "rapport_livres.txt")








