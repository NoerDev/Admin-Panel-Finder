import asyncio
import aiohttp
from bs4 import BeautifulSoup
import sys
import os
from urllib.parse import urlparse
import time
import random
from tqdm import tqdm  # Burada tqdm'yi normal olarak kullanıyoruz, asyncio ile uyumlu
import pyfiglet
from termcolor import colored

# Admin panel yollarını bir dosyadan okuma
def load_paths_from_file(file_name="adminpanel.txt"):
    if not os.path.exists(file_name):
        print(f"\033[91m[ERROR] '{file_name}' dosyası bulunamadı. Lütfen admin panel yollarını içeren bir dosya sağlamak için 'adminpanel.txt' dosyasını oluşturun.\033[0m")
        sys.exit(1)

    with open(file_name, "r") as file:
        # Dosyadaki her bir yolu satır satır oku ve listeye ekle
        paths = [line.strip() for line in file.readlines() if line.strip()]
    
    return paths

# Asenkron admin paneli arama fonksiyonu
async def find_admin_panel(session, url, path):
    admin_url = f"{url}/{path}"
    try:
        start_time = time.time()  # Zaman ölçümünü başlat
        async with session.get(admin_url, timeout=10) as response:
            end_time = time.time()  # Zaman ölçümünü sonlandır
            response_time = round((end_time - start_time) * 1000, 2)  # Yanıt süresi (ms)
            
            # Terminalde her bir URL'yi ve süresini yazdır
            if response.status == 200:
                page_content = await response.text()
                soup = BeautifulSoup(page_content, "html.parser")
                
                # Başlık dışında başka kriterlere de bakabiliriz (örneğin admin paneline dair metin araması)
                if soup.title and "admin" in soup.title.string.lower():
                    print(f"\033[92m[OK] {admin_url} (Yanıt süresi: {response_time}ms)\033[0m")
                    return admin_url
                elif "admin" in page_content.lower():  # Sayfa içeriğinde admin kelimesi var mı kontrolü
                    print(f"\033[92m[OK] {admin_url} (Yanıt süresi: {response_time}ms)\033[0m")
                    return admin_url
            print(f"\033[91m[FAIL] {admin_url} (Yanıt süresi: {response_time}ms)\033[0m")
    except asyncio.TimeoutError:
        print(f"\033[91m[ERROR] Zaman aşımı: {admin_url}\033[0m")
    except Exception as e:
        print(f"\033[91m[ERROR] Hata oluştu: {e}\033[0m")
    return None

# Ana tarama fonksiyonu
async def scan_admin_panels(url, paths):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for path in paths:
            task = asyncio.ensure_future(find_admin_panel(session, url, path))
            tasks.append(task)

        # Sonuçları bekliyoruz
        admin_panels = await asyncio.gather(*tasks)

    return [panel for panel in admin_panels if panel]

# URL doğrulama
def validate_url(url):
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        print("\033[91m[ERROR] Geçerli bir URL girin (örn. https://example.com).\033[0m")
        sys.exit(1)
    if not parsed_url.netloc:
        print("\033[91m[ERROR] Geçerli bir alan adı girin.\033[0m")
        sys.exit(1)
    return parsed_url.scheme + "://" + parsed_url.netloc

# Çıktıyı dosyaya kaydetme
def save_to_file(admin_panels, url):
    if not admin_panels:
        print("\033[91m[INFO] Admin paneli bulunamadı.\033[0m\n")
        return
    file_name = f"admin_panels_{urlparse(url).netloc}.txt"
    with open(file_name, "w") as file:
        for panel in admin_panels:
            file.write(panel + "\n")
    print(f"\033[94m[INFO] Bulunan admin panelleri '{file_name}' dosyasına kaydedildi.\033[0m\n")

# Animasyonlu "Hoşgeldiniz" Mesajı
def welcome_animation():
    welcome_text = "Welcome to NexVortex"
    clear_screen()
    print("\033[94m")  # Mavi renk
    for i in range(3):
        for c in welcome_text:
            print(f"\033[92m{c}\033[0m", end='', flush=True)
            time.sleep(0.1)  # Karakterler arasında kısa bir gecikme
        print()
        time.sleep(0.3)  # Bir süre bekle
        clear_screen()

    print("\033[92m[INFO] Giriş Başarılı!\033[0m\n")
    time.sleep(0.5)
    clear_screen()

# Ekranı temizleme fonksiyonu
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

# Kullanıcıdan hedef URL alma
async def get_target_url():
    target_url = input("\033[94mHedef web sitesinin URL'sini girin (örn. https://example.com) veya çıkmak için 'q' tuşlayın: \033[0m").strip()
    return target_url

# İlerleme çubuğu ile admin panel tarama fonksiyonu
async def run_with_progress_bar(url, paths):
    total = len(paths)
    admin_panels = []

    # Asenkron ilerleme çubuğu kullanımı
    with tqdm(total=total, desc="Admin Panel Tarama", ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} ({percentage:3.0f}%)") as progress_bar:
        async with aiohttp.ClientSession() as session:
            for path in paths:
                admin_url = await find_admin_panel(session, url, path)
                if admin_url:
                    admin_panels.append(admin_url)
                progress_bar.update(1)  # Her bir URL tarandıkça ilerleme çubuğunu güncelle
    return admin_panels

# Ana fonksiyon
async def main():
    welcome_animation()  # Hacker temalı animasyonlu hoşgeldiniz mesajı

    # Admin panel yollarını dosyadan yükle
    paths = load_paths_from_file()

    while True:
        target_url = await get_target_url()

        if target_url.lower() == 'q':
            print("\033[94m[INFO] Çıkılıyor...\033[0m")
            break  # Programı sonlandır

        url = validate_url(target_url)

        print("\033[94m[INFO] Tarama başlatılıyor... Lütfen bekleyin.\033[0m\n")
        admin_panels = await run_with_progress_bar(url, paths)

        if admin_panels:
            print("\033[92m[OK] Bulunan admin panelleri:\033[0m")
            for panel in admin_panels:
                print(f"\033[92m[OK] {panel}\033[0m")
        else:
            print("\033[91m[INFO] Admin paneli bulunamadı.\033[0m\n")

        # Sonuçları dosyaya kaydet
        save_to_file(admin_panels, url)

# Programı başlatma
if __name__ == "__main__":
    asyncio.run(main())
