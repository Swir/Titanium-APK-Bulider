package com.swir.wherewhoops;

import android.app.*;
import android.content.*;
import android.location.*;
import android.os.*;
import androidx.annotation.Nullable;
import com.google.android.gms.location.FusedLocationProviderClient;
import com.google.android.gms.location.LocationServices;
import java.util.*;

public class MockLocationService extends Service {
    public static final String START="com.swir.wherewhoops.START";
    public static final String STOP="com.swir.wherewhoops.STOP";
    public static final String LAT="lat", LON="lon", LABEL="label";
    private static final String CH="wherewhoops_mock";

    private final Handler h=new Handler(Looper.getMainLooper());
    private final Set<String> providers=new LinkedHashSet<>();
    private LocationManager lm;
    private FusedLocationProviderClient fused;
    private double lat,lon;
    private String label="Selected point";
    private boolean running=false;
    private boolean fusedReady=false;
    private boolean announced=false;

    private final Runnable tick=new Runnable(){
        @Override public void run(){
            injectAll();
            if(running) h.postDelayed(this,850);
        }
    };

    @Override public void onCreate(){
        super.onCreate();
        lm=(LocationManager)getSystemService(LOCATION_SERVICE);
        fused=LocationServices.getFusedLocationProviderClient(this);
        NotificationManager nm=(NotificationManager)getSystemService(NOTIFICATION_SERVICE);
        nm.createNotificationChannel(new NotificationChannel(CH,"Mock location",NotificationManager.IMPORTANCE_LOW));
    }

    @Override public int onStartCommand(Intent in,int flags,int id){
        if(in==null) return START_STICKY;
        if(STOP.equals(in.getAction())){
            cleanup(true);
            stopSelf();
            return START_NOT_STICKY;
        }

        lat=in.getDoubleExtra(LAT,0);
        lon=in.getDoubleExtra(LON,0);
        label=in.getStringExtra(LABEL);
        if(label==null||label.isBlank()) label="Selected point";

        startForeground(4107,notification());

        if(running){
            refreshNotification();
            injectAll();
            send(true,"Teleported to "+label);
            return START_REDELIVER_INTENT;
        }

        if(!mockAllowed()){
            send(false,"Select WhereWhoops in Developer options → Select mock location app");
            cleanup(false);
            stopSelf();
            return START_NOT_STICKY;
        }

        setupLegacyProviders();

        fused.setMockMode(true)
            .addOnSuccessListener(v->{
                fusedReady=true;
                running=true;
                announced=false;
                h.removeCallbacks(tick);
                injectAll();
                h.postDelayed(tick,850);
            })
            .addOnFailureListener(e->{
                fusedReady=false;
                if(!providers.isEmpty()){
                    running=true;
                    announced=true;
                    h.removeCallbacks(tick);
                    injectLegacy();
                    h.postDelayed(tick,850);
                    send(true,"Limited mock active (GPS/Network). Google Fused mock failed.");
                }else{
                    send(false,"Mock start failed: "+friendly(e));
                    cleanup(false);
                    stopSelf();
                }
            });

        return START_REDELIVER_INTENT;
    }

    private boolean mockAllowed(){
        try{
            AppOpsManager a=(AppOpsManager)getSystemService(APP_OPS_SERVICE);
            return a.checkOpNoThrow(AppOpsManager.OPSTR_MOCK_LOCATION,android.os.Process.myUid(),getPackageName())
                    ==AppOpsManager.MODE_ALLOWED;
        }catch(Exception e){
            return false;
        }
    }

    private void setupLegacyProviders(){
        providers.clear();
        tryAdd(LocationManager.GPS_PROVIDER,false,true,false);
        tryAdd(LocationManager.NETWORK_PROVIDER,true,false,true);
    }

    @SuppressWarnings("deprecation")
    private void tryAdd(String p,boolean net,boolean sat,boolean cell){
        try{
            try{ lm.removeTestProvider(p); }catch(Exception ignored){}
            lm.addTestProvider(p,net,sat,cell,false,true,true,true,Criteria.POWER_LOW,Criteria.ACCURACY_FINE);
            lm.setTestProviderEnabled(p,true);
            providers.add(p);
        }catch(Exception ignored){}
    }

