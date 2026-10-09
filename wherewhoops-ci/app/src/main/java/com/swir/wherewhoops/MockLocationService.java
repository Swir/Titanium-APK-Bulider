package com.swir.wherewhoops;

import android.app.*;
import android.content.*;
import android.location.*;
import android.os.*;
import java.util.*;

public class MockLocationService extends Service {
    public static final String START="com.swir.wherewhoops.START";
    public static final String STOP="com.swir.wherewhoops.STOP";
    public static final String LAT="lat", LON="lon", LABEL="label";
    private static final String CH="wherewhoops_mock";
    private final Handler h=new Handler(Looper.getMainLooper());
    private final Set<String> providers=new LinkedHashSet<>();
    private LocationManager lm;
    private double lat,lon;
    private String label="Selected point";

    private final Runnable tick=new Runnable(){
        public void run(){ inject(); h.postDelayed(this,900); }
    };

    @Override public void onCreate(){
        super.onCreate();
        lm=(LocationManager)getSystemService(LOCATION_SERVICE);
        NotificationManager nm=(NotificationManager)getSystemService(NOTIFICATION_SERVICE);
        nm.createNotificationChannel(new NotificationChannel(CH,"Mock location",NotificationManager.IMPORTANCE_LOW));
    }

    @Override public int onStartCommand(Intent in,int flags,int id){
        if(in==null)return START_STICKY;
        if(STOP.equals(in.getAction())){ cleanup(); stopSelf(); return START_NOT_STICKY; }

        lat=in.getDoubleExtra(LAT,0);
        lon=in.getDoubleExtra(LON,0);
        label=in.getStringExtra(LABEL);
        if(label==null||label.isBlank())label="Selected point";
        startForeground(4107,notification());

        try{
            add(LocationManager.GPS_PROVIDER,false,true,false);
            add(LocationManager.NETWORK_PROVIDER,true,false,true);
            try{ add("fused",true,true,true); }catch(Exception ignored){}
            if(providers.isEmpty())throw new SecurityException("No provider");
            getSharedPreferences("wherewhoops",MODE_PRIVATE).edit().putBoolean("mock_active",true).apply();
            h.removeCallbacks(tick); h.post(tick);
        }catch(Exception e){
            send(false,"Enable Developer options → Select mock location app → WhereWhoops");
            cleanup(); stopSelf();
        }
        return START_REDELIVER_INTENT;
    }

    @SuppressWarnings("deprecation")
    private void add(String p,boolean net,boolean sat,boolean cell){
        try{lm.removeTestProvider(p);}catch(Exception ignored){}
        lm.addTestProvider(p,net,sat,cell,false,true,true,true,Criteria.POWER_LOW,Criteria.ACCURACY_FINE);
        lm.setTestProviderEnabled(p,true);
        providers.add(p);
    }

    private void inject(){
        boolean ok=false;
        for(String p:providers){
            try{
                Location l=new Location(p);
                l.setLatitude(lat); l.setLongitude(lon); l.setAltitude(20);
                l.setAccuracy(3); l.setSpeed(0); l.setBearing(0);
                l.setTime(System.currentTimeMillis());
                l.setElapsedRealtimeNanos(SystemClock.elapsedRealtimeNanos());
                lm.setTestProviderLocation(p,l); ok=true;
            }catch(Exception ignored){}
        }
        if(ok){
            getSharedPreferences("wherewhoops",MODE_PRIVATE).edit()
                .putBoolean("mock_active",true)
                .putLong("mock_last_tick",System.currentTimeMillis()).apply();
            send(true,String.format(Locale.US,"%.6f, %.6f",lat,lon));
        }
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
            .setContentIntent(op).setOngoing(true).setOnlyAlertOnce(true).addAction(a).build();
    }

    private void cleanup(){
        h.removeCallbacks(tick);
        for(String p:providers){
            try{lm.setTestProviderEnabled(p,false);}catch(Exception ignored){}
            try{lm.removeTestProvider(p);}catch(Exception ignored){}
        }
        providers.clear();
        getSharedPreferences("wherewhoops",MODE_PRIVATE).edit()
            .putBoolean("mock_active",false).putLong("mock_last_tick",0).apply();
        send(false,"Stopped");
        stopForeground(STOP_FOREGROUND_REMOVE);
    }

    private void send(boolean active,String msg){
        Intent i=new Intent("com.swir.wherewhoops.STATE").setPackage(getPackageName());
        i.putExtra("active",active); i.putExtra("message",msg); sendBroadcast(i);
    }

    @Override public void onDestroy(){ cleanup(); super.onDestroy(); }
    @Override public android.os.IBinder onBind(Intent i){ return null; }
}
