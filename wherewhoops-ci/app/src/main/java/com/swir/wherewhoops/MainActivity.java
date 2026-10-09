package com.swir.wherewhoops;

import android.Manifest;
import android.app.*;
import android.content.*;
import android.content.pm.PackageManager;
import android.graphics.*;
import android.graphics.drawable.GradientDrawable;
import android.os.*;
import android.provider.Settings;
import android.view.*;
import android.webkit.*;
import android.widget.*;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.json.*;

public class MainActivity extends Activity {
    private static final int BG=Color.rgb(5,8,20), PANEL=Color.rgb(11,17,33), CYAN=Color.rgb(37,201,255), TEXT=Color.rgb(239,247,255), MUTED=Color.rgb(145,166,193), GREEN=Color.rgb(63,226,151), RED=Color.rgb(255,82,105);
    private static final int REQ_LOC=10,REQ_NOTIF=11;

    private WebView map;
    private EditText search;
    private TextView name,coords,status;
    private Button teleport;
    private double lat=59.9139,lon=10.7522;
    private String label="Oslo, Norway";
    private boolean active=false;
    private boolean starting=false;

    private final BroadcastReceiver rx=new BroadcastReceiver(){
        @Override public void onReceive(Context c,Intent i){
            if(!"com.swir.wherewhoops.STATE".equals(i.getAction())) return;
            starting=false;
            active=i.getBooleanExtra("active",false);
            updateState();
            String m=i.getStringExtra("message");
            if(m!=null && !m.isBlank() && !"Stopped".equals(m)){
                Toast.makeText(MainActivity.this,m,Toast.LENGTH_LONG).show();
            }
        }
    };

    @Override public void onCreate(Bundle b){
        super.onCreate(b);
        getWindow().setStatusBarColor(BG);
        getWindow().setNavigationBarColor(BG);
        setContentView(ui());
        setupMap();
        setPoint(label,lat,lon,11,false);
    }

    @Override public void onStart(){
        super.onStart();
        IntentFilter f=new IntentFilter("com.swir.wherewhoops.STATE");
        if(Build.VERSION.SDK_INT>=33) registerReceiver(rx,f,RECEIVER_NOT_EXPORTED);
        else registerReceiver(rx,f);
    }

    @Override public void onStop(){
        try{ unregisterReceiver(rx); }catch(Exception ignored){}
        super.onStop();
    }

    @Override public void onResume(){
        super.onResume();
        active=isAlive();
        if(active) starting=false;
        updateState();
    }

    private View ui(){
        LinearLayout root=new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(14),dp(10),dp(14),dp(10));
        root.setBackgroundColor(BG);

        LinearLayout head=new LinearLayout(this);
        head.setGravity(Gravity.CENTER_VERTICAL);
        TextView title=t("WhereWhoops",26,TEXT,true);
        head.addView(title,new LinearLayout.LayoutParams(0,dp(48),1));

        TextView by=t("by Swir",12,CYAN,true);
        by.setPadding(0,0,dp(10),0);
        head.addView(by);

        status=t("● SETUP NEEDED",11,Color.rgb(255,190,87),true);
        status.setPadding(dp(10),dp(7),dp(10),dp(7));
        status.setBackground(box(PANEL,14,1,Color.rgb(40,60,85)));
        head.addView(status);
        root.addView(head);

        TextView sub=t("Pick any place on Earth. Search it or tap the map.",13,MUTED,false);
        sub.setPadding(0,0,0,dp(8));
        root.addView(sub);

        Button setup=btn("SETUP MOCK LOCATION",Color.rgb(36,62,90));
        setup.setOnClickListener(v->openDeveloperOptions());
        root.addView(setup,new LinearLayout.LayoutParams(-1,dp(44)));

        LinearLayout sr=new LinearLayout(this);
        sr.setPadding(0,dp(8),0,dp(8));

        search=new EditText(this);
        search.setSingleLine();
        search.setHint("Search city, country, address, landmark…");
        search.setTextColor(TEXT);
        search.setHintTextColor(Color.rgb(100,125,155));
        search.setBackground(box(PANEL,14,1,Color.rgb(38,55,80)));
        search.setPadding(dp(12),0,dp(8),0);
        search.setOnEditorActionListener((v,a,e)->{ doSearch(); return true; });
        sr.addView(search,new LinearLayout.LayoutParams(0,dp(48),1));

        Button find=btn("FIND",CYAN);
        LinearLayout.LayoutParams fp=new LinearLayout.LayoutParams(dp(74),dp(48));
        fp.setMargins(dp(7),0,0,0);
        sr.addView(find,fp);
        find.setOnClickListener(v->doSearch());
        root.addView(sr);

        map=new WebView(this);
        map.setBackgroundColor(PANEL);
        root.addView(map,new LinearLayout.LayoutParams(-1,0,1));

