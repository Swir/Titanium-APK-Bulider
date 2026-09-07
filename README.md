<div align="center">

# 📱 Titanium APK Builder

**HTML / CSS / JavaScript → Android APK automation GUI**  
**Automatyczny kreator aplikacji Android z projektów HTML / CSS / JavaScript**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Cordova](https://img.shields.io/badge/Apache-Cordova-E8E8E8?logo=apachecordova&logoColor=black)
![Android](https://img.shields.io/badge/Android-APK-3DDC84?logo=android&logoColor=white)
![UI](https://img.shields.io/badge/UI-CustomTkinter-8A2BE2)
![Author](https://img.shields.io/badge/Author-Swir-ff4fa3)

</div>

---

## 🇬🇧 English

Titanium APK Builder is a Python GUI automation tool for turning HTML/CSS/JavaScript projects into Android applications using Apache Cordova. It automates repetitive project setup and build steps and provides convenient controls for application identity, graphics and Android-oriented options.

### ✨ Highlights
- modern CustomTkinter GUI
- Cordova project/build automation
- HTML/CSS/JS project input
- icon processing with Pillow
- Android splash-screen helper/injection workflow
- Android hardware/plugin options
- status-bar theming
- automatic Android package-name generation
- Debug/Release-oriented build workflow

### 🛠 Prerequisites
A working Android/Cordova build environment is required. Depending on your setup this normally includes Python, Node.js, Apache Cordova, JDK, Android SDK/Android Studio and Gradle.

Python dependencies:
```bash
pip install customtkinter Pillow
```

Run the version currently included in this repository:
```bash
python "Titanium V9.py"
```

Select a web-project directory containing `index.html`, configure the application and start the build from the GUI.

---

## 🇵🇱 Polski

Titanium APK Builder to graficzne narzędzie automatyzujące tworzenie aplikacji Android z projektów HTML/CSS/JavaScript przy użyciu Apache Cordova. Program upraszcza powtarzalne etapy konfiguracji i kompilacji oraz udostępnia wygodne opcje dotyczące nazwy aplikacji, grafiki i ustawień Androida.

### ✨ Najważniejsze funkcje
- nowoczesny interfejs CustomTkinter
- automatyzacja projektów i kompilacji Cordova
- obsługa projektów HTML/CSS/JS
- przetwarzanie ikon przez Pillow
- mechanizm pomocniczy dla splash screen Android
- opcje pluginów/uprawnień sprzętowych
- ustawianie wyglądu paska statusu
- automatyczne generowanie nazwy pakietu Android
- workflow dla kompilacji Debug/Release

### 🛠 Wymagania
Potrzebne jest działające środowisko kompilacji Android/Cordova. Zależnie od konfiguracji obejmuje ono zwykle Python, Node.js, Apache Cordova, JDK, Android SDK/Android Studio oraz Gradle.

Zależności Pythona:
```bash
pip install customtkinter Pillow
```

Uruchomienie wersji znajdującej się obecnie w repozytorium:
```bash
python "Titanium V9.py"
```

Wskaż katalog projektu zawierający `index.html`, skonfiguruj aplikację i uruchom proces budowania z poziomu GUI.

---

## 📁 Repository / Repozytorium
```text
Titanium-APK-Bulider/
├── Titanium V9.py
└── README.md
```

## ⚠️ Notes / Uwagi
Android toolchains change over time. If a build fails, verify that Cordova, JDK, Android SDK Build Tools and Gradle versions are mutually compatible.

Środowisko Android zmienia się z czasem. W razie problemów sprawdź zgodność wersji Cordova, JDK, Android SDK Build Tools i Gradle.

## 👤 Author / Autor
Developed by **Swir**.
