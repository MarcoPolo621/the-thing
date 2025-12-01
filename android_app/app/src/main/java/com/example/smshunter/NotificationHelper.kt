package com.example.smshunter

import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.os.Build
import androidx.core.app.NotificationCompat

object NotificationHelper {
    fun showWarning(context: Context, sender: String, verdict: String, reasons: String) {
        val channelId = "spam_alerts"
        val mgr = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            mgr.createNotificationChannel(NotificationChannel(channelId, "Alerts", NotificationManager.IMPORTANCE_HIGH))
        }

        val notification = NotificationCompat.Builder(context, channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle("⚠ ${verdict.uppercase()} DETECTED")
            .setContentText("Sender: $sender")
            .setStyle(NotificationCompat.BigTextStyle().bigText(reasons))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .build()

        mgr.notify(System.currentTimeMillis().toInt(), notification)
    }
}