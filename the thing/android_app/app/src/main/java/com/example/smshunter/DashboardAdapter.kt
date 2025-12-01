package com.example.smshunter

import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView

data class ScanLog(val sender: String, val msg: String, val verdict: String)

class DashboardAdapter(private val logs: List<ScanLog>) : RecyclerView.Adapter<DashboardAdapter.VH>() {
    class VH(v: View) : RecyclerView.ViewHolder(v) {
        val t1: TextView = v.findViewById(android.R.id.text1)
        val t2: TextView = v.findViewById(android.R.id.text2)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
        val v = LayoutInflater.from(parent.context).inflate(android.R.layout.simple_list_item_2, parent, false)
        return VH(v)
    }

    override fun onBindViewHolder(holder: VH, position: Int) {
        val log = logs[position]
        holder.t1.text = "${log.verdict.uppercase()}: ${log.sender}"
        holder.t2.text = log.msg
        
        when(log.verdict) {
            "phishing" -> holder.t1.setTextColor(Color.RED)
            "suspicious" -> holder.t1.setTextColor(Color.parseColor("#FFA500"))
            else -> holder.t1.setTextColor(Color.parseColor("#006400"))
        }
    }
    override fun getItemCount() = logs.size
}