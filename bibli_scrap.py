#!/bin/env python3 


import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class bibli_scrap:
    def __init__(self):
        self.downloaded_files = 0
        self.visited_urls = set()
    
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
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except (requests.RequestException, ValueError) as e:
            print(f"Failed to fetch {url}: {e}")
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
        parsed_url = urlparse(file_url)
        return any(parsed_url.path.endswith(ext) for ext in file_extensions)
    
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
            response = requests.get(file_url, stream=True, timeout=10)
            response.raise_for_status()
            
            filename = os.path.basename(urlparse(file_url).path)
            folder = 'downloads'
            os.makedirs(folder, exist_ok=True)
            file_path = os.path.join(folder, filename)
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.downloaded_files += 1
            print(f"Downloaded: {filename} -> {file_path}")
        except (requests.RequestException, IOError) as e:
            print(f"Failed to download {file_url}: {e}")
