package com.example.embedded_pj;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.VideoView;
import androidx.appcompat.app.AppCompatActivity;
import com.example.embedded_pj.databinding.ActivityLiveVideoBinding;

public class LiveVideoActivity extends AppCompatActivity {
    private boolean isAlertOn;
    private boolean isSoundOn;
    private SharedPreferences sharedPreferences;
    private static final String PREFS_NAME = "LiveVideoPrefs";
    private static final String ALERT_MODE_KEY = "isAlertOn";
    private static final String SOUND_MODE_KEY = "isSoundOn";

    // 뷰 바인딩 객체
    private ActivityLiveVideoBinding binding;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // 뷰 바인딩 초기화
        binding = ActivityLiveVideoBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        // SharedPreferences 초기화
        sharedPreferences = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        isAlertOn = sharedPreferences.getBoolean(ALERT_MODE_KEY, false);
        isSoundOn = sharedPreferences.getBoolean(SOUND_MODE_KEY, false);

        // 초기 상태 설정
        updateAlertButtonText();
        updateSoundButtonText();

        // 상단 타이틀 클릭 시 메인 페이지로 이동
        binding.titleLiveVideo.setOnClickListener(v -> {
            Intent intent = new Intent(LiveVideoActivity.this, MainActivity.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            startActivity(intent);
        });

        // VideoView 설정
        VideoView liveVideoView = findViewById(R.id.live_video_view);
        String videoUrl = "http://your-streaming-url.com/live";  // 실시간 스트리밍 URL을 사용
        liveVideoView.setVideoPath(videoUrl);
        liveVideoView.start();  // 스트리밍 재생 시작

        // 경고 알림 ON/OFF 클릭 이벤트
        binding.btnAlert.setOnClickListener(v -> {
            isAlertOn = !isAlertOn;
            updateAlertButtonText();
            saveAlertModeState();
        });

        // 환경음 ON/OFF 클릭 이벤트
        binding.btnSound.setOnClickListener(v -> {
            isSoundOn = !isSoundOn;
            updateSoundButtonText();
            saveSoundModeState();
        });
    }

    // 경고 알림 상태 저장
    private void saveAlertModeState() {
        SharedPreferences.Editor editor = sharedPreferences.edit();
        editor.putBoolean(ALERT_MODE_KEY, isAlertOn);
        editor.apply();
    }

    // 환경음 상태 저장
    private void saveSoundModeState() {
        SharedPreferences.Editor editor = sharedPreferences.edit();
        editor.putBoolean(SOUND_MODE_KEY, isSoundOn);
        editor.apply();
    }

    // 경고 알림 버튼 텍스트 업데이트
    private void updateAlertButtonText() {
        binding.btnAlert.setText(isAlertOn ? "경고 알림 ON" : "경고 알림 OFF");
    }

    // 환경음 버튼 텍스트 업데이트
    private void updateSoundButtonText() {
        binding.btnSound.setText(isSoundOn ? "환경음 ON" : "환경음 OFF");
    }
}