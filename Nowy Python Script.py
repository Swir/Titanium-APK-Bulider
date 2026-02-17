import os
import shutil
import subprocess
import threading
import re
import platform
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageOps

# --- USTAWIENIA MOTYWU TITANIUM ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class TitaniumApkBuilder(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Titanium APK Builder by Swir (v8.4 - Core Interceptor)")
        self.geometry("1100x820")
        self.resizable(False, False)

        self.html_folder_path = ""
        self.icon_file_path = ""

        self.create_widgets()

    def create_widgets(self):
        # GŁÓWNY BRANDING TITANIUM BY SWIR
        self.header = ctk.CTkLabel(self, text="💎 Titanium APK Builder by Swir", font=ctk.CTkFont(size=30, weight="bold", slant="italic"))
        self.header.grid(row=0, column=0, columnspan=2, pady=(15, 15))

        # --- KOLUMNA LEWA: USTAWIENIA PROJEKTU ---
        self.frame_left = ctk.CTkFrame(self, width=520, height=520)
        self.frame_left.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.frame_left.grid_propagate(False)

        ctk.CTkLabel(self.frame_left, text="1. Konfiguracja Projektu", font=ctk.CTkFont(weight="bold", size=16)).pack(anchor="w", pady=(10, 5), padx=15)
        
        self.entry_name = ctk.CTkEntry(self.frame_left, width=470, placeholder_text="Nazwa (np. Titanium App)")
        self.entry_name.pack(pady=5, padx=15)

        frame_pkg = ctk.CTkFrame(self.frame_left, fg_color="transparent")
        frame_pkg.pack(fill="x", padx=15, pady=5)
        self.entry_package = ctk.CTkEntry(frame_pkg, width=340, placeholder_text="Pakiet (np. com.swir.app)")
        self.entry_package.pack(side="left")
        ctk.CTkButton(frame_pkg, text="🎲 Auto", width=110, command=self.auto_generate_package).pack(side="right")

        frame_versions = ctk.CTkFrame(self.frame_left, fg_color="transparent")
        frame_versions.pack(fill="x", padx=15, pady=5)
        self.entry_version = ctk.CTkEntry(frame_versions, width=220, placeholder_text="Wersja (np. 1.0.0)")
        self.entry_version.insert(0, "1.0.0")
        self.entry_version.pack(side="left")
        
        self.entry_version_code = ctk.CTkEntry(frame_versions, width=220, placeholder_text="Version Code (np. 1)")
        self.entry_version_code.insert(0, "1")
        self.entry_version_code.pack(side="right")

        ctk.CTkLabel(self.frame_left, text="2. Wygląd Natywny", font=ctk.CTkFont(weight="bold", size=16)).pack(anchor="w", pady=(20, 5), padx=15)

        self.chk_nativizer = ctk.CTkCheckBox(self.frame_left, text="🛡️ Włącz 'Nativizer' (Blokuje zaznaczanie tekstu WWW)", onvalue=True, offvalue=False)
        self.chk_nativizer.select()
        self.chk_nativizer.pack(anchor="w", padx=15, pady=10)

        ctk.CTkLabel(self.frame_left, text="3. Tryb Kompilacji", font=ctk.CTkFont(weight="bold", size=16)).pack(anchor="w", pady=(20, 5), padx=15)
        self.combo_build_type = ctk.CTkComboBox(self.frame_left, values=["Debug (Szybki Build / Testy)", "Release (Wersja Produkcyjna)"], width=470)
        self.combo_build_type.pack(pady=5, padx=15)

        # --- KOLUMNA PRAWA: PLIKI I WTYCZKI ---
        self.frame_right = ctk.CTkFrame(self, width=520, height=520)
        self.frame_right.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        self.frame_right.grid_propagate(False)

        ctk.CTkLabel(self.frame_right, text="4. Zasoby", font=ctk.CTkFont(weight="bold", size=16)).pack(anchor="w", pady=(10, 5), padx=15)
        
        btn_frame1 = ctk.CTkFrame(self.frame_right, fg_color="transparent")
        btn_frame1.pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(btn_frame1, text="📁 Folder HTML", width=180, command=self.select_html).pack(side="left")
        self.lbl_html = ctk.CTkLabel(btn_frame1, text="❌ Brak")
        self.lbl_html.pack(side="left", padx=15)

        btn_frame2 = ctk.CTkFrame(self.frame_right, fg_color="transparent")
        btn_frame2.pack(fill="x", padx=15, pady=5)
        ctk.CTkButton(btn_frame2, text="🖼️ Ikona Appki", width=180, command=self.select_icon).pack(side="left")
        self.lbl_icon = ctk.CTkLabel(btn_frame2, text="ℹ️ Domyślna")
        self.lbl_icon.pack(side="left", padx=15)

        ctk.CTkLabel(self.frame_right, text="5. Funkcje Titanium", font=ctk.CTkFont(weight="bold", size=16)).pack(anchor="w", pady=(20, 5), padx=15)
        self.chk_web_splash = ctk.CTkCheckBox(self.frame_right, text="✨ Wstrzyknij Webowy Splash Screen", onvalue=True, offvalue=False)
        self.chk_web_splash.select()
        self.chk_web_splash.pack(anchor="w", padx=15, pady=5)
        
        # PANCERNY DOWNLOADER V4.1 (KRADZIEŻ FUNKCJI CLICK)
        self.chk_downloader = ctk.CTkCheckBox(self.frame_right, text="📥 Wymuś pobieranie plików (Core Interceptor & Native Share)", onvalue=True, offvalue=False)
        self.chk_downloader.select()
        self.chk_downloader.pack(anchor="w", padx=15, pady=5)

        ctk.CTkLabel(self.frame_right, text="6. Wtyczki Androida", font=ctk.CTkFont(weight="bold", size=16)).pack(anchor="w", pady=(20, 5), padx=15)
        self.chk_camera = ctk.CTkCheckBox(self.frame_right, text="Aparat")
        self.chk_camera.pack(anchor="w", padx=15, pady=5)
        self.chk_gps = ctk.CTkCheckBox(self.frame_right, text="Lokalizacja (GPS)")
        self.chk_gps.pack(anchor="w", padx=15, pady=5)
        self.chk_storage = ctk.CTkCheckBox(self.frame_right, text="Pamięć urządzenia")
        self.chk_storage.select() 
        self.chk_storage.pack(anchor="w", padx=15, pady=5)

        # --- SEKCJA DOLNA (HACKER TERMINAL) ---
        self.frame_bottom = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_bottom.grid(row=2, column=0, columnspan=2, padx=20, pady=(5, 10), sticky="ew")

        self.btn_build = ctk.CTkButton(self.frame_bottom, text="⚡ ROZPOCZNIJ BUDOWĘ TITANIUM", font=ctk.CTkFont(size=22, weight="bold"), height=55, fg_color="#27AE60", hover_color="#1E8449", command=self.start_build_thread)
        self.btn_build.pack(fill="x", pady=5)

        self.progress = ctk.CTkProgressBar(self.frame_bottom, height=15)
        self.progress.set(0)
        self.progress.pack(fill="x", pady=(5, 5))

        self.console = ctk.CTkTextbox(self.frame_bottom, height=130, state="disabled", font=ctk.CTkFont(family="Consolas", size=12))
        self.console.pack(fill="x")

    def auto_generate_package(self):
        app_name = self.entry_name.get().strip()
        if not app_name: app_name = "titaniumapp"
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', app_name).lower()
        self.entry_package.delete(0, "end")
        self.entry_package.insert(0, f"com.swir.{clean_name}")

    def select_html(self):
        folder = filedialog.askdirectory()
        if folder: self.html_folder_path = folder; self.lbl_html.configure(text=f"✅ ...{folder[-20:]}")
    def select_icon(self):
        file = filedialog.askopenfilename(filetypes=[("Obrazy", "*.png *.jpg *.jpeg *.webp *.bmp")])
        if file: self.icon_file_path = file; self.lbl_icon.configure(text=f"✅ ...{file[-20:]}")

    def log(self, text):
        self.after(0, self._append_log, text)

    def _append_log(self, text):
        self.console.configure(state="normal")
        self.console.insert("end", text + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def run_cmd_live(self, command, cwd=None):
        process = subprocess.Popen(command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
        for line in process.stdout:
            self.log("   " + line.strip())
        process.wait()
        if process.returncode != 0:
            raise Exception(f"Komenda wywaliła błąd: {command}")

    # --- MAGIA WTRYSKIWACZY TITANIUM (CORE INTERCEPTOR) ---
    def inject_titanium_features(self, index_html_path):
        self.log("💉 Wstrzykiwanie funkcji Titanium oraz zabezpieczeń do HTML...")
        try:
            with open(index_html_path, "r", encoding="utf-8") as f: html = f.read()
            
            if "cordova.js" not in html.lower():
                self.log("   -> Wstrzykuję wymagany skrypt silnika (cordova.js)...")
                html = re.sub(r'(</body>)', r'<script src="cordova.js"></script>\n\1', html, flags=re.IGNORECASE)

            nativizer_css = ""
            if self.chk_nativizer.get():
                nativizer_css = """
                <style>
                    /* TITANIUM NATIVIZER */
                    body, html { user-select: none; -webkit-user-select: none; -webkit-touch-callout: none; -webkit-tap-highlight-color: transparent; }
                </style>
                """

            splash_code = ""
            if self.chk_web_splash.get():
                splash_code = """
                <style>
                    #t-splash { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: #121212; z-index: 9999999; display: flex; flex-direction: column; justify-content: center; align-items: center; transition: opacity 0.5s ease-out; }
                    .t-spin { width: 50px; height: 50px; border: 5px solid rgba(255, 255, 255, 0.1); border-top-color: #27AE60; border-radius: 50%; animation: t-spin 1s linear infinite; margin-top: 30px; }
                    @keyframes t-spin { 100% { transform: rotate(360deg); } }
                </style>
                <div id="t-splash">
                    <img src="icon.png" width="120" style="border-radius: 25px; box-shadow: 0px 8px 25px rgba(0,0,0,0.6);">
                    <div class="t-spin"></div>
                </div>
                <script>
                    let splashDone = false;
                    function removeSplash() {
                        if(splashDone) return;
                        splashDone = true;
                        let s = document.getElementById('t-splash');
                        if(s) { s.style.opacity = '0'; setTimeout(() => s.remove(), 500); }
                    }
                    document.addEventListener('deviceready', () => setTimeout(removeSplash, 2000), false);
                    setTimeout(removeSplash, 4000);
                </script>
                """

            # TITANIUM NATIVE DOWNLOADER V4.1 (KRADZIEŻ .click())
            downloader_code = ""
            if self.chk_downloader.get():
                self.log("   -> Instalowanie Agenta Pobierania (Przechwytywanie skryptów jsPDF)...")
                downloader_code = """
                <script>
                    /* TITANIUM CORE INTERCEPTOR V4.1 BY SWIR */
                    function titaniumShareNatively(url, fileName) {
                        if (window.plugins && window.plugins.socialsharing) {
                            if (url.startsWith('data:')) {
                                window.plugins.socialsharing.share('Pobrano plik: ' + fileName, fileName, url, null);
                            } else if (url.startsWith('blob:')) {
                                fetch(url).then(r => r.blob()).then(blob => {
                                    let reader = new FileReader();
                                    reader.onloadend = function() {
                                        window.plugins.socialsharing.share('Pobrano plik: ' + fileName, fileName, reader.result, null);
                                    }
                                    reader.readAsDataURL(blob);
                                });
                            } else if (url.startsWith('http')) {
                                window.open(url, '_system');
                            }
                        } else {
                            alert('Trwa ładowanie wtyczek systemowych... Spróbuj ponownie za chwilę.');
                        }
                    }

                    // 1. Klasyczne kliknięcia palcem w link
                    document.addEventListener('click', function(e) {
                        let target = e.target.closest('a[download]');
                        if(target) {
                            e.preventDefault();
                            titaniumShareNatively(target.href, target.getAttribute('download') || 'dokument.pdf');
                        }
                    });

                    // 2. KILER-FEATURE: Przechwytywanie programistycznych kliknięć (doc.save z jsPDF)
                    const originalClick = HTMLAnchorElement.prototype.click;
                    HTMLAnchorElement.prototype.click = function() {
                        // Jeśli kod JS na stronie próbuje kliknąć w link pobierający (jak robi to jsPDF)
                        if (this.hasAttribute('download') || this.download) {
                            let fName = this.getAttribute('download') || this.download || 'dokument.pdf';
                            titaniumShareNatively(this.href, fName);
                            return; // CAŁKOWICIE BLOKUJEMY oryginalne "zepsute" kliknięcie Androida
                        }
                        originalClick.call(this); // Jeśli to zwykły link (nie pobieranie), pozwalamy mu działać
                    };
                </script>
                """

            injections = nativizer_css + splash_code + downloader_code
            if injections:
                html = re.sub(r'(<body[^>]*>)', r'\1\n' + injections, html, count=1, flags=re.IGNORECASE)
            
            with open(index_html_path, "w", encoding="utf-8") as f: f.write(html)
        except Exception as e:
            self.log(f"❌ Błąd wstrzykiwania: {e}")

    # --- LOGIKA BUDOWANIA W TLE ---
    def start_build_thread(self):
        if not self.entry_name.get() or not self.entry_package.get() or not self.html_folder_path:
            messagebox.showwarning("Braki!", "Uzupełnij nazwę, pakiet i wybierz folder HTML!")
            return
        if not os.path.exists(os.path.join(self.html_folder_path, "index.html")):
            messagebox.showerror("Błąd", "W folderze brakuje pliku 'index.html'!")
            return

        self.btn_build.configure(state="disabled", text="⏳ TITANIUM W AKCJI...")
        self.progress.set(0)
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")
        threading.Thread(target=self.build_apk).start()

    def build_apk(self):
        app_name = self.entry_name.get().strip()
        package_name = self.entry_package.get().strip()
        app_version = self.entry_version.get().strip() or "1.0.0"
        app_version_code = self.entry_version_code.get().strip() or "1"
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_folder = os.path.join(script_dir, f"{app_name}_Android")

        try:
            self.log(f"🚀 INICJALIZACJA: {app_name} (v{app_version} / kod {app_version_code})")
            self.progress.set(0.1)
            
            self.log("\n[1/5] Budowa struktury i import HTML...")
            if os.path.exists(project_folder): shutil.rmtree(project_folder)
            subprocess.run(f'cordova create "{app_name}_Android" {package_name} "{app_name}"', shell=True, check=True, cwd=script_dir, capture_output=True)
            
            www_dir = os.path.join(project_folder, "www")
            shutil.rmtree(www_dir)
            shutil.copytree(self.html_folder_path, www_dir)
            self.progress.set(0.2)

            self.log("\n[2/5] Grafiki i system Nativizer...")
            xml_injections = ""
            if self.icon_file_path:
                icon_path = os.path.join(project_folder, "icon.png")
                img = Image.open(self.icon_file_path).convert("RGBA")
                img = ImageOps.fit(img, (512, 512), Image.Resampling.LANCZOS)
                img.save(icon_path, "PNG")
                xml_injections += '    <icon src="icon.png" />\n'
                shutil.copy2(icon_path, os.path.join(www_dir, "icon.png"))

            xml_injections += '    <preference name="AndroidWindowSplashScreenBackground" value="#121212" />\n'
            
            self.inject_titanium_features(os.path.join(www_dir, "index.html"))

            self.log("\n[3/5] Podłączanie wtyczek systemowych Javy...")
            self.progress.set(0.4)
            
            if self.chk_downloader.get():
                self.run_cmd_live("cordova plugin add cordova-plugin-x-socialsharing", cwd=project_folder)
                self.run_cmd_live("cordova plugin add cordova-plugin-inappbrowser", cwd=project_folder)

            if self.chk_camera.get(): subprocess.run("cordova plugin add cordova-plugin-camera", shell=True, cwd=project_folder)
            if self.chk_gps.get(): subprocess.run("cordova plugin add cordova-plugin-geolocation", shell=True, cwd=project_folder)
            if self.chk_storage.get(): subprocess.run("cordova plugin add cordova-plugin-file", shell=True, cwd=project_folder)

            config_path = os.path.join(project_folder, "config.xml")
            with open(config_path, "r", encoding="utf-8") as f: config_content = f.read()
            config_content = re.sub(r'version="[^"]+"', f'version="{app_version}" android-versionCode="{app_version_code}"', config_content)
            config_content = config_content.replace('</widget>', f'{xml_injections}</widget>')
            with open(config_path, "w", encoding="utf-8") as f: f.write(config_content)

            self.progress.set(0.6)

            self.log("\n[4/5] Platforma Android...")
            self.run_cmd_live("cordova platform add android", cwd=project_folder)
            self.progress.set(0.75)

            build_mode = "release" if "Release" in self.combo_build_type.get() else "debug"
            self.log(f"\n[5/5] ROZPOCZYNAM KOMPILACJĘ GRADEL ({build_mode.upper()})...")
            self.run_cmd_live(f"cordova build android --{build_mode}", cwd=project_folder)

            apk_folder = os.path.join(project_folder, "platforms", "android", "app", "build", "outputs", "apk", build_mode)
            self.progress.set(1.0)
            self.log("\n" + "="*40)
            self.log(f"💎 SUKCES! WERSJA TITANIUM ZOSTAŁA ZBUDOWANA.")
            self.log("="*40)

            if messagebox.askyesno("Misja Ukończona!", "Titanium APK zostało zbudowane bezbłędnie!\nOtworzyć folder lokalizacji?"):
                if platform.system() == "Windows": os.startfile(apk_folder)
                elif platform.system() == "Darwin": subprocess.Popen(["open", apk_folder])
                else: subprocess.Popen(["xdg-open", apk_folder])

        except Exception as e:
            self.log(f"\n❌ KRYTYCZNY BŁĄD TITANIUM: {str(e)}")
            self.progress.set(0)
            messagebox.showerror("Błąd", "Kompilacja została przerwana. Sprawdź terminal poniżej.")
        finally:
            self.after(0, lambda: self.btn_build.configure(state="normal", text="⚡ ROZPOCZNIJ BUDOWĘ TITANIUM"))

if __name__ == "__main__":
    app = TitaniumApkBuilder()
    app.mainloop()