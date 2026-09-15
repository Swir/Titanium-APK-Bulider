from __future__ import annotations
import re, shutil, subprocess, tempfile, zipfile
from pathlib import Path
from . import ANDROID_API, AGP_VERSION

PACKAGE_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")

class AndroidBuilder:
    def __init__(self, paths, toolchain, emit): self.p,self.t,self.emit = paths,toolchain,emit
    def validate(self,c):
        if not c["app_name"]: raise ValueError("App name is required")
        if not PACKAGE_RE.fullmatch(c["package"]): raise ValueError("Package must look like com.example.app")
        if int(c["target_sdk"]) != ANDROID_API: raise ValueError(f"Target SDK must be {ANDROID_API} in this v10 build")
        if int(c["min_sdk"]) < 21 or int(c["min_sdk"]) > ANDROID_API: raise ValueError("Invalid Min SDK")
        if int(c["version_code"]) < 1: raise ValueError("Version code must be positive")
        if c["source_type"] == "URL":
            if not re.match(r"^https?://",c["source"],re.I): raise ValueError("URL must start with http:// or https://")
        elif not c["source"]: raise ValueError("Select an HTML folder or ZIP")
        if c["build_mode"]=="Release" and c["sign_release"]:
            if not Path(c["keystore"]).is_file(): raise ValueError("Select a valid keystore")
            if not c["store_password"] or not c["key_alias"] or not c["key_password"]: raise ValueError("Signing data is incomplete")
    def _web(self,c,stage):
        if c["source_type"]=="URL": return None
        dest=stage/"www"; src=Path(c["source"])
        if c["source_type"]=="Folder":
            if not src.is_dir(): raise ValueError("HTML folder does not exist")
            shutil.copytree(src,dest)
        else:
            if not src.is_file() or src.suffix.lower()!=".zip": raise ValueError("Select a valid ZIP")
            dest.mkdir(parents=True)
            with zipfile.ZipFile(src) as z:
                for m in z.infolist():
                    p=Path(m.filename)
                    if p.is_absolute() or ".." in p.parts: raise ValueError("Unsafe path in ZIP")
                z.extractall(dest)
        if not (dest/"index.html").exists():
            hits=list(dest.rglob("index.html"))
            if len(hits)==1:
                nested=hits[0].parent; flat=stage/"flat"; shutil.copytree(nested,flat); shutil.rmtree(dest); flat.rename(dest)
        if not (dest/"index.html").exists(): raise ValueError("Web project must contain index.html")
        return dest
    @staticmethod
    def _j(s): return s.replace("\\","\\\\").replace('"','\\"')
    def generate(self,c):
        project=self.p.workspace/"current"; shutil.rmtree(project,ignore_errors=True); project.mkdir(parents=True)
        stage=Path(tempfile.mkdtemp(prefix="web-",dir=self.p.root)); web=None
        try: web=self._web(c,stage)
        except Exception: shutil.rmtree(stage,ignore_errors=True); raise
        pkg=c["package"]; java=project/"app/src/main/java"/Path(*pkg.split(".")); java.mkdir(parents=True)
        (project/"app/src/main/res/values").mkdir(parents=True); assets=project/"app/src/main/assets/www"
        if web: shutil.copytree(web,assets)
        shutil.rmtree(stage,ignore_errors=True)
        (project/"settings.gradle").write_text("pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }\ndependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }\nrootProject.name='TitaniumGeneratedApp'\ninclude ':app'\n",encoding="utf-8")
        (project/"build.gradle").write_text(f"plugins {{ id 'com.android.application' version '{AGP_VERSION}' apply false }}\n",encoding="utf-8")
        (project/"gradle.properties").write_text("org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\n",encoding="utf-8")
        signing=use=""
        if c["sign_release"] and c["keystore"]:
            ks=Path(c["keystore"]).resolve().as_posix()
            signing=f"signingConfigs {{ release {{ storeFile file('{ks}'); storePassword System.getenv('TITANIUM_STORE_PASSWORD'); keyAlias System.getenv('TITANIUM_KEY_ALIAS'); keyPassword System.getenv('TITANIUM_KEY_PASSWORD') }} }}"
            use="signingConfig signingConfigs.release"
        gradle=f"""plugins {{ id 'com.android.application' }}
android {{ namespace '{pkg}'; compileSdk {ANDROID_API}; {signing}
defaultConfig {{ applicationId '{pkg}'; minSdk {c['min_sdk']}; targetSdk {ANDROID_API}; versionCode {c['version_code']}; versionName '{c['version_name']}' }}
buildTypes {{ release {{ minifyEnabled false; {use} }} debug {{ debuggable true }} }} }}
"""
        (project/"app/build.gradle").write_text(gradle,encoding="utf-8")
        perms=['<uses-permission android:name="android.permission.INTERNET" />']
        if c["camera"]: perms.append('<uses-permission android:name="android.permission.CAMERA" />')
        if c["microphone"]: perms.append('<uses-permission android:name="android.permission.RECORD_AUDIO" />')
        if c["location"]: perms += ['<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />','<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />']
        clear="true" if c["source_type"]=="URL" and c["source"].lower().startswith("http://") else "false"
        manifest=f'''<manifest xmlns:android="http://schemas.android.com/apk/res/android">{' '.join(perms)}<application android:label="@string/app_name" android:usesCleartextTraffic="{clear}" android:hardwareAccelerated="true" android:theme="@android:style/Theme.Material.Light.NoActionBar"><activity android:name=".MainActivity" android:exported="true" android:screenOrientation="{c['orientation']}"><intent-filter><action android:name="android.intent.action.MAIN"/><category android:name="android.intent.category.LAUNCHER"/></intent-filter></activity></application></manifest>'''
        (project/"app/src/main/AndroidManifest.xml").write_text(manifest,encoding="utf-8")
        name=c["app_name"].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        (project/"app/src/main/res/values/strings.xml").write_text(f'<resources><string name="app_name">{name}</string></resources>',encoding="utf-8")
        url=c["source"] if c["source_type"]=="URL" else "file:///android_asset/www/index.html"; local=str(c["source_type"]!="URL").lower()
        code=f'''package {pkg};
import android.app.Activity; import android.os.Bundle; import android.webkit.*;
public class MainActivity extends Activity {{ private WebView w; public void onCreate(Bundle b) {{ super.onCreate(b); w=new WebView(this); WebSettings s=w.getSettings(); s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setAllowFileAccess({local}); s.setAllowContentAccess(true); if({local}){{s.setAllowFileAccessFromFileURLs(true);s.setAllowUniversalAccessFromFileURLs(false);}} w.setWebViewClient(new WebViewClient()); w.setWebChromeClient(new WebChromeClient()); setContentView(w); w.loadUrl("{self._j(url)}"); }} public void onBackPressed() {{ if(w!=null&&w.canGoBack())w.goBack();else super.onBackPressed(); }} }}'''
        (java/"MainActivity.java").write_text(code,encoding="utf-8")
        return project
    def build(self,c):
        self.validate(c)
        if not self.t.ready(): raise RuntimeError("Prepare Build Engine first")
        project=self.generate(c); gradle=self.t.gradle_exe(); variant=c["build_mode"]; task=("assemble" if c["export_format"]=="APK" else "bundle")+variant
        env=self.t.env()
        if c["sign_release"]:
            env.update(TITANIUM_STORE_PASSWORD=c["store_password"],TITANIUM_KEY_ALIAS=c["key_alias"],TITANIUM_KEY_PASSWORD=c["key_password"])
        p=subprocess.Popen([str(gradle),"--no-daemon","--console=plain",task],cwd=project,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8",errors="replace")
        for line in p.stdout or []: self.emit("detail",line.rstrip())
        if p.wait(): raise RuntimeError("Gradle build failed")
        v=variant.lower(); folder=project/(f"app/build/outputs/apk/{v}" if c["export_format"]=="APK" else f"app/build/outputs/bundle/{v}"); ext=".apk" if c["export_format"]=="APK" else ".aab"
        files=list(folder.glob(f"*{ext}"))
        if not files: raise RuntimeError("Build artifact not found")
        out=Path(c["output_dir"]); out.mkdir(parents=True,exist_ok=True); safe=re.sub(r"[^A-Za-z0-9._-]+","_",c["app_name"]) or "app"; dest=out/f"{safe}-{c['version_name']}-{v}{ext}"; shutil.copy2(max(files,key=lambda x:x.stat().st_mtime),dest); return dest
