package com.example.smshunter

import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

object SpamDetector {
    private const val API_URL = "http://10.0.2.2:5000/predict"
    private val client = OkHttpClient()

    fun checkMessage(messageBody: String, callback: (String, String) -> Unit) {
        val json = JSONObject().put("message", messageBody)
        val body = json.toString().toRequestBody("application/json".toMediaType())
        val request = Request.Builder().url(API_URL).post(body).build()

        Thread {
            try {
                client.newCall(request).execute().use { response ->
                    if (response.isSuccessful) {
                        val respJson = JSONObject(response.body?.string())
                        callback(respJson.getString("verdict"), respJson.getString("reasons"))
                    }
                }
            } catch (e: Exception) { e.printStackTrace() }
        }.start()
    }
}