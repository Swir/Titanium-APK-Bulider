

```markdown
# 📱 Titanium APK Builder (HTML to Android) 
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Cordova](https://img.shields.io/badge/Cordova-13.0+-lightgrey.svg)
![Android](https://img.shields.io/badge/Android-Ready-green.svg)
![License](https://img.shields.io/badge/License-MIT-orange.svg)

> 🌍 **Languages:** [English](#-english-version) | [Polski](#-wersja-polska)

---

## 🇬🇧 English Version

### 🚀 About The Project
**Titanium APK Builder** is a powerful, GUI-based Python automation tool that instantly converts any HTML/CSS/JS web project into a fully functional, native Android application (.apk). 

Powered by **Apache Cordova** under the hood, it eliminates the need to manually write configuration files or use CLI commands. It features a **Smart Image Engine** that automatically resizes your icons, and a **Web Splash Injector** that bypasses Android 12+ splash screen restrictions by injecting a beautiful CSS/JS loader directly into your DOM!

### ✨ Key Features
* **Modern GUI:** Built with `customtkinter` for a sleek, dark-mode experience.
* **Smart Image Processing:** Select *any* image format (JPG, WEBP, PNG). The built-in engine (Pillow) auto-crops it to a 512x512 transparent icon.
* **Android 12+ Splash Screen Fix:** Automatically injects a fade-out CSS loader into your `index.html` to prevent the ugly default white Android splash screen.
* **Hardware Permissions:** 1-click injection of Cordova plugins (Camera, GPS, Storage).
* **Status Bar Theming:** Input a HEX color to dynamically tint the Android status bar to match your web app's background.
* **Auto-Package Generator:** Cleans your app name and auto-generates a valid Android package name (e.g., `com.yourname.app`).

### 🛠️ Prerequisites (Crucial Step)
To build Android apps, your system needs the underlying engines installed. Ensure you have the following:

1.  **Node.js** (v24 or newer)
2.  **Apache Cordova** (Install via terminal: `npm install -g cordova`)
3.  **Java JDK 17** (Adoptium Temurin recommended. *Note: Ensure `JAVA_HOME` is set during installation!*)
4.  **Android Studio** (Install the SDK, and specifically **SDK Build-Tools 35.0.0** via the SDK Manager).
5.  **Gradle** (v8.x or v9.x).

**⚠️ Windows Environment Variables Setup:**
You must add the following paths to your Windows `Path` variable:
* `%ANDROID_HOME%\platform-tools`
* `%ANDROID_HOME%\cmdline-tools\latest\bin`
* `C:\Path\To\Your\gradle\bin`

### 📦 Installation & Usage
1. Clone this repository:
   ```bash
   git clone https://github.com/YourUsername/titanium-apk-builder.git
   cd titanium-apk-builder

```

2. Install required Python libraries:
```bash
pip install customtkinter Pillow

```


3. Run the application:
```bash
python main.py

```


4. **How to use:** Select your project folder (it **MUST** contain an `index.html` file), pick an icon, select your build type (Debug/Release), and click Generate! The app will open the output folder once compilation is complete.

---

## 🇵🇱 Wersja Polska

### 🚀 O Projekcie

**Titanium APK Builder** to potężne narzędzie z graficznym interfejsem (GUI) napisane w Pythonie, które błyskawicznie konwertuje dowolny projekt webowy (HTML/CSS/JS) w pełnoprawną, natywną aplikację na Androida (.apk).

Program bazuje na silniku **Apache Cordova**, ale całkowicie eliminuje konieczność ręcznej zabawy w terminalu. Wyposażony jest w **Smart Image Engine**, który sam docina ikony, oraz **Web Splash Injector**, który omija blokady ekranów powitalnych w systemie Android 12+, wstrzykując piękny, animowany ekran ładowania prosto do Twojego kodu!

### ✨ Główne Funkcje

* **Nowoczesny Interfejs:** Zbudowany w oparciu o `customtkinter` (ciemny motyw).
* **Inteligentne Przetwarzanie Grafik:** Wybierz *dowolny* format (JPG, WEBP, PNG). Silnik (Pillow) sam wykadruje obraz do idealnej ikony 512x512.
* **Fix na Splash Screen (Android 12+):** Automatycznie wstrzykuje animowany "spinner" (CSS/JS) do pliku `index.html`, eliminując brzydki, domyślny biały ekran Androida.
* **Uprawnienia Sprzętowe:** Dodawaj obsługę aparatu, GPS i pamięci jednym kliknięciem (automatyczne pobieranie wtyczek).
* **Kolorowanie Paska Statusu:** Wpisz kod HEX, aby górny pasek telefonu (tam gdzie bateria) przyjął kolor Twojej aplikacji.
* **Auto-Generator Pakietów:** Program sam czyści nazwę apki i tworzy poprawny pakiet (np. `com.twojanazwa.apka`).

### 🛠️ Wymagania Systemowe (Bardzo Ważne)

Aby Python mógł zbudować aplikację, Twój system (Windows) musi posiadać zainstalowane poniższe silniki:

1. **Node.js** (v24 lub nowszy)
2. **Apache Cordova** (Zainstaluj w terminalu wpisując: `npm install -g cordova`)
3. **Java JDK 17** (Zalecane Adoptium Temurin. *Uwaga: Upewnij się, że zaznaczyłeś opcję dodania `JAVA_HOME` podczas instalacji!*)
4. **Android Studio** (Zainstaluj SDK, a w szczególności **SDK Build-Tools w wersji 35.0.0** w menedżerze SDK).
5. **Gradle** (wersja 8.x lub 9.x).

**⚠️ Zmienne Środowiskowe (Windows):**
Musisz dodać poniższe ścieżki do zmiennej systemowej `Path`:

* `%ANDROID_HOME%\platform-tools`
* `%ANDROID_HOME%\cmdline-tools\latest\bin`
* `C:\Ścieżka\Do\Twojego\gradle\bin`

### 📦 Instalacja i Uruchomienie

1. Pobierz repozytorium:
```bash
git clone https://github.com/TwójNick/titanium-apk-builder.git
cd titanium-apk-builder

```


2. Zainstaluj wymagane biblioteki Pythona:
```bash
pip install customtkinter Pillow

```


3. Uruchom program:
```bash
python main.py

```


4. **Jak używać:** Wybierz folder z projektem (folder **MUSI** zawierać plik `index.html`), wybierz dowolną grafikę na ikonę, wybierz rodzaj kompilacji (Debug/Release) i kliknij "Generuj". Gdy proces dobiegnie końca, program sam otworzy folder z gotowym plikiem APK!

