import os
import configparser
import requests
from argparse import ArgumentParser
from pathlib import Path
import re
import urllib3

# Désactiver l'avertissement InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Bibliotheque:
    def __init__(self, conf_file):
        # Lire les configurations
        self.conf_file = conf_file
        self.config = configparser.ConfigParser()
        self.config.read(conf_file)
        
        # Initialisation des paramètres
        self.livres_dir = self.config.get('bibliotheque', 'livres')
        self.etats_dir = self.config.get('bibliotheque', 'etats')
        self.nbmax = int(self.config.get('bibliotheque', 'nbmax'))
    
    def get_config(self):
        return {
            'livres_dir': self.livres_dir,
            'etats_dir': self.etats_dir,
            'nbmax': self.nbmax
        }

class FileDownloader:
    def __init__(self, livres_dir):
        self.livres_dir = Path(livres_dir)
        self.livres_dir.mkdir(parents=True, exist_ok=True)

    def download_file(self, url):
        try:
            response = requests.get(url, verify=False)  # Désactivation de la vérification SSL
            response.raise_for_status()
            filename = Path(url).name
            file_path = self.livres_dir / filename
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f"File downloaded: {file_path}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")

class WebScraper:
    def __init__(self, downloader, max_depth, max_files):
        self.downloader = downloader
        self.max_depth = max_depth
        self.max_files = max_files
        self.visited_urls = set()
        self.files_downloaded = 0

    def scrape(self, url, depth=0):
        if depth > self.max_depth or self.files_downloaded >= self.max_files:
            return
        if url in self.visited_urls:
            return
        self.visited_urls.add(url)

        print(f"Exploring: {url} (Depth: {depth})")

        try:
            response = requests.get(url, verify=False)  # Désactivation de la vérification SSL
            response.raise_for_status()
            html = response.text

            print(f"Successfully fetched: {url} (Status code: {response.status_code})")

            # Extraire les liens et télécharger les fichiers PDF/EPUB
            self._download_files_from_html(html)
            
            # Extraire les liens et scraper récursivement les pages suivantes
            links = self._extract_links(html, url)
            for link in links:
                self.scrape(link, depth + 1)
        except requests.exceptions.RequestException as e:
            print(f"Request Error: Failed to fetch {url}: {e}")

    def _extract_links(self, html, base_url):
        # Extraire les liens dans la page HTML (en utilisant une expression régulière simple)
        links = re.findall(r'href=["\'](https?://\S+)', html)
        return links

    def _download_files_from_html(self, html):
        # Extraire et télécharger les fichiers PDF/EPUB depuis les liens trouvés
        if self.files_downloaded < self.max_files:
            # Rechercher des liens vers des fichiers PDF ou EPUB dans le HTML
            links = re.findall(r'href=["\'](https?://\S+\.(pdf|epub))', html)

            for link in links:
                if self.files_downloaded < self.max_files:
                    print(f"Downloading file from {link[0]}")
                    self.downloader.download_file(link[0])
                    self.files_downloaded += 1
                else:
                    break

class ReportGenerator:
    def __init__(self, etats_dir):
        self.etats_dir = Path(etats_dir)
        self.etats_dir.mkdir(parents=True, exist_ok=True)

    def generate_reports(self):
        # Logic for generating PDF and EPUB reports
        pdf_report = self.etats_dir / "report.pdf"
        epub_report = self.etats_dir / "report.epub"
        
        with open(pdf_report, 'w') as f:
            f.write("PDF Report Content")
        with open(epub_report, 'w') as f:
            f.write("EPUB Report Content")
        
        print(f"Reports generated: {pdf_report}, {epub_report}")

def main():
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', help="Path to the configuration file", default="bibli.conf")
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand: url
    parser_url = subparsers.add_parser('url', help="Start scraping from a given URL")
    parser_url.add_argument('url', help="The starting URL for scraping")
    parser_url.add_argument('depth', type=int, help="Maximum depth to scrape")

    # Subcommand: rapports
    parser_rapports = subparsers.add_parser('rapports', help="Generate reports")

    args = parser.parse_args()

    # Load configuration
    bibli = Bibliotheque(args.config)
    config = bibli.get_config()

    # Command: url
    if args.command == "url":
        downloader = FileDownloader(config['livres_dir'])
        scraper = WebScraper(downloader, max_depth=args.depth, max_files=config['nbmax'])
        scraper.scrape(args.url, depth=0)

    # Command: rapports
    elif args.command == "rapports":
        report_generator = ReportGenerator(config['etats_dir'])
        report_generator.generate_reports()

if __name__ == "__main__":
    main()

""" Pour l'exécuter sur windows, il faut mettre python bibli_partie_3.py url https://math.univ-angers.fr/~jaclin/biblio/livres/ 3
et pour le rapport mettre python bibli_partie_3.py rapports"""





