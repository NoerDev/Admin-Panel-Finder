@echo off
color 0A
cls

:: Hoşgeldiniz mesajı
echo ================================
echo    Welcome to NexVortex
echo ================================
echo Hoşgeldiniz! NoerDeveloper tarafından yapılmıştır.
echo.

:: Python ve pip'in yüklü olup olmadığını kontrol et
echo [INFO] Python kontrol ediliyor...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python yüklü değil! Lütfen Python'u indirip yükleyin: https://www.python.org/downloads/
    pause
    exit /b
)

echo [INFO] Python başarıyla bulundu.

echo [INFO] pip kontrol ediliyor...
pip --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pip yüklü değil! pip yükleniyor...
    python -m ensurepip --upgrade
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] pip kurulumu başarısız oldu!
        pause
        exit /b
    )
    echo [INFO] pip başarıyla yüklendi.
) else (
    echo [INFO] pip başarıyla bulundu.
)

:: İnternet bağlantısını kontrol et
echo [INFO] İnternet bağlantısı kontrol ediliyor...
ping -n 1 google.com >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] İnternet bağlantısı yok! Lütfen internet bağlantınızı kontrol edin.
    pause
    exit /b
) else (
    echo [INFO] İnternet bağlantısı başarıyla tespit edildi.
)

:: Gerekli Python paketlerini yükle
echo [INFO] Gerekli Python paketleri yükleniyor...
pip install --user aiohttp beautifulsoup4 tqdm pyfiglet termcolor
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Paket kurulumu başarısız oldu! Lütfen internet bağlantınızı kontrol edin veya manuel olarak gerekli paketleri yükleyin.
    pause
    exit /b
) else (
    echo [INFO] Gerekli paketler başarıyla yüklendi.
)

:: Python script'ini çalıştır
echo.
echo [INFO] Admin paneli taraması başlatılıyor... 
echo Lütfen bekleyin. Tarama işlemi birkaç dakika sürebilir.
python adminpanel.py
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python script'inde bir hata oluştu! Lütfen hata mesajlarını kontrol edin.
    pause
    exit /b
) else (
    echo [INFO] Admin paneli taraması tamamlandı!
)

:: Programı bitir
echo.
echo [INFO] İşlem başarıyla tamamlandı!
pause
