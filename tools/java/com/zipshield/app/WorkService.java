package com.zipshield.app;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;

/** Minimal foreground service: keeps large-file work alive in background
 *  and shows live progress in a notification. No network, no data leaves the phone. */
public class WorkService extends Service {

    private static final String CH = "zipshield_work";
    private static final int ID = 1001;
    private static NotificationManager nm;
    private static Notification.Builder builder;
    private static String title = "ZipShield Pro";

    @Override
    public void onCreate() {
        super.onCreate();
        nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel ch = new NotificationChannel(CH, "ZipShield file work",
                    NotificationManager.IMPORTANCE_LOW);
            ch.setDescription("Progress of large ZIP encryption / decryption");
            nm.createNotificationChannel(ch);
        }
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        title = (intent != null && intent.getStringExtra("title") != null)
                ? intent.getStringExtra("title") : "ZipShield Pro";
        builder = new Notification.Builder(this, CH)
                .setContentTitle(title)
                .setContentText("Starting...")
                .setSmallIcon(android.R.drawable.stat_sys_download)
                .setOngoing(true)
                .setProgress(100, 0, false);
        try {
            startForeground(ID, builder.build());
        } catch (Exception e) {
            // Foreground start can fail on some devices; the in-app progress bar still works.
        }
        return START_NOT_STICKY;
    }

    public static void update(Context ctx, int pct, String text) {
        try {
            if (nm == null || builder == null) return;
            builder.setProgress(100, pct, false).setContentText(text);
            nm.notify(ID, builder.build());
        } catch (Exception ignored) {}
    }

    public static void finish(Context ctx, String text) {
        try {
            if (nm == null || builder == null) return;
            builder.setProgress(0, 0, false).setContentText(text).setOngoing(false);
            nm.notify(ID, builder.build());
        } catch (Exception ignored) {}
        try {
            Intent i = new Intent(ctx, WorkService.class);
            ctx.stopService(i);
        } catch (Exception ignored) {}
    }

    @Override public IBinder onBind(Intent intent) { return null; }
}
