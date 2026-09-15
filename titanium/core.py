from __future__ import annotations
import hashlib, json, os, shutil, subprocess, sys, tempfile, urllib.request, zipfile
from pathlib import Path
from . import APP_NAME, VERSION, ANDROID_API, BUILD_TOOLS, GRADLE_VERSION

JDK_META_URL = "https://api.adoptium.net/v3/assets/latest/21/hotspot?architecture=x64&image_type=jdk&os=windows&vendor=eclipse&heap_size=normal"
ANDROID_TOOLS_URL = "https://dl.google.com/android/repository/commandlinetools-win-15859902_latest.zip"
ANDROID_TOOLS_SHA256 = "90ae805d20434428bffcb699c290860f19bb5f66a67e6b330067e3de801fb04a"
GRADLE_URL = f"https://services.gradle.org/distributions/gradle-{GRADLE_VERSION}-bin.zip"
ANDROID_LICENSE_URL = "https://developer.android.com/studio/terms"

class Paths:
    def __init__(self):
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or str(Path.home())
        self.root = Path(base) / "TitaniumAPKBuilder"
        self.app_dir = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent
        self.portable = self.app_dir / "runtime"
        self.portable_jdk = self.portable / "jdk"
        self.portable_gradle = self.portable / "gradle"
        self.portable_sdk = self.portable / "android-sdk"
        self.toolchain = self.root / "toolchain"
        self.jdk = self.toolchain / "jdk"
        self.sdk = self.toolchain / "android-sdk"
        self.gradle = self.toolchain / "gradle"
        self.workspace = self.root / "workspace"
        self.downloads = self.root / "downloads"
        self.config = self.root / "config.json"
        for p in (self.root, self.toolchain, self.workspace, self.downloads): p.mkdir(parents=True, exist_ok=True)

class ConfigStore:
    def __init__(self, path: Path): self.path = path
    def load(self):
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception: return {}
    def save(self, data):
        safe = {k:v for k,v in data.items() if k not in {"store_password","key_password"}}
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(safe, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.path)

