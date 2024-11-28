

import requests
from urllib.parse import urlparse

class WebScraper:
    def __init__(self, downloader, extractor):
        self.downloader = downloader
        self.extractor = extractor
        self.visited_urls = set()
        self.downloaded_files = 0

    def scrape(self, start_url, max_depth, max_files):
        """
        Démarre le scraping en suivant les paramètres spécifiés.
        :param start_url: URL de départ
        :param max_depth: Profondeur maximale à explorer
        :param max_files: Nombre maximal de fichiers à télécharger
        """
        self._scrape_recursive(start_url, max_depth, max_files)

    def _scrape_recursive(self, url, max_depth, max_files, current_depth=0):
        if current_depth >= max_depth or self.downloaded_files >= max_files or url in self.visited_urls:
            return
        
        print(f"Exploring: {url} (Depth: {current_depth})")
        self.visited_urls.add(url)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except (requests.RequestException, ValueError) as e:
            print(f"Failed to fetch {url}: {e}")
            return

        links = self.extractor.extract_links(response.content, url)
        file_links = self.extractor.filter_links(links, ['.pdf', '.epub'])

        # Télécharger les fichiers
        for file_url in file_links:
            if self.downloaded_files >= max_files:
                break
            if self.downloader.download_file(file_url):
                self.downloaded_files += 1

        # Explorer les liens restants
        for link in links:
            if self._is_valid_url(link):
                self._scrape_recursive(link, max_depth, max_files, current_depth + 1)

    def _is_valid_url(self, url):
        """
        Vérifie si l'URL est valide pour être explorée.
        :param url: URL à vérifier
        :return: True si l'URL est valide, False sinon
        """
        return url.startswith('http') and url not in self.visited_urls



