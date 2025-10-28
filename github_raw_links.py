import requests
import argparse
from urllib.parse import urljoin
import sys

class GitHubRawLinkGenerator:
    def __init__(self):
        self.base_url = "https://api.github.com/repos/"
        self.raw_base_url = "https://raw.githubusercontent.com/"
    
    def get_repo_contents(self, username, repo_name, path="", branch="main"):
        """GitHub reposundaki dosya ve klasörleri recursive olarak getirir"""
        url = f"{self.base_url}{username}/{repo_name}/contents/{path}"
        print(f"API'ye bağlanılıyor: {url}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Hata: {e}")
            return None
    
    def should_include_file(self, file_path):
        """Dosyanın include edilip edilmeyeceğine karar verir"""
        # .pyc dosyalarını ve __pycache__ klasörlerini filtrele
        excluded_extensions = ['.pyc', '.pyo']
        excluded_folders = ['__pycache__']
        
        # Dosya uzantısını kontrol et
        if any(file_path.endswith(ext) for ext in excluded_extensions):
            return False
        
        # Klasör yolunu kontrol et
        if any(folder in file_path.split('/') for folder in excluded_folders):
            return False
        
        return True
    
    def generate_raw_links(self, username, repo_name, branch="main", path=""):
        """Tüm dosyalar için raw link oluşturur"""
        contents = self.get_repo_contents(username, repo_name, path, branch)
        
        if contents is None:
            return []
        
        raw_links = []
        
        for item in contents:
            if item['type'] == 'file':
                # Dosya filtreleme kontrolü
                if self.should_include_file(item['path']):
                    raw_link = f"{self.raw_base_url}{username}/{repo_name}/{branch}/{item['path']}"
                    raw_links.append(raw_link)
                    print(f"Bulundu: {raw_link}")
                else:
                    print(f"Filtrelendi: {item['path']}")
                    
            elif item['type'] == 'dir':
                # Klasör filtreleme kontrolü
                if self.should_include_file(item['path']):
                    print(f"Klasör taranıyor: {item['name']}")
                    sub_links = self.generate_raw_links(username, repo_name, branch, item['path'])
                    raw_links.extend(sub_links)
                else:
                    print(f"Klasör filtrelendi: {item['name']}")
        
        return raw_links

def main():
    parser = argparse.ArgumentParser(description='GitHub reposundaki tüm dosyaların raw linklerini çıkarır')
    parser.add_argument('username', help='GitHub kullanıcı adı')
    parser.add_argument('repo', help='Repository adı')
    parser.add_argument('--branch', default='main', help='Branch adı (varsayılan: main)')
    parser.add_argument('--exclude-py-cache', action='store_true', help='__pycache__ klasörlerini ve .pyc dosyalarını hariç tut')
    
    args = parser.parse_args()
    
    print(f"GitHub Raw Link Generator")
    print(f"Kullanıcı: {args.username}")
    print(f"Repo: {args.repo}")
    print(f"Branch: {args.branch}")
    print(f"__pycache__ filtreleniyor: {args.exclude_py_cache}")
    print("-" * 50)
    
    generator = GitHubRawLinkGenerator()
    
    # Eğer exclude-py-cache flag'i verilmişse, filtreleme yap
    if args.exclude_py_cache:
        generator.should_include_file = lambda path: not (path.endswith('.pyc') or 
                                                         path.endswith('.pyo') or 
                                                         '__pycache__' in path.split('/'))
    
    raw_links = generator.generate_raw_links(args.username, args.repo, args.branch)
    
    print("\n" + "=" * 50)
    print(f"TOPLAM {len(raw_links)} DOSYA BULUNDU:")
    print("=" * 50)
    
    for link in raw_links:
        print(link)

if __name__ == "__main__":
    main()