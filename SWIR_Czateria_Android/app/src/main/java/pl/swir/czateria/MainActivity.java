package pl.swir.czateria;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.stream.Collectors;

public class MainActivity extends Activity {
    private static final String CHAT_URL = "https://czateria.interia.pl/";
    private static final int FILE_CHOOSER_REQUEST = 7001;

    private WebView webView;
    private TextView statusText;
    private ValueCallback<Uri[]> fileCallback;
    private String swirScript = "";
    private String patchScript = "";
    private String defaultUserAgent = "";
    private boolean desktopMode = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        swirScript = readAsset("swir_app.js");
        patchScript = readAsset("swir_patch_v03.js");

        getWindow().setStatusBarColor(Color.rgb(7, 16, 25));
        getWindow().setNavigationBarColor(Color.rgb(7, 16, 25));

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.rgb(7, 16, 25));
        root.setOnApplyWindowInsetsListener((v, insets) -> {
            v.setPadding(0, insets.getSystemWindowInsetTop(), 0, insets.getSystemWindowInsetBottom());
            return insets;
        });

        root.addView(buildTopBar());

        statusText = new TextView(this);
        statusText.setText("SWIR Czateria+ v0.3 • uruchamianie");
        statusText.setTextColor(Color.rgb(148, 178, 200));
        statusText.setTextSize(10.5f);
        statusText.setPadding(dp(10), dp(4), dp(10), dp(4));
        statusText.setBackgroundColor(Color.rgb(8, 18, 30));
        root.addView(statusText);

        webView = new WebView(this);
        root.addView(webView, new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 0, 1f));

        setContentView(root);
        configureWebView();

        if (savedInstanceState != null) {
            webView.restoreState(savedInstanceState);
        } else {
            webView.loadUrl(CHAT_URL);
        }
    }

    private View buildTopBar() {
        HorizontalScrollView scroll = new HorizontalScrollView(this);
        scroll.setHorizontalScrollBarEnabled(false);
        scroll.setBackgroundColor(Color.rgb(9, 20, 32));

        LinearLayout bar = new LinearLayout(this);
        bar.setOrientation(LinearLayout.HORIZONTAL);
        bar.setGravity(Gravity.CENTER_VERTICAL);
        bar.setPadding(dp(5), dp(4), dp(5), dp(4));

        TextView title = new TextView(this);
        title.setText("⚡ SWIR");
        title.setTextColor(Color.WHITE);
        title.setTextSize(14f);
        title.setPadding(dp(7), 0, dp(7), 0);
        bar.addView(title);

        bar.addView(makeButton("MOD", v -> runJs("window.SWIR_APP&&SWIR_APP.openPanel()")));
        bar.addView(makeButton("Znajomi", v -> runJs("window.SWIR_APP&&SWIR_APP.openFriends()")));
        bar.addView(makeButton("CHNS", v -> runJs("window.SWIR_APP&&SWIR_APP.openChns()")));
        bar.addView(makeButton("📡", v -> {
            runJs("window.SWIR_APP&&SWIR_APP.requestFriends(true)");
            toast("Odświeżam znajomych…");
        }));
        bar.addView(makeButton("↻", v -> webView.reload()));
        bar.addView(makeButton("Tryb", v -> toggleUserAgent()));

        scroll.addView(bar, new HorizontalScrollView.LayoutParams(
                HorizontalScrollView.LayoutParams.WRAP_CONTENT,
                HorizontalScrollView.LayoutParams.WRAP_CONTENT));
        return scroll;
    }

    private Button makeButton(String label, View.OnClickListener listener) {
        Button b = new Button(this);
        b.setText(label);
        b.setAllCaps(false);
        b.setTextSize(10.5f);
        b.setTextColor(Color.WHITE);
        b.setBackgroundColor(Color.rgb(18, 38, 57));
        b.setPadding(dp(7), 0, dp(7), 0);
        b.setMinWidth(0);
        b.setMinHeight(dp(32));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT, dp(34));
        lp.setMargins(dp(2), 0, dp(2), 0);
        b.setLayoutParams(lp);
        b.setOnClickListener(listener);
        return b;
    }

    private void configureWebView() {
        defaultUserAgent = WebSettings.getDefaultUserAgent(this);
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setJavaScriptCanOpenWindowsAutomatically(true);
        s.setSupportMultipleWindows(false);
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        s.setUserAgentString(defaultUserAgent);

        webView.addJavascriptInterface(new SwirBridge(), "SwirAndroid");

        CookieManager cookies = CookieManager.getInstance();
        cookies.setAcceptCookie(true);
        cookies.setAcceptThirdPartyCookies(webView, true);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                String host = uri.getHost();
                if (host == null || host.endsWith("interia.pl")) return false;
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, uri));
                    return true;
                } catch (Exception ignored) {
                    return false;
                }
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                statusText.setText("Załadowano • czekam na silnik CZATerii…");
                Handler h = new Handler(Looper.getMainLooper());
                h.postDelayed(() -> injectSwir(false), 900);
                h.postDelayed(() -> injectSwir(false), 2400);
                h.postDelayed(() -> injectSwir(false), 5000);
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView view,
                                             ValueCallback<Uri[]> callback,
                                             FileChooserParams params) {
                if (fileCallback != null) fileCallback.onReceiveValue(null);
                fileCallback = callback;
                Intent i = new Intent(Intent.ACTION_GET_CONTENT);
                i.addCategory(Intent.CATEGORY_OPENABLE);
                i.setType("*/*");
                try {
                    startActivityForResult(Intent.createChooser(i, "Wybierz plik"), FILE_CHOOSER_REQUEST);
                    return true;
                } catch (Exception e) {
                    fileCallback = null;
                    return false;
                }
            }
        });
    }

    private void injectSwir(boolean force) {
        String gate = force
                ? "(typeof CHNS!=='undefined'?'READY':'WAIT')"
                : "(typeof CHNS==='undefined'?'WAIT':(window.__SWIR_APP_INJECTED?'ALREADY':(window.__SWIR_APP_INJECTED=true,'READY')))";

        webView.evaluateJavascript(gate, result -> {
            if (result == null) return;
            if (result.contains("READY")) {
                webView.evaluateJavascript(swirScript, baseResult ->
                        webView.evaluateJavascript(patchScript, patchResult ->
                                statusText.setText("✅ SWIR v0.3 aktywny • GIF COPY • NO ADS • Friend 85→159")));
            } else if (result.contains("ALREADY")) {
                webView.evaluateJavascript(patchScript, null);
                statusText.setText("✅ SWIR v0.3 aktywny");
            }
        });
    }

    private void runJs(String js) {
        if (webView != null) {
            webView.evaluateJavascript("(function(){try{" + js + "}catch(e){console.error(e)}})();", null);
        }
    }

    private void toggleUserAgent() {
        desktopMode = !desktopMode;
        if (desktopMode) {
            webView.getSettings().setUserAgentString(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                    "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36");
            statusText.setText("Tryb WWW: desktop");
        } else {
            webView.getSettings().setUserAgentString(defaultUserAgent);
            statusText.setText("Tryb WWW: mobile");
        }
        webView.reload();
    }

    private String readAsset(String name) {
        try (BufferedReader br = new BufferedReader(new InputStreamReader(getAssets().open(name)))) {
            return br.lines().collect(Collectors.joining("\n"));
        } catch (Exception e) {
            String msg = e.getMessage() == null ? "unknown" : e.getMessage().replace("'", "");
            return "console.error('Brak modułu SWIR: " + msg + "');";
        }
    }

    private void toast(String text) {
        Toast.makeText(this, text, Toast.LENGTH_SHORT).show();
    }

    private int dp(int value) {
        return (int) (value * getResources().getDisplayMetrics().density);
    }

    public class SwirBridge {
        @JavascriptInterface
        public void copyText(String text) {
            runOnUiThread(() -> {
                try {
                    ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                    clipboard.setPrimaryClip(ClipData.newPlainText("SWIR GIF", text == null ? "" : text));
                    toast("📋 Skopiowano GIF/link");
                } catch (Exception e) {
                    toast("Nie udało się skopiować");
                }
            });
        }

        @JavascriptInterface
        public void toast(String text) {
            runOnUiThread(() -> MainActivity.this.toast(text == null ? "SWIR" : text));
        }

        @JavascriptInterface
        public void shareText(String text) {
            runOnUiThread(() -> {
                try {
                    Intent share = new Intent(Intent.ACTION_SEND);
                    share.setType("text/plain");
                    share.putExtra(Intent.EXTRA_TEXT, text == null ? "" : text);
                    startActivity(Intent.createChooser(share, "Udostępnij GIF"));
                } catch (Exception e) {
                    toast("Nie udało się udostępnić GIF-a");
                }
            });
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == FILE_CHOOSER_REQUEST) {
            Uri[] result = null;
            if (resultCode == RESULT_OK && data != null && data.getData() != null) {
                result = new Uri[]{data.getData()};
            }
            if (fileCallback != null) fileCallback.onReceiveValue(result);
            fileCallback = null;
        }
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        if (webView != null) webView.saveState(outState);
        super.onSaveInstanceState(outState);
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.stopLoading();
            webView.destroy();
        }
        super.onDestroy();
    }
}