        LinearLayout card=new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);
        card.setPadding(dp(12),dp(9),dp(12),dp(12));
        card.setBackground(box(PANEL,16,1,Color.rgb(37,54,79)));

        name=t("Selected",16,TEXT,true);
        coords=t("",12,CYAN,false);
        card.addView(name);
        card.addView(coords);

        HorizontalScrollView hs=new HorizontalScrollView(this);
        hs.setHorizontalScrollBarEnabled(false);
        LinearLayout q=new LinearLayout(this);
        q.setPadding(0,dp(7),0,dp(7));
        quick(q,"Oslo",59.9139,10.7522);
        quick(q,"Warsaw",52.2297,21.0122);
        quick(q,"New York",40.7128,-74.0060);
        quick(q,"Tokyo",35.6762,139.6503);
        quick(q,"Dubai",25.2048,55.2708);
        quick(q,"Sydney",-33.8688,151.2093);
        hs.addView(q);
        card.addView(hs,new LinearLayout.LayoutParams(-1,dp(50)));

        teleport=btn("TELEPORT HERE",CYAN);
        teleport.setTextSize(16);
        teleport.setTextColor(Color.rgb(3,13,21));
        teleport.setOnClickListener(v->{
            if(active) stopMock();
            else prepareStart();
        });
        card.addView(teleport,new LinearLayout.LayoutParams(-1,dp(52)));
        root.addView(card);

        return root;
    }

    @SuppressWarnings("SetJavaScriptEnabled")
    private void setupMap(){
        WebSettings s=map.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        map.addJavascriptInterface(new Bridge(),"Android");
        map.setWebViewClient(new WebViewClient());
        map.loadUrl("file:///android_asset/map.html");
    }

    private void setPoint(String n,double a,double b,int zoom,boolean retarget){
        label=n;
        lat=a;
        lon=b;
        if(name!=null){
            name.setText(n);
            coords.setText(String.format(Locale.US,"%.6f, %.6f",a,b));
        }
        if(map!=null) map.evaluateJavascript("window.setPoint&&setPoint("+a+","+b+","+zoom+");",null);
        if(retarget && active){
            sendMockTarget();
            Toast.makeText(this,"Teleporting to "+n,Toast.LENGTH_SHORT).show();
        }
    }

    private void doSearch(){
        String q=search.getText().toString().trim();
        if(q.isEmpty()) return;

        search.setEnabled(false);
        new Thread(()->{
            try{
                String u="https://nominatim.openstreetmap.org/search?format=jsonv2&limit=8&q="+URLEncoder.encode(q,StandardCharsets.UTF_8);
                HttpURLConnection c=(HttpURLConnection)new URL(u).openConnection();
                c.setConnectTimeout(10000);
                c.setReadTimeout(12000);
                c.setRequestProperty("User-Agent","WhereWhoops/0.1.1 by Swir");

                StringBuilder sb=new StringBuilder();
                try(BufferedReader r=new BufferedReader(new InputStreamReader(c.getInputStream(),StandardCharsets.UTF_8))){
                    String x;
                    while((x=r.readLine())!=null) sb.append(x);
                }

                JSONArray a=new JSONArray(sb.toString());
                runOnUiThread(()->showResults(a));
            }catch(Exception e){
                runOnUiThread(()->Toast.makeText(this,"Search failed: "+e.getMessage(),Toast.LENGTH_LONG).show());
            }finally{
                runOnUiThread(()->search.setEnabled(true));
            }
        }).start();
    }

    private void showResults(JSONArray a){
        if(a.length()==0){
            Toast.makeText(this,"No places found.",Toast.LENGTH_SHORT).show();
            return;
        }

        String[] items=new String[a.length()];
        for(int i=0;i<a.length();i++){
            try{ items[i]=a.getJSONObject(i).getString("display_name"); }
            catch(Exception e){ items[i]="Place"; }
        }

        new AlertDialog.Builder(this)
            .setTitle("Choose location")
            .setItems(items,(d,w)->{
                try{
                    JSONObject o=a.getJSONObject(w);
                    setPoint(o.getString("display_name"),o.getDouble("lat"),o.getDouble("lon"),15,true);
                    if(!active) Toast.makeText(this,"Place selected — tap TELEPORT HERE",Toast.LENGTH_SHORT).show();
                }catch(Exception ignored){}
            })
            .setNegativeButton("CANCEL",null)
            .show();
    }

    private void prepareStart(){
        if(!allowed()){
            new AlertDialog.Builder(this)
                .setTitle("Mock location not enabled")
                .setMessage("Open Developer options, choose “Select mock location app”, then select WhereWhoops.")
                .setPositiveButton("OPEN SETTINGS",(d,w)->openDeveloperOptions())
                .setNegativeButton("CANCEL",null)
                .show();
            return;
        }

        if(checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)!=PackageManager.PERMISSION_GRANTED){
            requestPermissions(new String[]{Manifest.permission.ACCESS_FINE_LOCATION,Manifest.permission.ACCESS_COARSE_LOCATION},REQ_LOC);
            return;
        }

        if(Build.VERSION.SDK_INT>=33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED){
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},REQ_NOTIF);
        }

        startMock();
    }

    private void startMock(){
        starting=true;
        updateState();
        sendMockTarget();
    }

    private void sendMockTarget(){
        Intent i=new Intent(this,MockLocationService.class).setAction(MockLocationService.START);
        i.putExtra(MockLocationService.LAT,lat);
        i.putExtra(MockLocationService.LON,lon);
        i.putExtra(MockLocationService.LABEL,label);
        startForegroundService(i);
    }

    private void stopMock(){
        startService(new Intent(this,MockLocationService.class).setAction(MockLocationService.STOP));
        active=false;
        starting=false;
        updateState();
    }

    private boolean isAlive(){
        android.content.SharedPreferences p=getSharedPreferences("wherewhoops",MODE_PRIVATE);
        long x=p.getLong("mock_last_tick",0);
        return p.getBoolean("mock_active",false) && x>0 && System.currentTimeMillis()-x<6000;
    }

    private boolean allowed(){
        try{
            AppOpsManager a=(AppOpsManager)getSystemService(APP_OPS_SERVICE);
            return a.checkOpNoThrow(AppOpsManager.OPSTR_MOCK_LOCATION,android.os.Process.myUid(),getPackageName())
                    ==AppOpsManager.MODE_ALLOWED;
        }catch(Exception e){
            return false;
        }
    }

    private void openDeveloperOptions(){
        try{ startActivity(new Intent(Settings.ACTION_APPLICATION_DEVELOPMENT_SETTINGS)); }
        catch(Exception e){ startActivity(new Intent(Settings.ACTION_SETTINGS)); }
    }

    private void updateState(){
        if(status==null||teleport==null) return;

        if(active){
            status.setText("● MOCK ACTIVE");
            status.setTextColor(GREEN);
            teleport.setEnabled(true);
            teleport.setText("STOP MOCK");
            teleport.setTextColor(Color.WHITE);
            teleport.setBackground(box(RED,14,0,RED));
            return;
        }

        if(starting){
            status.setText("● STARTING…");
            status.setTextColor(CYAN);
            teleport.setEnabled(false);
            teleport.setText("STARTING…");
            teleport.setTextColor(TEXT);
            teleport.setBackground(box(Color.rgb(40,65,90),14,0,Color.rgb(40,65,90)));
            return;
        }

        boolean ok=allowed();
        status.setText(ok?"● READY":"● SETUP NEEDED");
        status.setTextColor(ok?GREEN:Color.rgb(255,190,87));
        teleport.setEnabled(true);
        teleport.setText("TELEPORT HERE");
        teleport.setTextColor(Color.rgb(3,13,21));
        teleport.setBackground(box(CYAN,14,0,CYAN));
    }

    @Override public void onRequestPermissionsResult(int r,String[] p,int[] g){
        super.onRequestPermissionsResult(r,p,g);
        if(r==REQ_LOC){
            if(checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)==PackageManager.PERMISSION_GRANTED){
                startMock();
            }else{
                Toast.makeText(this,"Precise location permission is required for mock mode.",Toast.LENGTH_LONG).show();
            }
        }
    }

    public final class Bridge{
        @JavascriptInterface public void onMapTap(double a,double b){
            runOnUiThread(()->setPoint("Dropped pin",a,b,15,true));
        }
    }

    private void quick(LinearLayout q,String n,double a,double b){
        Button x=btn(n,Color.rgb(42,69,101));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,dp(38));
        lp.setMargins(0,0,dp(6),0);
        q.addView(x,lp);
        x.setOnClickListener(v->{
            setPoint(n,a,b,13,true);
            if(!active) Toast.makeText(this,n+" selected — tap TELEPORT HERE",Toast.LENGTH_SHORT).show();
        });
    }

    private TextView t(String s,int z,int c,boolean bold){
        TextView v=new TextView(this);
        v.setText(s);
        v.setTextSize(z);
        v.setTextColor(c);
        if(bold) v.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
        return v;
    }

    private Button btn(String s,int c){
        Button b=new Button(this);
        b.setText(s);
        b.setTextColor(TEXT);
        b.setTextSize(11);
        b.setAllCaps(false);
        b.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
        b.setBackground(box(c,13,0,c));
        return b;
    }

    private GradientDrawable box(int c,int r,int sw,int sc){
        GradientDrawable g=new GradientDrawable();
        g.setColor(c);
        g.setCornerRadius(dp(r));
        if(sw>0) g.setStroke(dp(sw),sc);
        return g;
    }

    private int dp(int x){
        return Math.round(x*getResources().getDisplayMetrics().density);
    }
}
