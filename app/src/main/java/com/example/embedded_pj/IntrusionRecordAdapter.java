package com.example.embedded_pj;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.embedded_pj.databinding.ItemIntrusionRecordBinding;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class IntrusionRecordAdapter extends RecyclerView.Adapter<IntrusionRecordAdapter.RecordViewHolder> {

    private final List<Date> records;
    private final OnRecordClickListener onRecordClickListener;

    public interface OnRecordClickListener {
        void onRecordClick(Date record);
    }

    public IntrusionRecordAdapter(List<Date> records, OnRecordClickListener onRecordClickListener) {
        this.records = records;
        this.onRecordClickListener = onRecordClickListener;
    }

    @NonNull
    @Override
    public RecordViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        ItemIntrusionRecordBinding binding = ItemIntrusionRecordBinding.inflate(LayoutInflater.from(parent.getContext()), parent, false);
        return new RecordViewHolder(binding);
    }

    @Override
    public void onBindViewHolder(@NonNull RecordViewHolder holder, int position) {
        Date record = records.get(position);
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy.MM.dd. HH:mm:ss", Locale.getDefault());
        holder.binding.recordTime.setText(sdf.format(record));
        holder.itemView.setOnClickListener(v -> onRecordClickListener.onRecordClick(record));
    }

    @Override
    public int getItemCount() {
        return records.size();
    }

    static class RecordViewHolder extends RecyclerView.ViewHolder {
        ItemIntrusionRecordBinding binding;

        public RecordViewHolder(ItemIntrusionRecordBinding binding) {
            super(binding.getRoot());
            this.binding = binding;
        }
    }
}