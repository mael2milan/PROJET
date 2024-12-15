#!/usr/bin/env python3

import requests
import urllib3
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Désactiver les avertissements liés à SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class bibli_scrap:
    def __init__(self,download_folder):
        self.downloaded_files = 0
        self.visited_urls = set()
        self.download_folder = download_folder
        os.makedirs(self.download_folder, exist_ok=True)


    def scrap(self, url, profondeur, nbmax):
        """
        Réalise le web scraping pour télécharger les fichiers PDF et EPUB.
        
        :param url: URL de départ
        :param profondeur: Nombre maximal de niveaux à parcourir
        :param nbmax: Nombre maximal de documents à télécharger
        """
        self._scrap_recursive(url, profondeur, nbmax)
    
    def _scrap_recursive(self, url, profondeur, nbmax, current_depth=0):
        if current_depth >= profondeur or self.downloaded_files >= nbmax or url in self.visited_urls:
            return

        print(f"Exploring: {url} (Depth: {current_depth})")
        self.visited_urls.add(url)

        try:
            # Tentez d'utiliser 'verify=False' pour ignorer les erreurs SSL
            response = requests.get(url, timeout=10, verify=False)  
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Erreur lors de l'alimentation depuis l'URL {url} : {e}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')

        # Télécharger les fichiers PDF et EPUB référencés
        for link in soup.find_all('a', href=True):
            file_url = urljoin(url, link['href'])
            if self.downloaded_files >= nbmax:
                break
            if self._is_valid_file(file_url):
                self._download_file(file_url)

        # Explorer les liens vers d'autres pages
        for link in soup.find_all('a', href=True):
            next_url = urljoin(url, link['href'])
            if self._is_valid_url(next_url):
                self._scrap_recursive(next_url, profondeur, nbmax, current_depth + 1)
    
    def _is_valid_file(self, file_url):
        """
        Vérifie si l'URL correspond à un fichier PDF ou EPUB.
        """
        file_extensions = ['.pdf', '.epub']
        return any(file_url.endswith(ext) for ext in file_extensions)
    
    def _is_valid_url(self, next_url):
        """
        Vérifie si l'URL est valide et n'a pas été visitée.
        """
        return next_url.startswith('http') and next_url not in self.visited_urls
    
    def _download_file(self, file_url):
        """
        Télécharge le fichier depuis l'URL et l'enregistre localement.
        """
        try:
            response = requests.get(file_url, stream=True, timeout=10, verify=False)
            response.raise_for_status()

            filename = os.path.basename(file_url)
            file_path = os.path.join(self.download_folder, filename)

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.downloaded_files += 1
            print(f"Downloaded: {filename} -> {file_path}")
        except requests.RequestException as e:
            print(f"Failed to download {file_url}: {e}")

if __name__ == "__main__":
    # URL à scraper
    url = "https://math.univ-angers.fr/~jaclin/biblio/livres/"

    # Répertoire de téléchargement pour ce test
    download_folder = "/home/ousmane/Projet_POO/downloads"

    # Initialiser et lancer le scraping
    scraper = bibli_scrap(download_folder=download_folder)
    scraper.scrap(url, profondeur=1, nbmax=10)

    print(f"Test terminé. Les fichiers téléchargés se trouvent dans {download_folder}.")
