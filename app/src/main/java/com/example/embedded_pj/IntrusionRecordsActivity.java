package com.example.embedded_pj;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.example.embedded_pj.databinding.ActivityIntrusionRecordsBinding;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public class IntrusionRecordsActivity extends AppCompatActivity {
    private final List<Date> records = new ArrayList<>();
    private boolean isDescending = true;
    private ActivityIntrusionRecordsBinding binding;
    private IntrusionRecordAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityIntrusionRecordsBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        // RecyclerView 설정
        binding.recordList.setLayoutManager(new LinearLayoutManager(this));
        adapter = new IntrusionRecordAdapter(records, this::openDetailRecord);
        binding.recordList.setAdapter(adapter);

        // 더미 데이터 생성 (실제 구현에서는 데이터베이스나 API에서 가져와야 합니다)
        generateDummyRecords();
        displayRecords();

        // 상단 타이틀 클릭 시 메인 페이지로 이동
        binding.titleIntrusion.setOnClickListener(v -> {
            Intent intent = new Intent(IntrusionRecordsActivity.this, MainActivity.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(intent);
        });

        // 정렬 버튼 클릭 이벤트
        binding.sortButton.setOnClickListener(v -> {
            isDescending = !isDescending;
            binding.sortButton.setText(isDescending ? getString(R.string.sort_descending) : getString(R.string.sort_ascending));
            displayRecords();
        });
    }

    private void generateDummyRecords() {
        try {
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy.MM.dd. HH:mm:ss", Locale.getDefault());
            records.add(sdf.parse("2023.11.25. 14:00:00"));
            records.add(sdf.parse("2023.11.24. 12:30:00"));
            records.add(sdf.parse("2023.11.26. 18:15:00"));
        } catch (Exception e) {
            Log.e("IntrusionRecordsActivity", "Error parsing date", e);
        }
    }

    private void displayRecords() {
        if (isDescending) {
            records.sort((d1, d2) -> d2.compareTo(d1));  // 내림차순 정렬
        } else {
            records.sort(Date::compareTo);  // 오름차순 정렬
        }
        adapter.notifyDataSetChanged();
    }

    private void openDetailRecord(Date record) {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy.MM.dd. HH:mm:ss", Locale.getDefault());
        Intent intent = new Intent(IntrusionRecordsActivity.this, DetailRecordActivity.class);
        intent.putExtra("RECORD_TIME", sdf.format(record));
        intent.putExtra("DETECTED_OBJECT", "사람");
        intent.putExtra("RISK_LEVEL", "중");
        intent.putExtra("DURATION", "00:01:30");
        startActivity(intent);
    }
}