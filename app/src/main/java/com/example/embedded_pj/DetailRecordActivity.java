package com.example.embedded_pj;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.VideoView;
import androidx.appcompat.app.AppCompatActivity;

public class DetailRecordActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_detail_record);

        // 기록 정보 표시
        TextView recordDetails = findViewById(R.id.record_details);
        Button btnMainMenu = findViewById(R.id.btn_main_menu);
        Button btnLiveVideo = findViewById(R.id.btn_live_video);

        Intent intent = getIntent();
        String recordTime = intent.getStringExtra("RECORD_TIME");
        String detectedObject = intent.getStringExtra("DETECTED_OBJECT");
        String riskLevel = intent.getStringExtra("RISK_LEVEL");
        String duration = intent.getStringExtra("DURATION");

        recordDetails.setText(String.format(
                "일시: %s\n탐지 대상: %s\n위험 수준: %s\n체류 시간: %s",
                recordTime, detectedObject, riskLevel, duration
        ));

        // VideoView 설정 및 동영상 재생
        VideoView videoView = findViewById(R.id.video_view);
        Uri videoUri = Uri.parse("android.resource://" + getPackageName() + "/" + R.raw.wa); // 비디오 링크 나중에 수정하삼
        videoView.setVideoURI(videoUri);
        videoView.start();  // 비디오 재생 시작

        // 메인 메뉴로 이동
        btnMainMenu.setOnClickListener(v -> {
            Intent mainMenuIntent = new Intent(DetailRecordActivity.this, MainActivity.class);
            mainMenuIntent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(mainMenuIntent);
        });

        // 실시간 영상 페이지로 이동
        btnLiveVideo.setOnClickListener(v -> {
            Intent liveVideoIntent = new Intent(DetailRecordActivity.this, LiveVideoActivity.class);
            startActivity(liveVideoIntent);
        });
    }
}