class ToolchainManager:
    def __init__(self, paths: Paths, emit): self.p, self.emit = paths, emit
    @staticmethod
    def _find(root: Path, name: str):
        if root.exists():
            for x in root.rglob(name):
                if x.is_file(): return x
        return None
    @staticmethod
    def _sha256(path: Path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""): h.update(chunk)
        return h.hexdigest().lower()
    @staticmethod
    def _json(url: str):
        req = urllib.request.Request(url, headers={"User-Agent": f"{APP_NAME}/{VERSION}"})
        with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
    @staticmethod
    def _text(url: str):
        req = urllib.request.Request(url, headers={"User-Agent": f"{APP_NAME}/{VERSION}"})
        with urllib.request.urlopen(req, timeout=60) as r: return r.read().decode("utf-8").strip()
    def java_home(self):
        for root in (self.p.portable_jdk, self.p.jdk):
            x = self._find(root, "java.exe")
            if x: return x.parent.parent
        env = os.environ.get("JAVA_HOME")
        if env and (Path(env)/"bin/java.exe").exists(): return Path(env)
        x = shutil.which("java")
        return Path(x).resolve().parent.parent if x else None
    def sdk_root(self):
        for root in (self.p.portable_sdk, self.p.sdk):
            if (root/"cmdline-tools/latest/bin/sdkmanager.bat").exists(): return root
        for key in ("ANDROID_SDK_ROOT","ANDROID_HOME"):
            x = os.environ.get(key)
            if x and Path(x).exists(): return Path(x)
        x = Path(os.environ.get("LOCALAPPDATA", ""))/"Android/Sdk"
        return x if x.exists() else None
    def gradle_exe(self):
        for root in (self.p.portable_gradle, self.p.gradle):
            x = self._find(root, "gradle.bat")
            if x: return x
        x = shutil.which("gradle")
        return Path(x) if x else None
    def status(self):
        sdk = self.sdk_root()
        return {
            "JDK": str(self.java_home() or "missing"),
            "Android SDK": str(sdk or "missing"),
            f"Android API {ANDROID_API}": "ready" if sdk and (sdk/f"platforms/android-{ANDROID_API}").exists() else "missing",
            f"Build Tools {BUILD_TOOLS}": "ready" if sdk and (sdk/f"build-tools/{BUILD_TOOLS}").exists() else "missing",
            "Gradle": str(self.gradle_exe() or "missing"),
        }
    def ready(self): return all(v != "missing" for v in self.status().values())
    def env(self):
        env = os.environ.copy(); java, sdk = self.java_home(), self.sdk_root()
        if java:
            env["JAVA_HOME"] = str(java); env["PATH"] = str(java/"bin") + os.pathsep + env.get("PATH","")
        if sdk: env["ANDROID_SDK_ROOT"] = env["ANDROID_HOME"] = str(sdk)
        return env
    def _download(self, url, dest, label, expected_sha256=None):
        self.emit("log", f"Downloading {label}...")
        req = urllib.request.Request(url, headers={"User-Agent": f"{APP_NAME}/{VERSION}"})
        with urllib.request.urlopen(req, timeout=60) as r, open(dest,"wb") as f:
            total = int(r.headers.get("Content-Length") or 0); got = 0
            while True:
                b = r.read(1024*1024)
                if not b: break
                f.write(b); got += len(b)
                if total: self.emit("detail", f"{label}: {got*100//total}%")
        if expected_sha256:
            actual = self._sha256(dest)
            if actual != expected_sha256.lower():
                dest.unlink(missing_ok=True)
                raise RuntimeError(f"SHA-256 verification failed for {label}")
            self.emit("log", f"Verified SHA-256: {label}")
    def _extract_by_marker(self, archive, target, marker):
        temp = Path(tempfile.mkdtemp(prefix="titanium-", dir=self.p.root))
        try:
            with zipfile.ZipFile(archive) as z: z.extractall(temp)
            marker_path = self._find(temp, marker)
            if not marker_path: raise RuntimeError(f"Invalid archive: {marker} missing")
            root = marker_path.parent.parent
            shutil.rmtree(target, ignore_errors=True); shutil.copytree(root, target)
        finally: shutil.rmtree(temp, ignore_errors=True)
    def _jdk_package(self):
        data = self._json(JDK_META_URL)
        if not data: raise RuntimeError("No Temurin JDK package metadata returned")
        package = data[0]["binary"]["package"]
        return package["link"], package["checksum"]
    def provision(self):
        if not self.java_home():
            url, checksum = self._jdk_package()
            z = self.p.downloads/"jdk.zip"; self._download(url,z,"Temurin JDK 21",checksum); self._extract_by_marker(z,self.p.jdk,"java.exe"); z.unlink(missing_ok=True)
        if not self.gradle_exe():
            checksum = self._text(GRADLE_URL + ".sha256").split()[0]
            z = self.p.downloads/"gradle.zip"; self._download(GRADLE_URL,z,f"Gradle {GRADLE_VERSION}",checksum)
            temp = Path(tempfile.mkdtemp(prefix="titanium-gradle-", dir=self.p.root))
            try:
                with zipfile.ZipFile(z) as f: f.extractall(temp)
                root = next(x for x in temp.iterdir() if x.is_dir() and x.name.startswith("gradle-"))
                shutil.rmtree(self.p.gradle, ignore_errors=True); shutil.copytree(root,self.p.gradle)
            finally: shutil.rmtree(temp, ignore_errors=True); z.unlink(missing_ok=True)
        if not self.sdk_root() or not (self.sdk_root()/"cmdline-tools/latest/bin/sdkmanager.bat").exists():
            z = self.p.downloads/"android-tools.zip"; self._download(ANDROID_TOOLS_URL,z,"Android command-line tools",ANDROID_TOOLS_SHA256)
            temp = Path(tempfile.mkdtemp(prefix="titanium-sdk-", dir=self.p.root))
            try:
                with zipfile.ZipFile(z) as f: f.extractall(temp)
                src = temp/"cmdline-tools"; target = self.p.sdk/"cmdline-tools/latest"
                if not (src/"bin/sdkmanager.bat").exists(): raise RuntimeError("Invalid Android tools archive")
                shutil.rmtree(target, ignore_errors=True); target.parent.mkdir(parents=True,exist_ok=True); shutil.copytree(src,target)
            finally: shutil.rmtree(temp, ignore_errors=True); z.unlink(missing_ok=True)
        sdk = self.sdk_root() or self.p.sdk
        sm = sdk/"cmdline-tools/latest/bin/sdkmanager.bat"; env = self.env(); env["ANDROID_SDK_ROOT"] = env["ANDROID_HOME"] = str(sdk)
        # Install only the components Titanium actually needs. Feeding consent here applies
        # to the requested packages, instead of globally accepting unrelated SDK add-on licenses.
        args = [str(sm), f"--sdk_root={sdk}", "platform-tools", f"platforms;android-{ANDROID_API}", f"build-tools;{BUILD_TOOLS}"]
        r = subprocess.run(args,input="y\n"*40,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,encoding="utf-8",errors="replace")
        self.emit("detail", r.stdout[-6000:])
        if r.returncode: raise RuntimeError("Android SDK provisioning failed")
        if not self.ready(): raise RuntimeError("Toolchain readiness check failed")
