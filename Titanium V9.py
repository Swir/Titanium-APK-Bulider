# -*- coding: utf-8 -*-
import os
import subprocess
import threading
import shutil
import re
import datetime
import sys
import webbrowser
import random
import string
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser

# --- BEZPIECZNY IMPORT PILLOW ---
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# --- USTAWIENIA MOTYWU GHOST APEX ---
BG_COLOR = "#03060a"
PANEL_BG = "#0a1118"
TEXT_FG = "#e0e6ed"
ACCENT_COLOR = "#00ffcc"
ACCENT_HOVER = "#00ccaa"
CODE_BG = "#060a0f"
CODE_FG = "#00ffcc"
STATUS_OK = "#00ff66"
STATUS_ERR = "#ff0055"

class GhostMasterBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("GHOST APK BUILDER BY SWIR - APEX STABILITY CORE V13.0")
        self.root.geometry("1450x950")
        self.root.configure(bg=BG_COLOR)
        
        # --- ŚCIEŻKI SYSTEMOWE ---
        self.output_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        self.android_studio_dir = os.path.join(os.path.expanduser("~"), "AndroidStudioProjects")
        self.ghost_dir = os.path.join(self.android_studio_dir, "Ghost_Apex_Workspace")
        self.config_file = "ghost_apex_config.json"
        
        self.found_projects = []
        self.icon_path = ""
        self.custom_font_path = ""
        self.tk_icon_preview = None 
        
        # --- ZMIENNE: PODSTAWY ---
        self.build_mode = tk.StringVar(value="Debug") 
        self.export_format = tk.StringVar(value="APK") 
        self.auto_usb = tk.BooleanVar(value=False)

        # --- ZMIENNE: WYGLĄD UI ---
        self.use_splash = tk.BooleanVar(value=True)
        self.anim_splash = tk.BooleanVar(value=True)
        self.splash_bg_color = tk.StringVar(value="#0a1118")
        self.status_bar_color = tk.StringVar(value="#03060a")
        self.fullscreen_mode = tk.BooleanVar(value=False)
        self.force_dark_mode = tk.BooleanVar(value=True)
        self.hw_accel = tk.BooleanVar(value=True)
        self.screen_orientation = tk.StringVar(value="portrait")
        
        # --- ZMIENNE: UPRAWNIENIA ---
        self.perm_internet = tk.BooleanVar(value=True)
        self.perm_camera = tk.BooleanVar(value=False)
        self.perm_storage = tk.BooleanVar(value=False)
        self.perm_location = tk.BooleanVar(value=False)
        self.perm_mic = tk.BooleanVar(value=False)

        # --- ZMIENNE: SILNIK I ZASOBY ---
        self.min_sdk = tk.StringVar(value="24")
        self.target_sdk = tk.StringVar(value="34")
        self.use_proguard = tk.BooleanVar(value=False)
        self.use_multidex = tk.BooleanVar(value=False) 
        self.lib_retrofit = tk.BooleanVar(value=False)
        self.lib_glide = tk.BooleanVar(value=False)
        self.lib_gson = tk.BooleanVar(value=False)
        self.assets_folder_path = tk.StringVar(value="")

        # --- ZMIENNE: KEYSTORE ---
        self.sign_release = tk.BooleanVar(value=False)
        self.keystore_path = tk.StringVar(value="")
        self.keystore_pass = tk.StringVar(value="")
        self.key_alias = tk.StringVar(value="")
        self.key_pass = tk.StringVar(value="")

        # --- ZMIENNE: BIZNES I PRO ---
        self.lib_admob = tk.BooleanVar(value=False)
        self.admob_app_id = tk.StringVar(value="ca-app-pub-3940256099942544~3347511713") 
        self.lib_billing = tk.BooleanVar(value=False)
        self.lib_lottie = tk.BooleanVar(value=False)

        # --- SNIPPETY KODU ---
        self.snippets = {
            "Domyślny ekran (Tekst)": "import android.os.Bundle\nimport androidx.appcompat.app.AppCompatActivity\nimport android.widget.TextView\nimport android.view.Gravity\nimport android.graphics.Color\n\nclass MainActivity : AppCompatActivity() {\n    override fun onCreate(savedInstanceState: Bundle?) {\n        super.onCreate(savedInstanceState)\n        val textView = TextView(this).apply {\n            text = \"GHOST APK BUILDER\\nSYSTEM W 100% GOTOWY!\"\n            textSize = 24f\n            gravity = Gravity.CENTER\n            setTextColor(Color.parseColor(\"#00ffcc\"))\n        }\n        setContentView(textView)\n    }\n}",
            "Panel Logowania (UI)": "import android.os.Bundle\nimport androidx.appcompat.app.AppCompatActivity\nimport android.widget.*\nimport android.view.Gravity\nimport android.graphics.Color\n\nclass MainActivity : AppCompatActivity() {\n    override fun onCreate(savedInstanceState: Bundle?) {\n        super.onCreate(savedInstanceState)\n        val layout = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER; setPadding(80,80,80,80) }\n        val title = TextView(this).apply { text = \"Ghost Login\"; textSize = 32f; gravity = Gravity.CENTER; setTextColor(Color.parseColor(\"#00ffcc\")); setPadding(0,0,0,50) }\n        val user = EditText(this).apply { hint = \"Nazwa użytkownika\"; setTextColor(Color.WHITE) }\n        val pass = EditText(this).apply { hint = \"Hasło\"; setTextColor(Color.WHITE); inputType = android.text.InputType.TYPE_CLASS_TEXT or android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD }\n        val btn = Button(this).apply { text = \"Zaloguj\"; setBackgroundColor(Color.parseColor(\"#00ffcc\")); setTextColor(Color.BLACK); setOnClickListener { Toast.makeText(context, \"Zalogowano jako: ${user.text}\", Toast.LENGTH_SHORT).show() } }\n        layout.addView(title); layout.addView(user); layout.addView(pass); layout.addView(btn)\n        setContentView(layout)\n    }\n}",
            "Przeglądarka (WebView)": "import android.os.Bundle\nimport androidx.appcompat.app.AppCompatActivity\nimport android.webkit.WebView\nimport android.webkit.WebViewClient\n\nclass MainActivity : AppCompatActivity() {\n    override fun onCreate(savedInstanceState: Bundle?) {\n        super.onCreate(savedInstanceState)\n        val webView = WebView(this).apply {\n            settings.javaScriptEnabled = true\n            webViewClient = WebViewClient()\n            loadUrl(\"https://google.pl\")\n        }\n        setContentView(webView)\n    }\n}",
            "Latarka (Flashlight)": "import android.content.Context\nimport android.hardware.camera2.CameraManager\nimport android.os.Bundle\nimport androidx.appcompat.app.AppCompatActivity\nimport android.widget.ToggleButton\nimport android.view.Gravity\nimport android.widget.LinearLayout\n\nclass MainActivity : AppCompatActivity() {\n    private var isTorchOn = false\n    override fun onCreate(savedInstanceState: Bundle?) {\n        super.onCreate(savedInstanceState)\n        val layout = LinearLayout(this).apply { gravity = Gravity.CENTER }\n        val toggle = ToggleButton(this).apply {\n            textOff = \"Włącz Latarkę\"\n            textOn = \"Wyłącz Latarkę\"\n            isChecked = false\n            setOnClickListener {\n                isTorchOn = !isTorchOn\n                val cameraManager = getSystemService(Context.CAMERA_SERVICE) as CameraManager\n                try {\n                    val cameraId = cameraManager.cameraIdList[0]\n                    cameraManager.setTorchMode(cameraId, isTorchOn)\n                } catch (e: Exception) {}\n            }\n        }\n        layout.addView(toggle)\n        setContentView(layout)\n    }\n}",
            "Lokalizacja GPS (Tekst)": "import android.Manifest\nimport android.content.pm.PackageManager\nimport android.location.LocationManager\nimport android.os.Bundle\nimport androidx.appcompat.app.AppCompatActivity\nimport androidx.core.app.ActivityCompat\nimport android.widget.TextView\nimport android.view.Gravity\nimport android.graphics.Color\n\nclass MainActivity : AppCompatActivity() {\n    override fun onCreate(savedInstanceState: Bundle?) {\n        super.onCreate(savedInstanceState)\n        val textView = TextView(this).apply { text = \"Pobieranie GPS...\"; textSize = 20f; gravity = Gravity.CENTER; setTextColor(Color.WHITE) }\n        setContentView(textView)\n        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED) {\n            val lm = getSystemService(LOCATION_SERVICE) as LocationManager\n            val loc = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER)\n            if(loc != null) textView.text = \"Współrzędne:\\nLat: ${loc.latitude}\\nLng: ${loc.longitude}\"\n            else textView.text = \"Brak sygnału GPS. Spróbuj na zewnątrz.\"\n        } else {\n            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.ACCESS_FINE_LOCATION), 1)\n        }\n    }\n}",
            "Aparat (Zrób zdjęcie)": "import android.content.Intent\nimport android.graphics.Bitmap\nimport android.os.Bundle\nimport android.provider.MediaStore\nimport android.widget.*\nimport android.view.Gravity\nimport androidx.appcompat.app.AppCompatActivity\n\nclass MainActivity : AppCompatActivity() {\n    private lateinit var imageView: ImageView\n    override fun onCreate(savedInstanceState: Bundle?) {\n        super.onCreate(savedInstanceState)\n        val layout = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER }\n        val btn = Button(this).apply { text = \"Uruchom Aparat\"; setOnClickListener { startActivityForResult(Intent(MediaStore.ACTION_IMAGE_CAPTURE), 100) } }\n        imageView = ImageView(this).apply { layoutParams = LinearLayout.LayoutParams(800, 800) }\n        layout.addView(btn); layout.addView(imageView)\n        setContentView(layout)\n    }\n    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {\n        super.onActivityResult(requestCode, resultCode, data)\n        if (requestCode == 100 && resultCode == RESULT_OK) {\n            val imgBitmap = data?.extras?.get(\"data\") as Bitmap\n            imageView.setImageBitmap(imgBitmap)\n        }\n    }\n}",
            "Odtwarzacz Wideo": "import android.os.Bundle\nimport androidx.appcompat.app.AppCompatActivity\nimport android.widget.VideoView\nimport android.widget.MediaController\nimport android.widget.RelativeLayout\n\nclass MainActivity : AppCompatActivity() {\n    override fun onCreate(savedInstanceState: Bundle?) {\n        super.onCreate(savedInstanceState)\n        val layout = RelativeLayout(this)\n        val videoView = VideoView(this).apply {\n            val lp = RelativeLayout.LayoutParams(RelativeLayout.LayoutParams.MATCH_PARENT, RelativeLayout.LayoutParams.WRAP_CONTENT)\n            lp.addRule(RelativeLayout.CENTER_IN_PARENT)\n            layoutParams = lp\n            setVideoPath(\"https://www.w3schools.com/html/mov_bbb.mp4\")\n        }\n        val mediaController = MediaController(this)\n        mediaController.setAnchorView(videoView)\n        videoView.setMediaController(mediaController)\n        videoView.start()\n        layout.addView(videoView)\n        setContentView(layout)\n    }\n}",
            "Czujnik Ruchu (Akcelerometr)": "import android.content.Context\nimport android.hardware.* \nimport android.os.Bundle\nimport androidx.appcompat.app.AppCompatActivity\nimport android.widget.TextView\nimport android.view.Gravity\nimport android.graphics.Color\n\nclass MainActivity : AppCompatActivity(), SensorEventListener {\n    private lateinit var sensorManager: SensorManager\n    private var accelerometer: Sensor? = null\n    private lateinit var textView: TextView\n    override fun onCreate(savedInstanceState: Bundle?) {\n        super.onCreate(savedInstanceState)\n        textView = TextView(this).apply { textSize = 28f; gravity = Gravity.CENTER; setTextColor(Color.WHITE) }\n        setContentView(textView)\n        sensorManager = getSystemService(Context.SENSOR_SERVICE) as SensorManager\n        accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)\n    }\n    override fun onResume() { super.onResume(); sensorManager.registerListener(this, accelerometer, SensorManager.SENSOR_DELAY_NORMAL) }\n    override fun onPause() { super.onPause(); sensorManager.unregisterListener(this) }\n    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}\n    override fun onSensorChanged(event: SensorEvent?) {\n        if (event != null) textView.text = \"X: ${event.values[0]}\\nY: ${event.values[1]}\\nZ: ${event.values[2]}\"\n    }\n}",
            "AdMob Baner (Zarabianie)": "import android.os.Bundle\nimport androidx.appcompat.app.AppCompatActivity\nimport android.widget.LinearLayout\nimport android.view.Gravity\nimport com.google.android.gms.ads.MobileAds\nimport com.google.android.gms.ads.AdRequest\nimport com.google.android.gms.ads.AdView\nimport com.google.android.gms.ads.AdSize\n\nclass MainActivity : AppCompatActivity() {\n    override fun onCreate(savedInstanceState: Bundle?) {\n        super.onCreate(savedInstanceState)\n        MobileAds.initialize(this) {}\n        val layout = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; gravity = Gravity.BOTTOM }\n        val adView = AdView(this).apply {\n            setAdSize(AdSize.BANNER)\n            adUnitId = \"ca-app-pub-3940256099942544/6300978111\"\n            loadAd(AdRequest.Builder().build())\n        }\n        layout.addView(adView)\n        setContentView(layout)\n    }\n}",
            "Lottie (Animacja wektorowa)": "import android.os.Bundle\nimport androidx.appcompat.app.AppCompatActivity\nimport android.widget.LinearLayout\nimport android.view.Gravity\nimport com.airbnb.lottie.LottieAnimationView\nimport com.airbnb.lottie.LottieDrawable\n\nclass MainActivity : AppCompatActivity() {\n    override fun onCreate(savedInstanceState: Bundle?) {\n        super.onCreate(savedInstanceState)\n        val layout = LinearLayout(this).apply { gravity = Gravity.CENTER }\n        val lottieView = LottieAnimationView(this).apply {\n            setAnimation(\"animacja.json\")\n            repeatCount = LottieDrawable.INFINITE\n            playAnimation()\n        }\n        layout.addView(lottieView)\n        setContentView(layout)\n    }\n}"
        }

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup_styles()
        self.create_widgets()
        
        # Inicjalizacja odbywa się PRZED ładowaniem ustawień
        self.scan_and_init_ghost()
        self.load_settings() # Teraz wczytuje wszystko co do joty
        self.highlight_syntax()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground=PANEL_BG, background=PANEL_BG, foreground=TEXT_FG, borderwidth=1, selectbackground=ACCENT_COLOR)
        style.map('TCombobox', fieldbackground=[('readonly', PANEL_BG)], foreground=[('readonly', TEXT_FG)])
        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL_BG, foreground=TEXT_FG, padding=[15, 5], font=("Consolas", 12, "bold"))
        style.map("TNotebook.Tab", background=[("selected", ACCENT_COLOR)], foreground=[("selected", "#000000")])
        style.configure("Dark.TCheckbutton", background=PANEL_BG, foreground=TEXT_FG, font=("Arial", 11, "bold"))
        style.map("Dark.TCheckbutton", background=[("active", PANEL_BG)])
        style.configure("Dark.TRadiobutton", background=PANEL_BG, foreground=TEXT_FG, font=("Arial", 11, "bold"))
        style.map("Dark.TRadiobutton", background=[("active", PANEL_BG)])
        style.configure("Ghost.Horizontal.TProgressbar", troughcolor=PANEL_BG, background=ACCENT_COLOR, thickness=15)

    def create_widgets(self):
        header = tk.Label(self.root, text="GHOST APK BUILDER BY SWIR | V13.0 APEX ENGINE", font=("Consolas", 22, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR)
        header.pack(pady=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # ==================== KARTA 1: KOMPILATOR ====================
        self.tab_build = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_build, text="⚡ Kompilator")
        
        build_main_frame = tk.Frame(self.tab_build, bg=BG_COLOR)
        build_main_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        left_frame = tk.Frame(build_main_frame, bg=PANEL_BG, bd=2, relief="flat", width=500)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)

        self.lbl_ghost_status = tk.Label(left_frame, text="👻 Status: Inicjalizacja rdzenia GHOST APEX...", font=("Consolas", 11, "bold"), bg=PANEL_BG, fg="#f39c12")
        self.lbl_ghost_status.pack(anchor="w", padx=15, pady=5)

        tk.Label(left_frame, text="1. Konfiguracja", font=("Arial", 12, "bold"), bg=PANEL_BG, fg=TEXT_FG).pack(anchor="w", padx=15, pady=(5, 5))
        
        self.entry_name = tk.Entry(left_frame, font=("Arial", 11), bg=CODE_BG, fg=TEXT_FG, insertbackground=TEXT_FG, relief="flat")
        self.entry_name.pack(fill=tk.X, padx=15, pady=2, ipady=4)
        self.entry_name.insert(0, "GhostApp")
        
        pkg_frame = tk.Frame(left_frame, bg=PANEL_BG)
        pkg_frame.pack(fill=tk.X, padx=15, pady=2)
        
        self.entry_package = tk.Entry(pkg_frame, font=("Arial", 11), bg=CODE_BG, fg=TEXT_FG, insertbackground=TEXT_FG, relief="flat")
        self.entry_package.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self.entry_package.insert(0, "com.swir.ghost")
        
        tk.Button(pkg_frame, text="🎲 Losuj", bg="#8e44ad", fg="white", relief="flat", command=self.randomize_package).pack(side=tk.RIGHT, padx=(5,0), ipady=2)

        version_frame = tk.Frame(left_frame, bg=PANEL_BG)
        version_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.entry_vname = tk.Entry(version_frame, width=12, font=("Arial", 11), bg=CODE_BG, fg=TEXT_FG, relief="flat")
        self.entry_vname.grid(row=1, column=0, pady=2, ipady=4)
        self.entry_vname.insert(0, "1.0.0")
        
        self.entry_vcode = tk.Entry(version_frame, width=12, font=("Arial", 11), bg=CODE_BG, fg=TEXT_FG, relief="flat")
        self.entry_vcode.grid(row=1, column=1, pady=2, padx=(10,0), ipady=4)
        self.entry_vcode.insert(0, "1")
        
        tk.Button(version_frame, text="⏱️ Auto", bg="#2c3e50", fg="white", relief="flat", command=self.auto_version).grid(row=1, column=2, padx=(10,0), ipady=2)

        tk.Label(left_frame, text="2. Ikona i Eksport", font=("Arial", 12, "bold"), bg=PANEL_BG, fg=TEXT_FG).pack(anchor="w", padx=15, pady=(15, 5))
        
        icon_frame = tk.Frame(left_frame, bg=PANEL_BG)
        icon_frame.pack(fill=tk.X, padx=15, pady=2)
        
        tk.Button(icon_frame, text="🖼️ Wybierz Ikonę", bg="#008899", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.select_icon).pack(side=tk.LEFT)
        self.lbl_icon_preview = tk.Label(icon_frame, bg=PANEL_BG)
        self.lbl_icon_preview.pack(side=tk.LEFT, padx=(10, 5))
        
        tk.Button(left_frame, text="📁 Zapisz pliki do...", bg="#2c3e50", fg="white", relief="flat", command=self.select_output).pack(anchor="w", padx=15, pady=(15, 5))
        self.lbl_output = tk.Label(left_frame, text=f"Cel: Pulpit", bg=PANEL_BG, fg="#8b9bb4", font=("Arial", 9))
        self.lbl_output.pack(anchor="w", padx=15)

        fmt_frame = tk.Frame(left_frame, bg=PANEL_BG)
        fmt_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(fmt_frame, text="Format:", bg=PANEL_BG, fg=ACCENT_COLOR, font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=2)
        ttk.Radiobutton(fmt_frame, text=".APK", variable=self.export_format, value="APK", style="Dark.TRadiobutton").grid(row=0, column=1, padx=10)
        ttk.Radiobutton(fmt_frame, text=".AAB", variable=self.export_format, value="AAB", style="Dark.TRadiobutton").grid(row=0, column=2)

        tk.Label(fmt_frame, text="Tryb:", bg=PANEL_BG, fg="#e67e22", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=10)
        ttk.Radiobutton(fmt_frame, text="Debug", variable=self.build_mode, value="Debug", style="Dark.TRadiobutton").grid(row=1, column=1, padx=10)
        ttk.Radiobutton(fmt_frame, text="Release", variable=self.build_mode, value="Release", style="Dark.TRadiobutton").grid(row=1, column=2)

        usb_frame = tk.Frame(left_frame, bg=PANEL_BG)
        usb_frame.pack(fill=tk.X, padx=15, pady=5)
        ttk.Checkbutton(usb_frame, text="📱 Wgraj po ADB (APK)", variable=self.auto_usb, style="Dark.TCheckbutton").pack(side=tk.LEFT)

        right_frame = tk.Frame(build_main_frame, bg=PANEL_BG, bd=2, relief="flat")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        snippet_frame = tk.Frame(right_frame, bg=PANEL_BG)
        snippet_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        tk.Label(snippet_frame, text="Edytor Kotlin | Szybki Snippet:", font=("Arial", 12, "bold"), bg=PANEL_BG, fg=TEXT_FG).pack(side=tk.LEFT)
        self.combo_snippet = ttk.Combobox(snippet_frame, values=list(self.snippets.keys()), state="readonly", width=35)
        self.combo_snippet.pack(side=tk.LEFT, padx=10)
        self.combo_snippet.current(0)
        
        tk.Button(snippet_frame, text="💉 Wstrzyknij Gotowca", bg="#e67e22", fg="white", font=("Arial", 9, "bold"), command=self.insert_snippet).pack(side=tk.LEFT)

        self.code_text = tk.Text(right_frame, font=("Consolas", 12), bg=CODE_BG, fg=CODE_FG, insertbackground=TEXT_FG, relief="flat", undo=True)
        self.code_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        self.code_text.bind("<KeyRelease>", self.highlight_syntax)
        self.code_text.insert("1.0", self.snippets["Domyślny ekran (Tekst)"])

        # ==================== KARTA 2: WYGLĄD ====================
        self.tab_design = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_design, text="🎨 Wygląd UI")
        
        design_frame = tk.Frame(self.tab_design, bg=BG_COLOR)
        design_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        des_left = tk.Frame(design_frame, bg=PANEL_BG, bd=2, relief="flat")
        des_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(des_left, text="Silnik Ekranu", font=("Arial", 14, "bold"), bg=PANEL_BG, fg=ACCENT_COLOR).pack(pady=(15,10))
        ttk.Checkbutton(des_left, text="🚀 Aktywuj Splash Screen", variable=self.use_splash, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=5)
        ttk.Checkbutton(des_left, text="✨ Animacja Ikony (Puls)", variable=self.anim_splash, style="Dark.TCheckbutton").pack(anchor="w", padx=40, pady=5)
        ttk.Checkbutton(des_left, text="🌙 Wymuś Tryb Ciemny", variable=self.force_dark_mode, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=15)
        ttk.Checkbutton(des_left, text="⚡ Wymuś Akcelerację Sprzętową (Płynność 60FPS)", variable=self.hw_accel, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=5)
        
        font_frame = tk.Frame(des_left, bg=PANEL_BG)
        font_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Button(font_frame, text="🔤 Własna Czcionka (.ttf)", bg="#8e44ad", fg="white", font=("Arial", 10, "bold"), relief="flat", command=self.select_font).pack(side=tk.LEFT)
        self.lbl_font_path = tk.Label(font_frame, text="Brak", bg=PANEL_BG, fg=TEXT_FG)
        self.lbl_font_path.pack(side=tk.LEFT, padx=10)

        color_frame = tk.Frame(des_left, bg=PANEL_BG)
        color_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(color_frame, text="Tło Splasha:", bg=PANEL_BG, fg=TEXT_FG).grid(row=0, column=0, sticky="w", pady=5)
        self.btn_splash_col = tk.Button(color_frame, text=self.splash_bg_color.get(), bg=self.splash_bg_color.get(), fg="white", width=10, command=lambda: self.pick_color(self.splash_bg_color, self.btn_splash_col))
        self.btn_splash_col.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(color_frame, text="Status Bar:", bg=PANEL_BG, fg=TEXT_FG).grid(row=1, column=0, sticky="w", pady=5)
        self.btn_status_col = tk.Button(color_frame, text=self.status_bar_color.get(), bg=self.status_bar_color.get(), fg="white", width=10, command=lambda: self.pick_color(self.status_bar_color, self.btn_status_col))
        self.btn_status_col.grid(row=1, column=1, padx=10, pady=5)

        ttk.Checkbutton(des_left, text="🖥️ Tryb Pełnoekranowy", variable=self.fullscreen_mode, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=15)
        
        ori_frame = tk.Frame(des_left, bg=PANEL_BG)
        ori_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(ori_frame, text="Orientacja:", bg=PANEL_BG, fg=TEXT_FG).pack(side=tk.LEFT)
        ttk.Combobox(ori_frame, textvariable=self.screen_orientation, values=["portrait", "landscape", "unspecified"], state="readonly", width=15).pack(side=tk.LEFT, padx=10)

        des_right = tk.Frame(design_frame, bg=PANEL_BG, bd=2, relief="flat")
        des_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(des_right, text="Manifest & Uprawnienia", font=("Arial", 14, "bold"), bg=PANEL_BG, fg="#3498db").pack(pady=(15,10))
        ttk.Checkbutton(des_right, text="🌐 Internet", variable=self.perm_internet, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=8)
        ttk.Checkbutton(des_right, text="📸 Aparat", variable=self.perm_camera, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=8)
        ttk.Checkbutton(des_right, text="💾 Pamięć", variable=self.perm_storage, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=8)
        ttk.Checkbutton(des_right, text="📍 GPS (Lokalizacja)", variable=self.perm_location, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=8)
        ttk.Checkbutton(des_right, text="🎤 Mikrofon", variable=self.perm_mic, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=8)

        # ==================== KARTA 3: PRO ====================
        self.tab_pro = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_pro, text="💰 Biznes i PRO")
        
        pro_frame = tk.Frame(self.tab_pro, bg=BG_COLOR)
        pro_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        pro_left = tk.Frame(pro_frame, bg=PANEL_BG, bd=2, relief="flat")
        pro_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(pro_left, text="Monetyzacja", font=("Arial", 14, "bold"), bg=PANEL_BG, fg="#f1c40f").pack(pady=(15,10))
        ttk.Checkbutton(pro_left, text="💵 Włącz Google AdMob", variable=self.lib_admob, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=10)
        
        admob_f = tk.Frame(pro_left, bg=PANEL_BG)
        admob_f.pack(fill=tk.X, padx=40, pady=2)
        tk.Label(admob_f, text="App ID:", bg=PANEL_BG, fg=TEXT_FG).pack(side=tk.LEFT)
        tk.Entry(admob_f, textvariable=self.admob_app_id, bg=CODE_BG, fg=TEXT_FG, width=35).pack(side=tk.LEFT, padx=10)
        
        ttk.Checkbutton(pro_left, text="💳 Włącz Google Play Billing", variable=self.lib_billing, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=15)

        pro_right = tk.Frame(pro_frame, bg=PANEL_BG, bd=2, relief="flat")
        pro_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(pro_right, text="Moduły Zaawansowane", font=("Arial", 14, "bold"), bg=PANEL_BG, fg="#e74c3c").pack(pady=(15,10))
        ttk.Checkbutton(pro_right, text="🎬 Biblioteka Lottie (Animacje AE JSON)", variable=self.lib_lottie, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=10)
        ttk.Checkbutton(pro_right, text="🧠 Aktywuj Multidex", variable=self.use_multidex, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=10)

        # ==================== KARTA 4: ZASOBY ====================
        self.tab_engine = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_engine, text="📦 Zasoby")
        
        eng_frame = tk.Frame(self.tab_engine, bg=BG_COLOR)
        eng_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        eng_left = tk.Frame(eng_frame, bg=PANEL_BG, bd=2, relief="flat")
        eng_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(eng_left, text="Wstrzykiwacz Assets", font=("Arial", 14, "bold"), bg=PANEL_BG, fg=ACCENT_COLOR).pack(pady=(15,10))
        
        asset_f = tk.Frame(eng_left, bg=PANEL_BG)
        asset_f.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(asset_f, text="📂 Wybierz folder", bg="#2980b9", fg="white", relief="flat", command=self.select_assets_folder).pack(side=tk.LEFT)
        self.lbl_assets_path = tk.Label(asset_f, text="Brak", bg=PANEL_BG, fg=TEXT_FG)
        self.lbl_assets_path.pack(side=tk.LEFT, padx=10)

        tk.Label(eng_left, text="Wersje SDK", font=("Arial", 12, "bold"), bg=PANEL_BG, fg=TEXT_FG).pack(anchor="w", padx=20, pady=(20, 5))
        
        sdk_f1 = tk.Frame(eng_left, bg=PANEL_BG)
        sdk_f1.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(sdk_f1, text="Min SDK:", bg=PANEL_BG, fg=TEXT_FG).pack(side=tk.LEFT)
        tk.Entry(sdk_f1, textvariable=self.min_sdk, font=("Arial", 11), bg=CODE_BG, fg=TEXT_FG, width=5).pack(side=tk.RIGHT)
        
        sdk_f2 = tk.Frame(eng_left, bg=PANEL_BG)
        sdk_f2.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(sdk_f2, text="Target SDK:", bg=PANEL_BG, fg=TEXT_FG).pack(side=tk.LEFT)
        tk.Entry(sdk_f2, textvariable=self.target_sdk, font=("Arial", 11), bg=CODE_BG, fg=TEXT_FG, width=5).pack(side=tk.RIGHT)
        
        ttk.Checkbutton(eng_left, text="🛡️ Włącz ProGuard", variable=self.use_proguard, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=20)

        eng_right = tk.Frame(eng_frame, bg=PANEL_BG, bd=2, relief="flat")
        eng_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(eng_right, text="Automatyczne Biblioteki API", font=("Arial", 14, "bold"), bg=PANEL_BG, fg="#2ecc71").pack(pady=(15,10))
        ttk.Checkbutton(eng_right, text="🌐 Retrofit", variable=self.lib_retrofit, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=10)
        ttk.Checkbutton(eng_right, text="🖼️ Glide", variable=self.lib_glide, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=10)
        ttk.Checkbutton(eng_right, text="📄 Gson", variable=self.lib_gson, style="Dark.TCheckbutton").pack(anchor="w", padx=20, pady=10)

        # ==================== KARTA 5: KEYSTORE ====================
        self.tab_security = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_security, text="🔐 Keystore")
        
        sec_frame = tk.Frame(self.tab_security, bg=PANEL_BG, bd=2, relief="flat")
        sec_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(sec_frame, text="PODPISYWANIE APLIKACJI", font=("Arial", 18, "bold"), bg=PANEL_BG, fg=ACCENT_COLOR).pack(pady=20)
        ttk.Checkbutton(sec_frame, text="✍️ Użyj klucza JKS dla Release", variable=self.sign_release, style="Dark.TCheckbutton").pack(pady=15)
        
        grid_frame = tk.Frame(sec_frame, bg=PANEL_BG)
        grid_frame.pack(pady=10)
        
        tk.Label(grid_frame, text="Keystore:", bg=PANEL_BG, fg=TEXT_FG, font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(grid_frame, textvariable=self.keystore_path, width=40, font=("Arial", 11), bg=CODE_BG, fg=TEXT_FG).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(grid_frame, text="Wybierz", bg="#34495e", fg="white", relief="flat", command=self.select_keystore).grid(row=0, column=2, padx=5)
        
        tk.Label(grid_frame, text="Hasło:", bg=PANEL_BG, fg=TEXT_FG, font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(grid_frame, textvariable=self.keystore_pass, show="*", width=20, font=("Arial", 11), bg=CODE_BG, fg=TEXT_FG).grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        tk.Label(grid_frame, text="Alias:", bg=PANEL_BG, fg=TEXT_FG, font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(grid_frame, textvariable=self.key_alias, width=20, font=("Arial", 11), bg=CODE_BG, fg=TEXT_FG).grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        tk.Label(grid_frame, text="Hasło Aliasu:", bg=PANEL_BG, fg=TEXT_FG, font=("Arial", 11)).grid(row=3, column=0, sticky="w", pady=5)
        tk.Entry(grid_frame, textvariable=self.key_pass, show="*", width=20, font=("Arial", 11), bg=CODE_BG, fg=TEXT_FG).grid(row=3, column=1, sticky="w", padx=10, pady=5)

        # ==================== KARTA 6: FABRYKA ====================
        self.tab_factory = tk.Frame(self.notebook, bg=BG_COLOR)
        self.notebook.add(self.tab_factory, text="🏗️ Fabryka Bazy")
        
        factory_frame = tk.Frame(self.tab_factory, bg=PANEL_BG, bd=2, relief="flat")
        factory_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(factory_frame, text="ZARZĄDZANIE BAZAMI KODU", font=("Arial", 16, "bold"), bg=PANEL_BG, fg=ACCENT_COLOR).pack(pady=20)
        
        self.combo_factory_base = ttk.Combobox(factory_frame, state="readonly", font=("Arial", 12), width=38)
        self.combo_factory_base.pack(pady=5)
        
        self.entry_factory_name = tk.Entry(factory_frame, font=("Arial", 12), bg=CODE_BG, fg=TEXT_FG, insertbackground=TEXT_FG, relief="flat", width=40)
        self.entry_factory_name.pack(pady=5, ipady=5)
        
        self.entry_factory_pkg = tk.Entry(factory_frame, font=("Arial", 12), bg=CODE_BG, fg=TEXT_FG, insertbackground=TEXT_FG, relief="flat", width=40)
        self.entry_factory_pkg.pack(pady=5, ipady=5)
        
        tk.Button(factory_frame, text="🧬 KLONUJ", bg="#27AE60", fg="white", font=("Arial", 12, "bold"), relief="flat", command=self.create_template).pack(pady=20, ipady=5, ipadx=20)
        
        tk.Label(factory_frame, text="NISZCZYCIEL", font=("Arial", 16, "bold"), bg=PANEL_BG, fg="#e74c3c").pack(pady=(30, 10))
        
        self.combo_delete = ttk.Combobox(factory_frame, state="readonly", font=("Arial", 12), width=38)
        self.combo_delete.pack(pady=5)
        
        tk.Button(factory_frame, text="🗑️ USUŃ PROJEKT", bg="#c0392b", fg="white", font=("Arial", 12, "bold"), relief="flat", command=self.delete_template).pack(pady=10, ipady=5, ipadx=20)

        # ==================== DOLNY PANEL ====================
        bot_frame = tk.Frame(self.root, bg=BG_COLOR)
        bot_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.progress = ttk.Progressbar(bot_frame, style="Ghost.Horizontal.TProgressbar", mode="determinate", maximum=100)
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        self.btn_build = tk.Button(bot_frame, text="⚡ GENERUJ APLIKACJĘ (GHOST APEX COMPILE)", font=("Arial", 16, "bold"), bg=ACCENT_COLOR, fg="#000000", activebackground=ACCENT_HOVER, relief="flat", cursor="hand2", command=self.start_build)
        self.btn_build.pack(fill=tk.X, side=tk.LEFT, expand=True, ipady=10)
        
        # NOWOŚĆ: Przycisk RESTART (Twardy reset aplikacji)
        tk.Button(bot_frame, text="🔄 Restart", font=("Arial", 10, "bold"), bg="#c0392b", fg="white", relief="flat", command=self.restart_app).pack(side=tk.RIGHT, padx=(10,0), ipady=13)
        tk.Button(bot_frame, text="💾 Zapisz Logi", font=("Arial", 10, "bold"), bg="#34495e", fg="white", relief="flat", command=self.export_logs).pack(side=tk.RIGHT, padx=(10,0), ipady=13)
        
        self.console = tk.Text(self.root, height=7, font=("Consolas", 10), bg="#000000", fg="#00ffcc", state=tk.DISABLED, relief="flat")
        self.console.pack(fill=tk.X, padx=20, pady=(10, 15))
        
        self.console.tag_config("link", foreground="#2ecc71", underline=True)
        self.console.tag_bind("link", "<Button-1>", self.open_folder_from_link)

    # --- FUNKCJE POMOCNICZE (ABSOLUTNA PAMIĘĆ) ---
    def save_settings(self):
        config = {
            "app_name": self.entry_name.get(),
            "package_name": self.entry_package.get(),
            "export_format": self.export_format.get(),
            "build_mode": self.build_mode.get(),
            "auto_usb": self.auto_usb.get(),
            
            "use_splash": self.use_splash.get(),
            "anim_splash": self.anim_splash.get(),
            "splash_bg_color": self.splash_bg_color.get(),
            "status_bar_color": self.status_bar_color.get(),
            "fullscreen_mode": self.fullscreen_mode.get(),
            "force_dark_mode": self.force_dark_mode.get(),
            "hw_accel": self.hw_accel.get(),
            "screen_orientation": self.screen_orientation.get(),
            
            "perm_internet": self.perm_internet.get(),
            "perm_camera": self.perm_camera.get(),
            "perm_storage": self.perm_storage.get(),
            "perm_location": self.perm_location.get(),
            "perm_mic": self.perm_mic.get(),
            
            "min_sdk": self.min_sdk.get(),
            "target_sdk": self.target_sdk.get(),
            "use_proguard": self.use_proguard.get(),
            "use_multidex": self.use_multidex.get(),
            "lib_retrofit": self.lib_retrofit.get(),
            "lib_glide": self.lib_glide.get(),
            "lib_gson": self.lib_gson.get(),
            
            "sign_release": self.sign_release.get(),
            "keystore_path": self.keystore_path.get(),
            "keystore_pass": self.keystore_pass.get(),
            "key_alias": self.key_alias.get(),
            "key_pass": self.key_pass.get(),
            
            "lib_admob": self.lib_admob.get(),
            "admob_app_id": self.admob_app_id.get(),
            "lib_billing": self.lib_billing.get(),
            "lib_lottie": self.lib_lottie.get(),
            
            "icon_path": self.icon_path,
            "custom_font_path": self.custom_font_path,
            "assets_folder_path": self.assets_folder_path.get(),
            "output_dir": self.output_dir
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f: 
                json.dump(config, f)
        except Exception: pass

    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f: 
                    config = json.load(f)
                
                # Teksty i comboboxy
                if "app_name" in config: self.entry_name.delete(0, tk.END); self.entry_name.insert(0, config["app_name"])
                if "package_name" in config: self.entry_package.delete(0, tk.END); self.entry_package.insert(0, config["package_name"])
                if "export_format" in config: self.export_format.set(config["export_format"])
                if "build_mode" in config: self.build_mode.set(config["build_mode"])
                if "admob_app_id" in config: self.admob_app_id.set(config["admob_app_id"])
                if "keystore_path" in config: self.keystore_path.set(config["keystore_path"])
                if "keystore_pass" in config: self.keystore_pass.set(config["keystore_pass"])
                if "key_alias" in config: self.key_alias.set(config["key_alias"])
                if "key_pass" in config: self.key_pass.set(config["key_pass"])
                if "min_sdk" in config: self.min_sdk.set(config["min_sdk"])
                if "target_sdk" in config: self.target_sdk.set(config["target_sdk"])
                if "screen_orientation" in config: self.screen_orientation.set(config["screen_orientation"])
                
                # Checkboxy
                if "auto_usb" in config: self.auto_usb.set(config["auto_usb"])
                if "use_splash" in config: self.use_splash.set(config["use_splash"])
                if "anim_splash" in config: self.anim_splash.set(config["anim_splash"])
                if "fullscreen_mode" in config: self.fullscreen_mode.set(config["fullscreen_mode"])
                if "force_dark_mode" in config: self.force_dark_mode.set(config["force_dark_mode"])
                if "hw_accel" in config: self.hw_accel.set(config["hw_accel"])
                if "perm_internet" in config: self.perm_internet.set(config["perm_internet"])
                if "perm_camera" in config: self.perm_camera.set(config["perm_camera"])
                if "perm_storage" in config: self.perm_storage.set(config["perm_storage"])
                if "perm_location" in config: self.perm_location.set(config["perm_location"])
                if "perm_mic" in config: self.perm_mic.set(config["perm_mic"])
                if "use_proguard" in config: self.use_proguard.set(config["use_proguard"])
                if "use_multidex" in config: self.use_multidex.set(config["use_multidex"])
                if "lib_retrofit" in config: self.lib_retrofit.set(config["lib_retrofit"])
                if "lib_glide" in config: self.lib_glide.set(config["lib_glide"])
                if "lib_gson" in config: self.lib_gson.set(config["lib_gson"])
                if "sign_release" in config: self.sign_release.set(config["sign_release"])
                if "lib_admob" in config: self.lib_admob.set(config["lib_admob"])
                if "lib_billing" in config: self.lib_billing.set(config["lib_billing"])
                if "lib_lottie" in config: self.lib_lottie.set(config["lib_lottie"])
                
                # Kolory (Aktualizacja UI)
                if "splash_bg_color" in config: 
                    self.splash_bg_color.set(config["splash_bg_color"])
                    self._update_color_btn(self.splash_bg_color.get(), self.btn_splash_col)
                if "status_bar_color" in config: 
                    self.status_bar_color.set(config["status_bar_color"])
                    self._update_color_btn(self.status_bar_color.get(), self.btn_status_col)
                
                # Ścieżki
                if "icon_path" in config and config["icon_path"] and os.path.exists(config["icon_path"]):
                    self.icon_path = config["icon_path"]
                    if HAS_PIL:
                        img = Image.open(self.icon_path).resize((32, 32), Image.LANCZOS)
                        self.tk_icon_preview = ImageTk.PhotoImage(img)
                        self.lbl_icon_preview.config(image=self.tk_icon_preview)
                
                if "custom_font_path" in config and config["custom_font_path"]:
                    self.custom_font_path = config["custom_font_path"]
                    self.lbl_font_path.config(text=f"...{os.path.basename(self.custom_font_path)}")
                
                if "assets_folder_path" in config and config["assets_folder_path"]:
                    self.assets_folder_path.set(config["assets_folder_path"])
                    p = config["assets_folder_path"]
                    self.lbl_assets_path.config(text=f"...{p[-25:]}" if len(p)>25 else p)
                
                if "output_dir" in config and config["output_dir"]:
                    self.output_dir = config["output_dir"]
                    p = self.output_dir
                    self.lbl_output.config(text=f"...{p[-37:]}" if len(p)>40 else f"Cel: {p}")
                    
            except Exception as e: 
                print(f"Błąd wczytywania configu: {e}")

    def _update_color_btn(self, color, btn):
        btn.config(bg=color, text=color)
        try:
            brightness = 0.299 * int(color[1:3], 16) + 0.587 * int(color[3:5], 16) + 0.114 * int(color[5:7], 16)
            btn.config(fg="white" if brightness < 128 else "black")
        except: pass

    # --- NOWOŚĆ: TWARDY RESTART APLIKACJI ---
    def restart_app(self):
        if messagebox.askyesno("Ostrzeżenie", "Czy na pewno chcesz zrestartować Ghost APK Builder? Zmiany zostaną zapisane, a proces zresetowany."):
            self.save_settings()
            if os.path.exists(self.ghost_dir): 
                shutil.rmtree(self.ghost_dir, ignore_errors=True)
            self.root.destroy()
            os.execl(sys.executable, sys.executable, *sys.argv)

    def insert_snippet(self):
        choice = self.combo_snippet.get()
        if choice in self.snippets:
            self.code_text.delete("1.0", tk.END)
            self.code_text.insert("1.0", self.snippets[choice])
            self.highlight_syntax()
            self.log(f">>> Snippet '{choice}' wstrzyknięty pomyślnie.")

    def select_font(self):
        file = filedialog.askopenfilename(filetypes=[("Czcionki", "*.ttf *.otf")])
        if file: 
            self.custom_font_path = file
            self.lbl_font_path.config(text=f"...{os.path.basename(file)}")

    def export_logs(self):
        file = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=f"GHOST_Logs_{datetime.datetime.now().strftime('%H%M%S')}.txt")
        if file:
            with open(file, 'w', encoding='utf-8') as f: 
                f.write(self.console.get("1.0", tk.END))
            messagebox.showinfo("Logi", "Zapisano logi!")

    def pick_color(self, var, btn):
        c = colorchooser.askcolor()[1]
        if c:
            var.set(c)
            self._update_color_btn(c, btn)

    def set_progress(self, val): 
        self.progress['value'] = val
        self.root.update_idletasks()
        
    def randomize_package(self): 
        self.entry_package.delete(0, tk.END)
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        self.entry_package.insert(0, f"com.swir.ghost.{random_str}")
        
    def open_folder_from_link(self, event): 
        os.startfile(self.output_dir)
    
    def highlight_syntax(self, event=None):
        self.code_text.tag_configure("kw", foreground="#c678dd", font=("Consolas", 12, "bold"))
        self.code_text.tag_configure("string", foreground="#98c379") 
        
        for tag in ["kw", "string"]: 
            self.code_text.tag_remove(tag, "1.0", tk.END)
            
        text = self.code_text.get("1.0", tk.END)
        
        for match in re.finditer(r'".*?"', text): 
            self.code_text.tag_add("string", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")
            
        keywords = ["class", "fun", "val", "var", "import", "package", "override", "super", "if", "else"]
        for kw in keywords:
            for match in re.finditer(r'\b' + kw + r'\b', text): 
                self.code_text.tag_add("kw", f"1.0 + {match.start()} chars", f"1.0 + {match.end()} chars")

    def auto_version(self):
        now = datetime.datetime.now()
        self.entry_vname.delete(0, tk.END)
        self.entry_vname.insert(0, f"1.0.{now.strftime('%y%m%d')}")
        self.entry_vcode.delete(0, tk.END)
        self.entry_vcode.insert(0, now.strftime('%y%m%d%H'))

    def select_icon(self):
        file = filedialog.askopenfilename(filetypes=[("Pliki PNG", "*.png")])
        if file and HAS_PIL:
            self.icon_path = file
            try: 
                img = Image.open(file).resize((32, 32), Image.LANCZOS)
                self.tk_icon_preview = ImageTk.PhotoImage(img)
                self.lbl_icon_preview.config(image=self.tk_icon_preview)
            except Exception: 
                pass

    def select_output(self):
        folder = filedialog.askdirectory()
        if folder: 
            self.output_dir = folder
            display_text = f"...{folder[-37:]}" if len(folder)>40 else f"Cel: {folder}"
            self.lbl_output.config(text=display_text)

    def select_assets_folder(self):
        folder = filedialog.askdirectory()
        if folder: 
            self.assets_folder_path.set(folder)
            display_text = f"...{folder[-25:]}" if len(folder)>25 else folder
            self.lbl_assets_path.config(text=display_text)

    def select_keystore(self):
        file = filedialog.askopenfilename(filetypes=[("Keystore", "*.jks *.keystore")])
        if file: 
            self.keystore_path.set(file)

    def log(self, text):
        self.console.config(state=tk.NORMAL)
        if "Zapisano plik:" in text: 
            parts = text.split("Zapisano plik:")
            self.console.insert(tk.END, parts[0] + "Zapisano plik: ")
            self.console.insert(tk.END, parts[1].strip() + "\n", "link")
        else: 
            self.console.insert(tk.END, text + "\n")
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)

    # --- SILNIK KOMPILACJI APEX ---
    def scan_and_init_ghost(self): 
        threading.Thread(target=self._bg_init_ghost, daemon=True).start()

    def _bg_init_ghost(self):
        self.root.after(0, lambda: self.btn_build.config(state=tk.DISABLED, text="⏳ INICJALIZACJA SYSTEMU..."))
        os.makedirs(self.android_studio_dir, exist_ok=True)
        
        base_project = None
        for folder_name in os.listdir(self.android_studio_dir):
            if "Ghost_Apex_Workspace" in folder_name: 
                continue
            full_path = os.path.join(self.android_studio_dir, folder_name)
            if os.path.isdir(full_path):
                if os.path.exists(os.path.join(full_path, "build.gradle.kts")) or os.path.exists(os.path.join(full_path, "build.gradle")):
                    base_project = full_path
                    break
                
        if not base_project:
            self.root.after(0, lambda: self.lbl_ghost_status.config(text="👻 Brak bazy Android Studio!", fg=STATUS_ERR))
            self.log("!!! Najpierw utwórz lub sklonuj pusty projekt Android Studio.")
            return

        self.root.after(0, lambda: self.lbl_ghost_status.config(text=f"👻 Klonowanie bezpiecznej bazy..."))
        if os.path.exists(self.ghost_dir): 
            shutil.rmtree(self.ghost_dir, ignore_errors=True)
            
        shutil.copytree(base_project, self.ghost_dir)
        
        for d in ['.gradle', '.idea', 'build', 'app/build']: 
            shutil.rmtree(os.path.join(self.ghost_dir, d), ignore_errors=True)
            
        self.root.after(0, lambda: self.lbl_ghost_status.config(text="👻 SYSTEM GHOST APEX GOTOWY", fg=STATUS_OK))
        self.root.after(0, lambda: self.btn_build.config(state=tk.NORMAL, text="⚡ GENERUJ APLIKACJĘ (GHOST APEX COMPILE)", bg=ACCENT_COLOR))
        
        self.found_projects = []
        for f in os.listdir(self.android_studio_dir):
            full_path = os.path.join(self.android_studio_dir, f)
            if "Ghost_Apex" not in f and os.path.isdir(full_path):
                self.found_projects.append(full_path)
                
        if self.found_projects:
            names = [os.path.basename(p) for p in self.found_projects]
            self.combo_factory_base['values'] = names
            self.combo_factory_base.current(0)
            self.combo_delete['values'] = names
            self.combo_delete.current(0)

    def get_ui_injection_code(self):
        code = f"\n        window.statusBarColor = android.graphics.Color.parseColor(\"{self.status_bar_color.get()}\")"
        if self.fullscreen_mode.get(): 
            code += "\n        window.decorView.systemUiVisibility = (android.view.View.SYSTEM_UI_FLAG_FULLSCREEN or android.view.View.SYSTEM_UI_FLAG_HIDE_NAVIGATION or android.view.View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY)"
        if self.force_dark_mode.get(): 
            code += "\n        androidx.appcompat.app.AppCompatDelegate.setDefaultNightMode(androidx.appcompat.app.AppCompatDelegate.MODE_NIGHT_YES)"
        return code

    def start_build(self):
        if not os.path.exists(self.ghost_dir): 
            self.log("!!! Błąd: Brak folderu roboczego Ghost.")
            return
            
        self.btn_build.config(state=tk.DISABLED, text="⏳ KOMPILACJA W TOKU...")
        self.console.config(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.config(state=tk.DISABLED)
        
        self.save_settings()
        
        threading.Thread(target=self.build_logic, daemon=True).start()

    def build_logic(self):
        app_name = self.entry_name.get() or "GhostApp"
        pkg_name = re.sub(r'[^a-z0-9.]', '', self.entry_package.get().lower().replace(',', '.'))
        mode = self.build_mode.get()
        export_fmt = self.export_format.get() 

        try:
            self.set_progress(10)
            subprocess.run("taskkill /F /IM java.exe /T", shell=True, capture_output=True)
            
            java_src = os.path.join(self.ghost_dir, 'app', 'src', 'main', 'java')
            if os.path.exists(java_src): 
                shutil.rmtree(java_src)
                
            new_pkg_dir = os.path.join(java_src, *pkg_name.split('.'))
            os.makedirs(new_pkg_dir, exist_ok=True)

            self.set_progress(25)
            self._inject_gradle(pkg_name)
            self._inject_manifest(app_name)
            
            if self.assets_folder_path.get() and os.path.exists(self.assets_folder_path.get()):
                assets_target = os.path.join(self.ghost_dir, 'app', 'src', 'main', 'assets')
                shutil.copytree(self.assets_folder_path.get(), assets_target, dirs_exist_ok=True)
            
            font_injection_code = "setTypeface(null, android.graphics.Typeface.BOLD)"
            if self.custom_font_path and os.path.exists(self.custom_font_path):
                self.log("   -> Bezpieczne wstrzykiwanie czcionki...")
                font_dest_dir = os.path.join(self.ghost_dir, 'app', 'src', 'main', 'assets', 'fonts')
                os.makedirs(font_dest_dir, exist_ok=True)
                
                font_filename = "ghost_font" + os.path.splitext(self.custom_font_path)[1]
                shutil.copy2(self.custom_font_path, os.path.join(font_dest_dir, font_filename))
                font_injection_code = f"typeface = android.graphics.Typeface.createFromAsset(assets, \"fonts/{font_filename}\")"

            self.set_progress(40)
            
            user_code = self.code_text.get("1.0", tk.END)
            main_code = f"package {pkg_name}\n\n" + re.sub(r'^package\s+.*?\n', '', user_code, flags=re.MULTILINE).strip()
            
            if "supportActionBar?.hide()" in main_code: 
                main_code = main_code.replace("supportActionBar?.hide()", f"supportActionBar?.hide(){self.get_ui_injection_code()}")
                
            with open(os.path.join(new_pkg_dir, 'MainActivity.kt'), 'w', encoding='utf-8') as f: 
                f.write(main_code)

            if self.use_splash.get():
                anim_code = ""
                if self.anim_splash.get():
                    anim_code = "imageView.animate().scaleX(1.3f).scaleY(1.3f).setDuration(1500).setInterpolator(android.view.animation.OvershootInterpolator()).start()"
                    
                splash_code = f"""package {pkg_name}
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import android.graphics.Color

class SplashActivity : AppCompatActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        supportActionBar?.hide()
        {self.get_ui_injection_code()}
        
        val layout = LinearLayout(this).apply {{ 
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setBackgroundColor(Color.parseColor("{self.splash_bg_color.get()}")) 
        }}
        
        try {{ 
            var resId = resources.getIdentifier("ghost_icon", "mipmap", packageName)
            if (resId == 0) {{
                resId = resources.getIdentifier("ic_launcher", "mipmap", packageName)
            }}
            
            if (resId != 0) {{ 
                val imageView = ImageView(this).apply {{ 
                    setImageResource(resId)
                    layoutParams = LinearLayout.LayoutParams(300, 300).apply {{ bottomMargin = 60 }} 
                }}
                layout.addView(imageView)
                {anim_code}
            }} 
        }} catch (e: Exception) {{}}
        
        val textView = TextView(this).apply {{ 
            text = "{app_name}"
            textSize = 32f
            setTextColor(Color.parseColor("{ACCENT_COLOR}"))
            gravity = Gravity.CENTER
            {font_injection_code}
            alpha = 0f 
        }}
        
        textView.animate().alpha(1f).setDuration(1000).start()
        layout.addView(textView)
        setContentView(layout)
        
        Handler(Looper.getMainLooper()).postDelayed({{ 
            startActivity(Intent(this@SplashActivity, MainActivity::class.java))
            finish() 
        }}, 2500)
    }}
}}"""
                with open(os.path.join(new_pkg_dir, 'SplashActivity.kt'), 'w', encoding='utf-8') as f: 
                    f.write(splash_code)

            gradle_task = f"assemble{mode}" if export_fmt == "APK" else f"bundle{mode}"
            self.log(f">>> [4/6] START GHOST APEX CORE ({gradle_task})...")
            self.set_progress(55)
            
            gradle_exec = "gradlew.bat" if os.path.exists(os.path.join(self.ghost_dir, "gradlew.bat")) else "gradle"
            cmd = f"{gradle_exec} clean {gradle_task} --no-daemon --no-build-cache --console=plain"
            
            process = subprocess.Popen(cmd, cwd=self.ghost_dir, env=os.environ.copy(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
            
            for line in process.stdout: 
                self.log("   " + line.strip())
                if "Task :" in line and self.progress['value'] < 90: 
                    self.set_progress(self.progress['value'] + 1)
                    
            process.wait()
            self.set_progress(90)

            ext = export_fmt.lower()
            if export_fmt == "APK":
                target_path = os.path.join(self.ghost_dir, 'app', 'build', 'outputs', 'apk', mode.lower(), f'app-{mode.lower()}.apk')
                if not os.path.exists(target_path): 
                    target_path = os.path.join(self.ghost_dir, 'app', 'build', 'outputs', 'apk', mode.lower(), f'app-{mode.lower()}-unsigned.apk')
            else:
                target_path = os.path.join(self.ghost_dir, 'app', 'build', 'outputs', 'bundle', mode.lower(), f'app-{mode.lower()}.aab')

            if os.path.exists(target_path) and process.returncode == 0:
                self.set_progress(100)
                safe_app_name = re.sub(r'[^a-zA-Z0-9_]', '', app_name.replace(' ', '_'))
                final_dest = os.path.join(self.output_dir, f"{safe_app_name}_{mode}_v{self.entry_vname.get()}.{ext}")
                shutil.copy2(target_path, final_dest)
                
                file_size_mb = os.path.getsize(final_dest) / (1024 * 1024)
                self.log(f"\n>>> [SUKCES!] GHOST wygenerował plik ({file_size_mb:.2f} MB)")
                self.log(f">>> Zapisano plik: {final_dest}")
                
                if self.auto_usb.get() and export_fmt == "APK":
                    adb = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Android', 'Sdk', 'platform-tools', 'adb.exe')
                    if os.path.exists(adb): 
                        subprocess.run([adb, "install", "-r", final_dest], capture_output=True)
                        launch_str = f"{pkg_name}/{pkg_name}.SplashActivity" if self.use_splash.get() else f"{pkg_name}/{pkg_name}.MainActivity"
                        subprocess.run([adb, "shell", "am", "start", "-n", launch_str])
                        
                self.root.after(0, lambda: self.ask_ghost_fate(app_name))
            else:
                self.log(f"\n!!! [BŁĄD] Plik {ext} nie istnieje.")
                self.set_progress(0)
                self.root.after(0, lambda: self.btn_build.config(state=tk.NORMAL, text="⚡ GENERUJ APLIKACJĘ (GHOST APEX COMPILE)", bg=ACCENT_COLOR))
                
        except Exception as e: 
            self.log(f"!!! BŁĄD SYSTEMU: {str(e)}")
            self.set_progress(0)
            self.root.after(0, lambda: self.btn_build.config(state=tk.NORMAL, text="⚡ GENERUJ APLIKACJĘ (GHOST APEX COMPILE)", bg=ACCENT_COLOR))

    # --- STRAŻNIK GRADLE ---
    def _inject_gradle(self, pkg_name):
        gradle_kts_path = os.path.join(self.ghost_dir, 'app', 'build.gradle.kts')
        gradle_path = gradle_kts_path if os.path.exists(gradle_kts_path) else os.path.join(self.ghost_dir, 'app', 'build.gradle')
        
        with open(gradle_path, 'r', encoding='utf-8') as f: 
            g = f.read()
            
        is_kts = "kts" in gradle_path
        
        if is_kts:
            g = re.sub(r'applicationId\s*=?\s*["\'].*?["\']', f'applicationId = "{pkg_name}"', g)
            g = re.sub(r'namespace\s*=?\s*["\'].*?["\']', f'namespace = "{pkg_name}"', g)
            g = re.sub(r'versionCode\s*=?\s*\d+', f'versionCode = {self.entry_vcode.get()}', g)
            g = re.sub(r'versionName\s*=?\s*["\'].*?["\']', f'versionName = "{self.entry_vname.get()}"', g)
            g = re.sub(r'minSdk\s*=?\s*\d+', f'minSdk = {self.min_sdk.get()}', g)
        else:
            g = re.sub(r'applicationId\s*=?\s*["\'].*?["\']', f'applicationId "{pkg_name}"', g)
            g = re.sub(r'namespace\s*=?\s*["\'].*?["\']', f'namespace "{pkg_name}"', g)
            g = re.sub(r'versionCode\s*=?\s*\d+', f'versionCode {self.entry_vcode.get()}', g)
            g = re.sub(r'versionName\s*=?\s*["\'].*?["\']', f'versionName "{self.entry_vname.get()}"', g)
            g = re.sub(r'minSdk\s*=?\s*\d+', f'minSdk {self.min_sdk.get()}', g)
        
        if self.use_multidex.get() and "multiDexEnabled" not in g:
            if is_kts:
                g = g.replace("defaultConfig {", "defaultConfig {\n        multiDexEnabled = true")
            else:
                g = g.replace("defaultConfig {", "defaultConfig {\n        multiDexEnabled true")

        if self.build_mode.get() == "Release" and self.sign_release.get() and os.path.exists(self.keystore_path.get()) and "signingConfigs {" not in g:
            k = self.keystore_path.get().replace('\\', '/')
            if is_kts: 
                sign_block = f"""
    signingConfigs {{
        create("release") {{
            storeFile = file("{k}")
            storePassword = "{self.keystore_pass.get()}"
            keyAlias = "{self.key_alias.get()}"
            keyPassword = "{self.key_pass.get()}"
        }}
    }}
    buildTypes {{"""
                g = g.replace("buildTypes {", sign_block)
                g = g.replace("getByName(\"release\") {", "getByName(\"release\") {\n            signingConfig = signingConfigs.getByName(\"release\")")
            else: 
                sign_block = f"""
    signingConfigs {{
        release {{
            storeFile file("{k}")
            storePassword "{self.keystore_pass.get()}"
            keyAlias "{self.key_alias.get()}"
            keyPassword "{self.key_pass.get()}"
        }}
    }}
    buildTypes {{"""
                g = g.replace("buildTypes {", sign_block)
                g = g.replace("release {", "release {\n            signingConfig signingConfigs.release")

        if self.use_proguard.get(): 
            if is_kts:
                g = g.replace('isMinifyEnabled = false', 'isMinifyEnabled = true')
            else:
                g = g.replace('minifyEnabled false', 'minifyEnabled true\n            shrinkResources true')
        
        libs = ""
        if self.lib_retrofit.get() and "retrofit:2.9.0" not in g: 
            libs += "    implementation(\"com.squareup.retrofit2:retrofit:2.9.0\")\n" if is_kts else "    implementation 'com.squareup.retrofit2:retrofit:2.9.0'\n"
        if self.lib_glide.get() and "glide:4.16.0" not in g: 
            libs += "    implementation(\"com.github.bumptech.glide:glide:4.16.0\")\n" if is_kts else "    implementation 'com.github.bumptech.glide:glide:4.16.0'\n"
        if self.lib_gson.get() and "gson:2.10.1" not in g: 
            libs += "    implementation(\"com.google.code.gson:gson:2.10.1\")\n" if is_kts else "    implementation 'com.google.code.gson:gson:2.10.1'\n"
        if self.use_multidex.get() and "multidex:2.0.1" not in g: 
            libs += "    implementation(\"androidx.multidex:multidex:2.0.1\")\n" if is_kts else "    implementation 'androidx.multidex:multidex:2.0.1'\n"
        if self.lib_admob.get() and "play-services-ads:22.6.0" not in g: 
            libs += "    implementation(\"com.google.android.gms:play-services-ads:22.6.0\")\n" if is_kts else "    implementation 'com.google.android.gms:play-services-ads:22.6.0'\n"
        if self.lib_billing.get() and "billing-ktx:6.1.0" not in g: 
            libs += "    implementation(\"com.android.billingclient:billing-ktx:6.1.0\")\n" if is_kts else "    implementation 'com.android.billingclient:billing-ktx:6.1.0'\n"
        if self.lib_lottie.get() and "lottie:6.3.0" not in g: 
            libs += "    implementation(\"com.airbnb.android:lottie:6.3.0\")\n" if is_kts else "    implementation 'com.airbnb.android:lottie:6.3.0'\n"

        if libs and "dependencies {" in g: 
            g = g.replace("dependencies {", f"dependencies {{\n{libs}")
            
        with open(gradle_path, 'w', encoding='utf-8') as f: 
            f.write(g)

    # --- STRAŻNIK MANIFESTU ---
    def _inject_manifest(self, app_name):
        manifest_path = os.path.join(self.ghost_dir, 'app', 'src', 'main', 'AndroidManifest.xml')
        with open(manifest_path, 'r', encoding='utf-8') as f: 
            m = f.read()
        
        strings_path = os.path.join(self.ghost_dir, 'app', 'src', 'main', 'res', 'values', 'strings.xml')
        if os.path.exists(strings_path):
            with open(strings_path, 'r', encoding='utf-8') as f: 
                s_content = f.read()
            s_content = re.sub(r'<string name="app_name">.*?</string>', f'<string name="app_name">{app_name}</string>', s_content)
            with open(strings_path, 'w', encoding='utf-8') as f: 
                f.write(s_content)
        
        m = re.sub(r'android:label="[^"]+"', f'android:label="{app_name}"', m)

        # AKCELERACJA SPRZĘTOWA
        if self.hw_accel.get() and 'android:hardwareAccelerated' not in m:
            m = m.replace('<application', '<application android:hardwareAccelerated="true"')
        elif not self.hw_accel.get() and 'android:hardwareAccelerated="true"' in m:
            m = m.replace(' android:hardwareAccelerated="true"', '')

        if self.perm_internet.get() and "android.permission.INTERNET" not in m: 
            m = m.replace('<application', '<uses-permission android:name="android.permission.INTERNET" />\n    <application')
        if self.perm_camera.get() and "android.permission.CAMERA" not in m: 
            m = m.replace('<application', '<uses-permission android:name="android.permission.CAMERA" />\n    <application')
        if self.perm_storage.get() and "android.permission.WRITE_EXTERNAL_STORAGE" not in m: 
            m = m.replace('<application', '<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />\n    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />\n    <application')
        if self.perm_location.get() and "android.permission.ACCESS_FINE_LOCATION" not in m: 
            m = m.replace('<application', '<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />\n    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />\n    <application')
        if self.perm_mic.get() and "android.permission.RECORD_AUDIO" not in m: 
            m = m.replace('<application', '<uses-permission android:name="android.permission.RECORD_AUDIO" />\n    <application')
        
        if self.lib_admob.get() and self.admob_app_id.get() and "com.google.android.gms.ads.APPLICATION_ID" not in m:
            admob_tag = f'<meta-data android:name="com.google.android.gms.ads.APPLICATION_ID" android:value="{self.admob_app_id.get()}"/>\n        '
            m = m.replace('<application', f'<application\n        {admob_tag}')

        if self.icon_path and os.path.exists(self.icon_path):
            res_dir = os.path.join(self.ghost_dir, 'app', 'src', 'main', 'res')
            
            for root_dir, dirs, files in os.walk(res_dir):
                if 'mipmap' in root_dir or 'drawable' in root_dir:
                    for file in files:
                        if 'ic_launcher' in file or 'ghost_icon' in file:
                            try: 
                                os.remove(os.path.join(root_dir, file))
                            except Exception: 
                                pass
            
            if HAS_PIL:
                img = Image.open(self.icon_path)
                sizes = {'mdpi':48, 'hdpi':72, 'xhdpi':96, 'xxhdpi':144, 'xxxhdpi':192}
                for den, sz in sizes.items():
                    folder = os.path.join(res_dir, f'mipmap-{den}')
                    os.makedirs(folder, exist_ok=True)
                    img.resize((sz, sz), Image.LANCZOS).save(os.path.join(folder, "ghost_icon.png"))
            else:
                drawable_dir = os.path.join(res_dir, 'drawable')
                os.makedirs(drawable_dir, exist_ok=True)
                shutil.copy2(self.icon_path, os.path.join(drawable_dir, "ghost_icon.png"))

            m = re.sub(r'android:icon="[^"]+"', 'android:icon="@mipmap/ghost_icon"', m)
            m = re.sub(r'android:roundIcon="[^"]+"', 'android:roundIcon="@mipmap/ghost_icon"', m)

        if self.screen_orientation.get() != "unspecified" and f'android:screenOrientation="{self.screen_orientation.get()}"' not in m:
            m = re.sub(r'android:screenOrientation="[^"]+"', '', m)
            m = m.replace('<activity', f'<activity android:screenOrientation="{self.screen_orientation.get()}"')
            
        if self.use_splash.get() and 'android:name=".SplashActivity"' not in m:
            m = m.replace('android:name=".MainActivity"', 'android:name=".SplashActivity"')
            if '.MainActivity"' not in m: 
                m = m.replace('</application>', f'    <activity android:name=".MainActivity" android:exported="true" />\n    </application>')
                
        with open(manifest_path, 'w', encoding='utf-8') as f: 
            f.write(m)

    def ask_ghost_fate(self, project_name):
        if messagebox.askyesno("Gotowe!", "Zachować cały wygenerowany projekt źródłowy w folderze Android Studio?"):
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '', project_name)
            new_dir = os.path.join(self.android_studio_dir, f"GhostProject_{safe_name}_{int(datetime.datetime.now().timestamp())}")
            os.rename(self.ghost_dir, new_dir)
            self.log(f">>> Projekt zapisany: {new_dir}")
        else: 
            shutil.rmtree(self.ghost_dir, ignore_errors=True)
            self.log(">>> Pamięć robocza wyczyszczona.")
            
        self.btn_build.config(state=tk.NORMAL, text="⚡ GENERUJ APLIKACJĘ (GHOST APEX COMPILE)", bg=ACCENT_COLOR)
        self.set_progress(0)
        self.scan_and_init_ghost()

    # --- FABRYKA KODU ---
    def create_template(self):
        if not self.found_projects: 
            return
            
        base_idx = self.combo_factory_base.current()
        base_project_path = self.found_projects[base_idx]
        name = re.sub(r'[^a-zA-Z0-9_]', '', self.entry_factory_name.get().strip())
        pkg = re.sub(r'[^a-z0-9.]', '', self.entry_factory_pkg.get().strip().lower().replace(',', '.'))
        
        if not name or not pkg: 
            messagebox.showwarning("Błąd", "Wprowadź nazwę i pakiet!")
            return
            
        target_dir = os.path.join(self.android_studio_dir, name)
        try:
            self.log(f">>> 🧬 KLONOWANIE BAZY GHOST: {name}")
            shutil.copytree(base_project_path, target_dir)
            
            for d in ['.gradle', '.idea', 'build', 'app/build', '.cxx']: 
                shutil.rmtree(os.path.join(target_dir, d), ignore_errors=True)
                
            for s_file in ['settings.gradle.kts', 'settings.gradle']:
                s_path = os.path.join(target_dir, s_file)
                if os.path.exists(s_path):
                    with open(s_path, 'r', encoding='utf-8') as f: 
                        c = f.read()
                    c = re.sub(r'rootProject\.name\s*=\s*["\'].*?["\']', f'rootProject.name = "{name}"', c)
                    with open(s_path, 'w', encoding='utf-8') as f: 
                        f.write(c)
                        
            for b_file in ['app/build.gradle.kts', 'app/build.gradle']:
                b_path = os.path.join(target_dir, b_file)
                if os.path.exists(b_path):
                    with open(b_path, 'r', encoding='utf-8') as f: 
                        c = f.read()
                    if "kts" in b_file:
                        c = re.sub(r'applicationId\s*=\s*["\'].*?["\']', f'applicationId = "{pkg}"', c)
                        c = re.sub(r'namespace\s*=\s*["\'].*?["\']', f'namespace = "{pkg}"', c)
                    else:
                        c = re.sub(r'applicationId\s+["\'].*?["\']', f'applicationId "{pkg}"', c)
                        c = re.sub(r'namespace\s+["\'].*?["\']', f'namespace "{pkg}"', c)
                    with open(b_path, 'w', encoding='utf-8') as f: 
                        f.write(c)
            
            java_dir = os.path.join(target_dir, 'app', 'src', 'main', 'java')
            old_main = None
            
            for root_dir, dirs, files in os.walk(java_dir):
                if 'MainActivity.kt' in files: 
                    old_main = os.path.join(root_dir, 'MainActivity.kt')
                    break
                    
            new_pkg_dir = os.path.join(java_dir, *pkg.split('.'))
            os.makedirs(new_pkg_dir, exist_ok=True)
            new_main = os.path.join(new_pkg_dir, 'MainActivity.kt')
            
            if old_main:
                with open(old_main, 'r', encoding='utf-8') as f: 
                    c = f.read()
                c = re.sub(r'^package\s+.*?\n', f'package {pkg}\n', c, flags=re.MULTILINE)
                with open(new_main, 'w', encoding='utf-8') as f: 
                    f.write(c)
                if os.path.abspath(old_main) != os.path.abspath(new_main): 
                    os.remove(old_main)
                    
            for root_dir, dirs, files in os.walk(java_dir, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root_dir, dir_name)
                    if not os.listdir(dir_path): 
                        os.rmdir(dir_path)
                        
            self.log(f">>> Gotowy projekt Ghost: {name}")
            self.scan_and_init_ghost()
            
        except Exception as e: 
            self.log(f"!!! BŁĄD: {e}")

    def delete_template(self):
        sel = self.combo_delete.get()
        if sel and "Brak" not in sel and messagebox.askyesno("OSTRZEŻENIE", f"Usunąć bezpowrotnie projekt {sel}?"):
            try: 
                shutil.rmtree(os.path.join(self.android_studio_dir, sel), ignore_errors=True)
                self.log(f">>> Projekt usunięty.")
                self.scan_and_init_ghost()
            except Exception as e: 
                self.log(f"!!! Błąd: {e}")

    def on_closing(self):
        self.save_settings()
        if os.path.exists(self.ghost_dir): 
            shutil.rmtree(self.ghost_dir, ignore_errors=True)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GhostMasterBuilder(root)
    root.mainloop()
