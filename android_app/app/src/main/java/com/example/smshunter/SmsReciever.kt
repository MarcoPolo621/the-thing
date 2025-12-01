package com.example.smshunter

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import androidx.localbroadcastmanager.content.LocalBroadcastManager

class SmsReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Telephony.Sms.Intents.SMS_RECEIVED_ACTION) {
            val msgs = Telephony.Sms.Intents.getMessagesFromIntent(intent)
            for (sms in msgs) {
                val body = sms.messageBody
                val sender = sms.originatingAddress ?: "Unknown"

                SpamDetector.checkMessage(body) { verdict, reasons ->
                    MainActivity.logList.add(0, ScanLog(sender, body, verdict))
                    LocalBroadcastManager.getInstance(context).sendBroadcast(Intent("UPDATE_DASHBOARD"))

                    if (verdict == "phishing" || verdict == "suspicious") {
                        NotificationHelper.showWarning(context, sender, verdict, reasons)
                    }
                }
            }
        }
    }
}