    private Location makeLocation(String provider){
        Location l=new Location(provider);
        l.setLatitude(lat);
        l.setLongitude(lon);
        l.setAltitude(20.0);
        l.setAccuracy(2.0f);
        l.setSpeed(0.0f);
        l.setBearing(0.0f);
        l.setTime(System.currentTimeMillis());
        l.setElapsedRealtimeNanos(SystemClock.elapsedRealtimeNanos());
        if(Build.VERSION.SDK_INT>=26){
            l.setVerticalAccuracyMeters(2.0f);
            l.setSpeedAccuracyMetersPerSecond(0.2f);
            l.setBearingAccuracyDegrees(1.0f);
        }
        return l;
    }

    private void injectAll(){
        if(!running && !fusedReady) return;
        injectLegacy();

        if(fusedReady){
            Location fl=makeLocation("fused");
            fused.setMockLocation(fl)
                .addOnSuccessListener(v->{
                    markHeartbeat();
                    if(!announced){
                        announced=true;
                        send(true,"Mock active: GPS + Network + Google Fused");
                    }
                })
                .addOnFailureListener(e->{
                    fusedReady=false;
                    if(!providers.isEmpty()){
                        markHeartbeat();
                        send(true,"Google Fused stopped; legacy GPS/Network still active");
                    }else{
                        send(false,"Mock injection failed: "+friendly(e));
                    }
                });
        }else if(!providers.isEmpty()){
            markHeartbeat();
        }
    }

    private void injectLegacy(){
        for(String p:providers){
            try{ lm.setTestProviderLocation(p,makeLocation(p)); }catch(Exception ignored){}
        }
    }

    private void markHeartbeat(){
        getSharedPreferences("wherewhoops",MODE_PRIVATE).edit()
            .putBoolean("mock_active",true)
            .putLong("mock_last_tick",System.currentTimeMillis())
            .putFloat("mock_lat",(float)lat)
            .putFloat("mock_lon",(float)lon)
            .apply();
    }

    private Notification notification(){
        Intent open=new Intent(this,MainActivity.class);
        PendingIntent op=PendingIntent.getActivity(this,1,open,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        Intent stop=new Intent(this,MockLocationService.class).setAction(STOP);
        PendingIntent sp=PendingIntent.getService(this,2,stop,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE);
        Notification.Action a=new Notification.Action.Builder(android.R.drawable.ic_media_pause,"STOP MOCK",sp).build();
        return new Notification.Builder(this,CH)
            .setSmallIcon(android.R.drawable.ic_menu_mylocation)
            .setContentTitle("WhereWhoops is teleporting")
            .setContentText(label)
            .setContentIntent(op)
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .addAction(a)
            .build();
    }

    private void refreshNotification(){
        ((NotificationManager)getSystemService(NOTIFICATION_SERVICE)).notify(4107,notification());
    }

    private void cleanup(boolean announce){
        running=false;
        fusedReady=false;
        announced=false;
        h.removeCallbacks(tick);

        try{ fused.setMockMode(false); }catch(Exception ignored){}

        for(String p:providers){
            try{ lm.setTestProviderEnabled(p,false); }catch(Exception ignored){}
            try{ lm.removeTestProvider(p); }catch(Exception ignored){}
        }
        providers.clear();

        getSharedPreferences("wherewhoops",MODE_PRIVATE).edit()
            .putBoolean("mock_active",false)
            .putLong("mock_last_tick",0)
            .apply();

        if(announce) send(false,"Stopped");
        stopForeground(STOP_FOREGROUND_REMOVE);
    }

    private String friendly(Throwable e){
        String m=e==null?null:e.getMessage();
        return (m==null||m.isBlank()) ? e.getClass().getSimpleName() : m;
    }

    private void send(boolean active,String msg){
        Intent i=new Intent("com.swir.wherewhoops.STATE").setPackage(getPackageName());
        i.putExtra("active",active);
        i.putExtra("message",msg);
        sendBroadcast(i);
    }

    @Override public void onDestroy(){
        cleanup(false);
        super.onDestroy();
    }

    @Override public android.os.IBinder onBind(Intent i){ return null; }
}
