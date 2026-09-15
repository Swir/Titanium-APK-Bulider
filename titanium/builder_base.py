from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from . import AGP_VERSION, ANDROID_API

PACKAGE_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")


class AndroidBuilder:
    def __init__(self, paths, toolchain, emit):
        self.p, self.t, self.emit = paths, toolchain, emit

    def validate(self, c):
        if not c["app_name"]:
            raise ValueError("App name is required")
        if not PACKAGE_RE.fullmatch(c["package"]):
            raise ValueError("Package must look like com.example.app")
        if int(c["target_sdk"]) != ANDROID_API:
            raise ValueError(f"Target SDK must be {ANDROID_API} in this v10 build")
        if int(c["min_sdk"]) < 21 or int(c["min_sdk"]) > ANDROID_API:
            raise ValueError("Invalid Min SDK")
        if int(c["version_code"]) < 1:
            raise ValueError("Version code must be positive")
        if not re.fullmatch(r"[0-9A-Za-z._+-]+", c["version_name"]):
            raise ValueError("Version name contains unsupported characters")
        if c["source_type"] == "URL":
            if not re.match(r"^https?://", c["source"], re.I):
                raise ValueError("URL must start with http:// or https://")
        elif not c["source"]:
            raise ValueError("Select an HTML folder or ZIP")
        if c["build_mode"] == "Release" and c["sign_release"]:
            if not Path(c["keystore"]).is_file():
                raise ValueError("Select a valid keystore")
            if not c["store_password"] or not c["key_alias"] or not c["key_password"]:
                raise ValueError("Signing data is incomplete")

    def _web(self, c, stage):
        if c["source_type"] == "URL":
            return None
        dest = stage / "www"
        src = Path(c["source"])
        if c["source_type"] == "Folder":
            if not src.is_dir():
                raise ValueError("HTML folder does not exist")
            shutil.copytree(src, dest)
        else:
            if not src.is_file() or src.suffix.lower() != ".zip":
                raise ValueError("Select a valid ZIP")
            dest.mkdir(parents=True)
            with zipfile.ZipFile(src) as z:
                for member in z.infolist():
                    member_path = Path(member.filename)
                    if member_path.is_absolute() or ".." in member_path.parts:
                        raise ValueError("Unsafe path in ZIP")
                z.extractall(dest)
        if not (dest / "index.html").exists():
            hits = list(dest.rglob("index.html"))
            if len(hits) == 1:
                nested = hits[0].parent
                flat = stage / "flat"
                shutil.copytree(nested, flat)
                shutil.rmtree(dest)
                flat.rename(dest)
        if not (dest / "index.html").exists():
            raise ValueError("Web project must contain index.html")
        return dest

    @staticmethod
    def _j(value):
        return value.replace("\\", "\\\\").replace('"', '\\"')

    @staticmethod
    def _groovy(value):
        return value.replace("\\", "/").replace("'", "\\'")

    def _gradle(self, c, pkg):
        signing = ""
        signing_line = ""
        if c["sign_release"] and c["keystore"]:
            keystore = self._groovy(str(Path(c["keystore"]).resolve()))
            signing = f"""
    signingConfigs {{
        release {{
            storeFile file('{keystore}')
            storePassword System.getenv('TITANIUM_STORE_PASSWORD')
            keyAlias System.getenv('TITANIUM_KEY_ALIAS')
            keyPassword System.getenv('TITANIUM_KEY_PASSWORD')
        }}
    }}
"""
            signing_line = "            signingConfig signingConfigs.release\n"
        return f"""plugins {{
    id 'com.android.application'
}}

android {{
    namespace '{pkg}'
    compileSdk {ANDROID_API}

    defaultConfig {{
        applicationId '{pkg}'
        minSdk {c['min_sdk']}
        targetSdk {ANDROID_API}
        versionCode {c['version_code']}
        versionName '{c['version_name']}'
    }}
{signing}
    buildTypes {{
        debug {{
            debuggable true
        }}
        release {{
            minifyEnabled false
{signing_line}        }}
    }}
}}
"""

    def _main_activity(self, c, pkg, start_url, local):
        template = r'''package __PACKAGE__;

import android.Manifest;
import android.app.Activity;
import android.app.DownloadManager;
import android.content.ActivityNotFoundException;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.CookieManager;
import android.webkit.GeolocationPermissions;
import android.webkit.PermissionRequest;
import android.webkit.URLUtil;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.Toast;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class MainActivity extends Activity {
    private static final int REQ_WEB_PERMISSIONS = 4101;
    private static final int REQ_GEOLOCATION = 4102;
    private static final int REQ_FILE_CHOOSER = 4103;

    private static final boolean CAMERA_ENABLED = __CAMERA__;
    private static final boolean MICROPHONE_ENABLED = __MICROPHONE__;
    private static final boolean LOCATION_ENABLED = __LOCATION__;
    private static final boolean LOCAL_CONTENT = __LOCAL__;

    private FrameLayout root;
    private WebView webView;
    private ValueCallback<Uri[]> fileCallback;
    private PermissionRequest pendingWebPermission;
    private GeolocationPermissions.Callback pendingGeoCallback;
    private String pendingGeoOrigin;
    private View customView;
    private WebChromeClient.CustomViewCallback customViewCallback;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        root = new FrameLayout(this);
        webView = new WebView(this);
        root.addView(webView, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(root);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(LOCAL_CONTENT);
        settings.setAllowContentAccess(true);
        settings.setGeolocationEnabled(LOCATION_ENABLED);
        settings.setSupportMultipleWindows(false);
        if (LOCAL_CONTENT) {
            settings.setAllowFileAccessFromFileURLs(true);
            settings.setAllowUniversalAccessFromFileURLs(false);
        }

        webView.setWebViewClient(new TitaniumWebViewClient());
        webView.setWebChromeClient(new TitaniumChromeClient());
        webView.setDownloadListener((url, userAgent, contentDisposition, mimeType, contentLength) ->
                startDownload(url, userAgent, contentDisposition, mimeType));
        webView.loadUrl("__START_URL__");
    }

    private class TitaniumWebViewClient extends WebViewClient {
        private boolean route(Uri uri, String rawUrl) {
            String scheme = uri == null ? null : uri.getScheme();
            if (scheme == null) {
                return false;
            }
            scheme = scheme.toLowerCase(Locale.ROOT);
            if (scheme.equals("http") || scheme.equals("https") || scheme.equals("file")
                    || scheme.equals("about") || scheme.equals("data") || scheme.equals("blob")) {
                return false;
            }
            if (scheme.equals("javascript")) {
                return true;
            }
            try {
                if (scheme.equals("intent")) {
                    Intent intent = Intent.parseUri(rawUrl, Intent.URI_INTENT_SCHEME);
                    try {
                        startActivity(intent);
                    } catch (ActivityNotFoundException missing) {
                        String fallback = intent.getStringExtra("browser_fallback_url");
                        if (fallback != null && (fallback.startsWith("https://") || fallback.startsWith("http://"))) {
                            webView.loadUrl(fallback);
                        }
                    }
                    return true;
                }
                startActivity(new Intent(Intent.ACTION_VIEW, uri));
                return true;
            } catch (Exception error) {
                Toast.makeText(MainActivity.this, "No application can open this link", Toast.LENGTH_SHORT).show();
                return true;
            }
        }

        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            Uri uri = request.getUrl();
            return route(uri, uri == null ? "" : uri.toString());
        }

        @Override
        @SuppressWarnings("deprecation")
        public boolean shouldOverrideUrlLoading(WebView view, String url) {
            return route(Uri.parse(url), url);
        }
    }

    private class TitaniumChromeClient extends WebChromeClient {
        @Override
        public void onPermissionRequest(final PermissionRequest request) {
            runOnUiThread(() -> handleWebPermission(request, true));
        }

        @Override
        public void onPermissionRequestCanceled(PermissionRequest request) {
            if (pendingWebPermission == request) {
                pendingWebPermission = null;
            }
        }

        @Override
        public void onGeolocationPermissionsShowPrompt(
                String origin, GeolocationPermissions.Callback callback) {
            handleGeolocation(origin, callback, true);
        }

        @Override
        public boolean onShowFileChooser(
                WebView view,
                ValueCallback<Uri[]> callback,
                FileChooserParams params) {
            if (fileCallback != null) {
                fileCallback.onReceiveValue(null);
            }
            fileCallback = callback;
            try {
                Intent chooserIntent = params.createIntent();
                chooserIntent.addCategory(Intent.CATEGORY_OPENABLE);
                startActivityForResult(chooserIntent, REQ_FILE_CHOOSER);
                return true;
            } catch (ActivityNotFoundException error) {
                fileCallback = null;
                Toast.makeText(MainActivity.this, "No file picker is available", Toast.LENGTH_SHORT).show();
                return false;
            }
        }

        @Override
        public void onShowCustomView(View view, CustomViewCallback callback) {
            showFullscreen(view, callback);
        }

        @Override
        public void onHideCustomView() {
            hideFullscreen();
        }
    }

    private void handleWebPermission(PermissionRequest request, boolean allowPrompt) {
        if (request == null) {
            return;
        }
        List<String> grantedResources = new ArrayList<>();
        List<String> missingAndroidPermissions = new ArrayList<>();

        for (String resource : request.getResources()) {
            if (PermissionRequest.RESOURCE_VIDEO_CAPTURE.equals(resource) && CAMERA_ENABLED) {
                if (checkSelfPermission(Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
                    grantedResources.add(resource);
                } else if (!missingAndroidPermissions.contains(Manifest.permission.CAMERA)) {
                    missingAndroidPermissions.add(Manifest.permission.CAMERA);
                }
            } else if (PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(resource) && MICROPHONE_ENABLED) {
                if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                    grantedResources.add(resource);
                } else if (!missingAndroidPermissions.contains(Manifest.permission.RECORD_AUDIO)) {
                    missingAndroidPermissions.add(Manifest.permission.RECORD_AUDIO);
                }
            }
        }

        if (!missingAndroidPermissions.isEmpty() && allowPrompt) {
            pendingWebPermission = request;
            requestPermissions(missingAndroidPermissions.toArray(new String[0]), REQ_WEB_PERMISSIONS);
            return;
        }

        pendingWebPermission = null;
        if (grantedResources.isEmpty()) {
            request.deny();
        } else {
            request.grant(grantedResources.toArray(new String[0]));
        }
    }

    private void handleGeolocation(
            String origin,
            GeolocationPermissions.Callback callback,
            boolean allowPrompt) {
        if (!LOCATION_ENABLED) {
            callback.invoke(origin, false, false);
            return;
        }

        boolean fine = checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)
                == PackageManager.PERMISSION_GRANTED;
        boolean coarse = checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION)
                == PackageManager.PERMISSION_GRANTED;
        if (fine || coarse) {
            callback.invoke(origin, true, false);
            pendingGeoCallback = null;
            pendingGeoOrigin = null;
            return;
        }

        if (allowPrompt) {
            pendingGeoCallback = callback;
            pendingGeoOrigin = origin;
            requestPermissions(new String[] {
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION
            }, REQ_GEOLOCATION);
        } else {
            callback.invoke(origin, false, false);
            pendingGeoCallback = null;
            pendingGeoOrigin = null;
        }
    }

    @Override
    public void onRequestPermissionsResult(
            int requestCode,
            String[] permissions,
            int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQ_WEB_PERMISSIONS && pendingWebPermission != null) {
            PermissionRequest request = pendingWebPermission;
            pendingWebPermission = null;
            handleWebPermission(request, false);
        } else if (requestCode == REQ_GEOLOCATION && pendingGeoCallback != null) {
            GeolocationPermissions.Callback callback = pendingGeoCallback;
            String origin = pendingGeoOrigin;
            handleGeolocation(origin, callback, false);
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQ_FILE_CHOOSER && fileCallback != null) {
            Uri[] result = WebChromeClient.FileChooserParams.parseResult(resultCode, data);
            fileCallback.onReceiveValue(result);
            fileCallback = null;
        }
    }

    private void startDownload(
            String url,
            String userAgent,
            String contentDisposition,
            String mimeType) {
        try {
            Uri uri = Uri.parse(url);
            String scheme = uri.getScheme();
            if (scheme == null || (!scheme.equalsIgnoreCase("http") && !scheme.equalsIgnoreCase("https"))) {
                Toast.makeText(this, "This download type is not supported", Toast.LENGTH_SHORT).show();
                return;
            }

            DownloadManager.Request request = new DownloadManager.Request(uri);
            String fileName = URLUtil.guessFileName(url, contentDisposition, mimeType);
            request.setTitle(fileName);
            request.setDescription("Downloading from Titanium app");
            request.setNotificationVisibility(
                    DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
            request.setAllowedOverMetered(true);
            request.setAllowedOverRoaming(true);
            if (mimeType != null && !mimeType.isEmpty()) {
                request.setMimeType(mimeType);
            }
            String cookies = CookieManager.getInstance().getCookie(url);
            if (cookies != null && !cookies.isEmpty()) {
                request.addRequestHeader("Cookie", cookies);
            }
            if (userAgent != null && !userAgent.isEmpty()) {
                request.addRequestHeader("User-Agent", userAgent);
            }
            if (android.os.Build.VERSION.SDK_INT >= 29) {
                request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, fileName);
            }

            DownloadManager manager = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
            manager.enqueue(request);
            Toast.makeText(this, "Download started", Toast.LENGTH_SHORT).show();
        } catch (Exception error) {
            Toast.makeText(this, "Download failed to start", Toast.LENGTH_SHORT).show();
        }
    }

    private void showFullscreen(View view, WebChromeClient.CustomViewCallback callback) {
        if (customView != null) {
            callback.onCustomViewHidden();
            return;
        }
        customView = view;
        customViewCallback = callback;
        webView.setVisibility(View.GONE);
        root.addView(view, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
    }

    private void hideFullscreen() {
        if (customView == null) {
            return;
        }
        root.removeView(customView);
        customView = null;
        webView.setVisibility(View.VISIBLE);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_VISIBLE);
        if (customViewCallback != null) {
            customViewCallback.onCustomViewHidden();
            customViewCallback = null;
        }
    }

    @Override
    public void onBackPressed() {
        if (customView != null) {
            hideFullscreen();
        } else if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (fileCallback != null) {
            fileCallback.onReceiveValue(null);
            fileCallback = null;
        }
        if (pendingWebPermission != null) {
            pendingWebPermission.deny();
            pendingWebPermission = null;
        }
        if (webView != null) {
            root.removeView(webView);
            webView.stopLoading();
            webView.loadUrl("about:blank");
            webView.clearHistory();
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }
}
'''
        replacements = {
            "__PACKAGE__": pkg,
            "__START_URL__": self._j(start_url),
            "__CAMERA__": str(bool(c["camera"])).lower(),
            "__MICROPHONE__": str(bool(c["microphone"])).lower(),
            "__LOCATION__": str(bool(c["location"])).lower(),
            "__LOCAL__": str(bool(local)).lower(),
        }
        for key, value in replacements.items():
            template = template.replace(key, value)
        return template

    def generate(self, c):
        project = self.p.workspace / "current"
        shutil.rmtree(project, ignore_errors=True)
        project.mkdir(parents=True)

        stage = Path(tempfile.mkdtemp(prefix="web-", dir=self.p.root))
        try:
            web = self._web(c, stage)
            pkg = c["package"]
            java_dir = project / "app/src/main/java" / Path(*pkg.split("."))
            java_dir.mkdir(parents=True)
            (project / "app/src/main/res/values").mkdir(parents=True)
            assets = project / "app/src/main/assets/www"
            if web:
                shutil.copytree(web, assets)

            (project / "settings.gradle").write_text(
                "pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }\n"
                "dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); "
                "repositories { google(); mavenCentral() } }\n"
                "rootProject.name='TitaniumGeneratedApp'\n"
                "include ':app'\n",
                encoding="utf-8",
            )
            (project / "build.gradle").write_text(
                f"plugins {{ id 'com.android.application' version '{AGP_VERSION}' apply false }}\n",
                encoding="utf-8",
            )
            (project / "gradle.properties").write_text(
                "org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\n",
                encoding="utf-8",
            )
            (project / "app/build.gradle").write_text(self._gradle(c, pkg), encoding="utf-8")

            permissions = ['<uses-permission android:name="android.permission.INTERNET" />']
            if c["camera"]:
                permissions.append('<uses-permission android:name="android.permission.CAMERA" />')
            if c["microphone"]:
                permissions.append('<uses-permission android:name="android.permission.RECORD_AUDIO" />')
            if c["location"]:
                permissions.extend([
                    '<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />',
                    '<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />',
                ])

            cleartext = (
                "true"
                if c["source_type"] == "URL" and c["source"].lower().startswith("http://")
                else "false"
            )
            manifest = (
                '<manifest xmlns:android="http://schemas.android.com/apk/res/android">'
                + " ".join(permissions)
                + f'<application android:label="@string/app_name" android:usesCleartextTraffic="{cleartext}" '
                'android:hardwareAccelerated="true" android:theme="@android:style/Theme.Material.Light.NoActionBar">'
                f'<activity android:name=".MainActivity" android:exported="true" android:screenOrientation="{c["orientation"]}">'
                '<intent-filter><action android:name="android.intent.action.MAIN"/>'
                '<category android:name="android.intent.category.LAUNCHER"/></intent-filter>'
                '</activity></application></manifest>'
            )
            (project / "app/src/main/AndroidManifest.xml").write_text(manifest, encoding="utf-8")

            app_name = (
                c["app_name"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            (project / "app/src/main/res/values/strings.xml").write_text(
                f'<resources><string name="app_name">{app_name}</string></resources>',
                encoding="utf-8",
            )

            start_url = (
                c["source"]
                if c["source_type"] == "URL"
                else "file:///android_asset/www/index.html"
            )
            local = c["source_type"] != "URL"
            (java_dir / "MainActivity.java").write_text(
                self._main_activity(c, pkg, start_url, local),
                encoding="utf-8",
            )
            return project
        finally:
            shutil.rmtree(stage, ignore_errors=True)

    def build(self, c):
        self.validate(c)
        if not self.t.ready():
            raise RuntimeError("Prepare Build Engine first")
        project = self.generate(c)
        gradle = self.t.gradle_exe()
        variant = c["build_mode"]
        task = ("assemble" if c["export_format"] == "APK" else "bundle") + variant
        env = self.t.env()
        if c["sign_release"]:
            env.update(
                TITANIUM_STORE_PASSWORD=c["store_password"],
                TITANIUM_KEY_ALIAS=c["key_alias"],
                TITANIUM_KEY_PASSWORD=c["key_password"],
            )
        process = subprocess.Popen(
            [str(gradle), "--no-daemon", "--console=plain", task],
            cwd=project,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        for line in process.stdout or []:
            self.emit("detail", line.rstrip())
        if process.wait():
            raise RuntimeError("Gradle build failed")

        variant_lower = variant.lower()
        folder = project / (
            f"app/build/outputs/apk/{variant_lower}"
            if c["export_format"] == "APK"
            else f"app/build/outputs/bundle/{variant_lower}"
        )
        extension = ".apk" if c["export_format"] == "APK" else ".aab"
        files = list(folder.glob(f"*{extension}"))
        if not files:
            raise RuntimeError("Build artifact not found")
        output = Path(c["output_dir"])
        output.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", c["app_name"]) or "app"
        destination = output / f"{safe_name}-{c['version_name']}-{variant_lower}{extension}"
        shutil.copy2(max(files, key=lambda x: x.stat().st_mtime), destination)
        return destination
