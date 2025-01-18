import aiohttp
import asyncio
from bs4 import BeautifulSoup
import sys
import os
from urllib.parse import urlparse
import time
import random

# Admin panel yollarını dosyadan okuma fonksiyonu

def load_admin_paths():

    try:

        with open('admin.txt', 'r', encoding='utf-8') as file:

            paths = [line.strip() for line in file if line.strip()]

        return paths

    except FileNotFoundError:

        print(f"{Colors.FAIL}[HATA]{Colors.ENDC} admin.txt dosyası bulunamadı!")

        sys.exit(1)



# common_paths listesini kaldırıp, dosyadan okuma yapacağız

common_paths = load_admin_paths()


# Kullanıcı Arayüzü renkleri için sabitler
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    MAGENTA = '\033[35m'
    RED = '\033[31m'
    YELLOW = '\033[33m'
    WHITE = '\033[37m'
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'
    UNDERLINE = '\033[4m'

def print_banner():
    banner = f"""
{Colors.CYAN}
    ███╗   ██╗███████╗██╗  ██╗██╗   ██╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗
    ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝
    ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝ 
    ██║╚██╗██║██╔══╝   ██╔██╗ ╚██╗ ██╔╝██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗ 
    ██║ ╚████║███████╗██╔╝ ██╗ ╚████╔╝ ╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗
    ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
{Colors.GREEN}╔══════════════════════════════════════════════════════════════════════════╗
║ {Colors.YELLOW}Version: 3.0                                     Developed by: noerdev{Colors.GREEN}     ║
╚══════════════════════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
    print(banner)

# İlerleme çubuğu sınıfı güncellendi
class ProgressBar:
    def __init__(self, total):
        self.total = total
        self.current = 0
        self.bar_width = 40
        self.start_time = time.time()
        
    def update(self):
        self.current += 1
        percentage = (self.current / self.total) * 100
        filled_length = int(self.bar_width * self.current / self.total)
        bar = f"{Colors.GREEN}█{Colors.ENDC}" * filled_length + f"{Colors.WHITE}-{Colors.ENDC}" * (self.bar_width - filled_length)
        
        elapsed_time = time.time() - self.start_time
        speed = self.current / elapsed_time if elapsed_time > 0 else 0
        
        print(f'\r{Colors.BLUE}[{Colors.ENDC} {bar} {Colors.BLUE}]{Colors.ENDC} {Colors.YELLOW}{percentage:6.2f}%{Colors.ENDC} ' + 
              f'{Colors.CYAN}({self.current}/{self.total}){Colors.ENDC} ' +
              f'{Colors.MAGENTA}[{speed:.2f} req/s]{Colors.ENDC}', end='')

# Sonuç özeti sınıfı eklendi
class ScanSummary:
    def __init__(self):
        self.start_time = time.time()
        self.found_panels = []
        self.errors = []
        
    def add_panel(self, panel):
        self.found_panels.append(panel)
        
    def add_error(self, error):
        self.errors.append(error)
        
    def print_summary(self):
        duration = time.time() - self.start_time
        print(f"\n\n{Colors.BOLD}{Colors.BG_BLUE} TARAMA SONUÇLARI {Colors.ENDC}")
        print(f"\n{Colors.CYAN}├─{Colors.ENDC} Toplam Süre: {Colors.GREEN}{duration:.2f} saniye{Colors.ENDC}")
        print(f"{Colors.CYAN}├─{Colors.ENDC} Taranan URL Sayısı: {Colors.GREEN}{len(common_paths)}{Colors.ENDC}")
        print(f"{Colors.CYAN}├─{Colors.ENDC} Bulunan Panel Sayısı: {Colors.GREEN}{len(self.found_panels)}{Colors.ENDC}")
        print(f"{Colors.CYAN}└─{Colors.ENDC} Hata Sayısı: {Colors.RED}{len(self.errors)}{Colors.ENDC}")
        
        if self.found_panels:
            print(f"\n{Colors.BOLD}{Colors.BG_GREEN} BULUNAN PANELLER {Colors.ENDC}")
            for i, panel in enumerate(self.found_panels, 1):
                print(f"\n{Colors.CYAN}[{i}]{Colors.ENDC} {Colors.GREEN}{panel['url']}{Colors.ENDC}")
                print(f"   {Colors.YELLOW}├─{Colors.ENDC} Yanıt Süresi: {panel['response_time']}ms")
                print(f"   {Colors.YELLOW}├─{Colors.ENDC} Durum Kodu: {panel['status_code']}")
                print(f"   {Colors.YELLOW}└─{Colors.ENDC} Başlık: {panel['title']}")

# Asenkron admin paneli arama fonksiyonu
async def find_admin_panel(session, url, path, progress_bar):
    admin_url = f"{url}/{path}"
    try:
        start_time = time.time()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
        }
        
        async with session.get(admin_url, timeout=10, headers=headers, ssl=False) as response:
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            
            if response.status == 200:
                page_content = await response.text()
                soup = BeautifulSoup(page_content, "html.parser")
                
                # Geliştirilmiş kontrol mekanizması
                admin_indicators = [
                    "admin", "login", "dashboard", "yönetim", "panel",
                    "giriş", "kontrol paneli", "yönetici"
                ]
                
                title_match = soup.title and any(indicator in soup.title.string.lower() for indicator in admin_indicators)
                content_match = any(indicator in page_content.lower() for indicator in admin_indicators)
                form_exists = bool(soup.find('form'))
                
                if title_match or (content_match and form_exists):
                    print(f"\n{Colors.GREEN}[BULUNDU]{Colors.ENDC} {admin_url} (Yanıt: {response_time}ms)")
                    return {
                        'url': admin_url,
                        'response_time': response_time,
                        'status_code': response.status,
                        'title': soup.title.string if soup.title else 'Başlık Bulunamadı'
                    }
            
            progress_bar.update()
            
    except Exception as e:
        print(f"\n{Colors.FAIL}[HATA]{Colors.ENDC} {admin_url}: {str(e)}")
    
    return None

# Ana tarama fonksiyonu
async def scan_admin_panels(url):
    print(f"\n{Colors.BLUE}[BİLGİ]{Colors.ENDC} Tarama başlatılıyor: {Colors.UNDERLINE}{url}{Colors.ENDC}\n")
    
    summary = ScanSummary()
    progress_bar = ProgressBar(len(common_paths))
    tasks = []
    
    connector = aiohttp.TCPConnector(limit=50)
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        for path in common_paths:
            task = asyncio.ensure_future(find_admin_panel(session, url, path, progress_bar))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        for result in results:
            if result:
                summary.add_panel(result)
    
    summary.print_summary()
    return summary.found_panels

# URL doğrulama
def validate_url(url):
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        print(f"\n{Colors.BG_RED}[HATA]{Colors.ENDC} Geçerli bir URL girin (örn: https://example.com)")
        sys.exit(1)
    if not parsed_url.netloc:
        print(f"\n{Colors.BG_RED}[HATA]{Colors.ENDC} Geçerli bir alan adı girin.")
        sys.exit(1)
    return parsed_url.scheme + "://" + parsed_url.netloc

# Sonuçları dosyaya kaydetme
def save_to_file(admin_panels, url):
    if not admin_panels:
        return
        
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    file_name = f"admin_panels_{urlparse(url).netloc}_{timestamp}.txt"
    
    with open(file_name, "w", encoding='utf-8') as file:
        file.write(f"Tarama Tarihi: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"Hedef URL: {url}\n")
        file.write("-" * 50 + "\n\n")
        
        for panel in admin_panels:
            file.write(f"URL: {panel['url']}\n")
            file.write(f"Yanıt Süresi: {panel['response_time']}ms\n")
            file.write(f"Durum Kodu: {panel['status_code']}\n")
            file.write(f"Sayfa Başlığı: {panel['title']}\n")
            file.write("-" * 30 + "\n")
    
    print(f"\n{Colors.GREEN}[BAŞARILI]{Colors.ENDC} Sonuçlar '{file_name}' dosyasına kaydedildi.")

# Ekranı temizleme fonksiyonu
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

# Ana fonksiyon
async def main():
    clear_screen()
    print_banner()
    
    while True:
        print(f"\n{Colors.BOLD}{Colors.BG_BLUE} ADMIN PANEL TARAYICI {Colors.ENDC}")
        print(f"\n{Colors.CYAN}[?]{Colors.ENDC} Hedef URL girin (örn: https://example.com)")
        print(f"{Colors.CYAN}[?]{Colors.ENDC} Çıkmak için 'q' tuşuna basın")
        print(f"{Colors.CYAN}{'─' * 50}{Colors.ENDC}")
        
        target_url = input(f"\n{Colors.GREEN}┌──({Colors.CYAN}NexVortex{Colors.GREEN}){Colors.WHITE}-[{Colors.YELLOW}~/admin-scanner{Colors.WHITE}]\n{Colors.GREEN}└─$ {Colors.ENDC}").strip()

        if target_url.lower() == 'q':
            print(f"\n{Colors.BLUE}[BİLGİ]{Colors.ENDC} Program sonlandırılıyor...")
            print(f"{Colors.CYAN}İyi günler dileriz!{Colors.ENDC}")
            break

        try:
            url = validate_url(target_url)
            admin_panels = await scan_admin_panels(url)
            save_to_file(admin_panels, url)
            
        except Exception as e:
            print(f"\n{Colors.BG_RED}[HATA]{Colors.ENDC} {str(e)}")
        
        input(f"\n{Colors.BLUE}[BİLGİ]{Colors.ENDC} Devam etmek için Enter'a basın...")
        clear_screen()
        print_banner()

# Programı başlatma
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BLUE}[BİLGİ]{Colors.ENDC} Program kullanıcı tarafından sonlandırıldı.")
        print(f"{Colors.CYAN}İyi günler dileriz!{Colors.ENDC}")
        sys.exit(0)
