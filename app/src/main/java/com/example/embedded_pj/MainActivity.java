package com.example.embedded_pj;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

import com.bumptech.glide.Glide;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class MainActivity extends AppCompatActivity {
    private boolean isSecurityModeOn;
    private SharedPreferences sharedPreferences;
    private static final String PREFS_NAME = "SecurityPrefs";
    private static final String SECURITY_MODE_KEY = "isSecurityModeOn";

    private ImageView securityImageView;
    private Retrofit retrofit;
    private ApiService apiService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // SharedPreferences 초기화
        sharedPreferences = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        isSecurityModeOn = sharedPreferences.getBoolean(SECURITY_MODE_KEY, true);

        // Retrofit 초기화
        retrofit = new Retrofit.Builder()
                .baseUrl("https://your-api-base-url.com/")  // 서버 기본 URL
                .addConverterFactory(GsonConverterFactory.create())
                .build();
        apiService = retrofit.create(ApiService.class);

        // 버튼 및 이미지 초기화
        securityImageView = findViewById(R.id.security_image);
        Button btnMode = findViewById(R.id.btn_mode);
        Button btnVideo = findViewById(R.id.btn_video);
        Button btnRecord = findViewById(R.id.btn_record);

        // 초기 상태 설정
        updateModeButtonText(btnMode);
        updateSecurityImageView();

        // 경비 모드 ON/OFF 클릭 이벤트
        btnMode.setOnClickListener(v -> {
            isSecurityModeOn = !isSecurityModeOn;
            updateModeButtonText(btnMode);
            saveSecurityModeState();
            updateSecurityImageView();
            Toast.makeText(this, isSecurityModeOn ? "경비 모드가 활성화되었습니다." : "경비 모드가 비활성화되었습니다.", Toast.LENGTH_SHORT).show();
        });

        // 실시간 영상 페이지로 이동
        btnVideo.setOnClickListener(v -> startNewActivity(LiveVideoActivity.class));

        // 침입 기록 페이지로 이동
        btnRecord.setOnClickListener(v -> startNewActivity(IntrusionRecordsActivity.class));

        // 서버로부터 침입 기록 상태 확인
        checkIntrusionStatus();
    }

    @Override
    protected void onResume() {
        super.onResume();
        // 액티비티가 다시 표시될 때 경비 모드 상태 유지 및 UI 업데이트
        isSecurityModeOn = sharedPreferences.getBoolean(SECURITY_MODE_KEY, true);
        Button btnMode = findViewById(R.id.btn_mode);
        updateModeButtonText(btnMode);
        updateSecurityImageView();
    }

    // 경비 모드 상태를 SharedPreferences에 저장
    private void saveSecurityModeState() {
        SharedPreferences.Editor editor = sharedPreferences.edit();
        editor.putBoolean(SECURITY_MODE_KEY, isSecurityModeOn);
        editor.apply();
    }

    // 경비 모드 버튼 텍스트 업데이트
    private void updateModeButtonText(Button btnMode) {
        btnMode.setText(isSecurityModeOn ? "경비 모드 ON" : "경비 모드 OFF");
    }

    // 새로운 액티비티를 시작하는 메서드
    private void startNewActivity(Class<?> activityClass) {
        Intent newIntent = new Intent(MainActivity.this, activityClass);
        startActivity(newIntent);
    }

    // 경비 모드 상태에 따라 이미지 업데이트
    private void updateSecurityImageView() {
        if (isSecurityModeOn) {
            securityImageView.setImageResource(R.drawable.security_on);  // 경비 모드 ON 이미지
        } else {
            securityImageView.setImageResource(R.drawable.security_off); // 경비 모드 OFF 이미지
        }
    }

    // 서버로부터 침입 기록 확인
    private void checkIntrusionStatus() {
        Handler handler = new Handler(Looper.getMainLooper());
        Runnable checkIntrusionRunnable = new Runnable() {
            @Override
            public void run() {
                // 서버로부터 침입 기록 상태 요청
                Call<IntrusionResponse> call = apiService.getIntrusionStatus();
                call.enqueue(new Callback<IntrusionResponse>() {
                    @Override
                    public void onResponse(Call<IntrusionResponse> call, Response<IntrusionResponse> response) {
                        if (response.isSuccessful() && response.body() != null) {
                            IntrusionResponse intrusionResponse = response.body();
                            if (intrusionResponse.isIntrusionDetected()) {
                                Glide.with(MainActivity.this)
                                        .load(R.drawable.intrusion_detected) // 침입 감지 시 이미지 변경
                                        .into(securityImageView);
                                Toast.makeText(MainActivity.this, "침입이 감지되었습니다!", Toast.LENGTH_LONG).show();
                            }
                        }
                    }

                    @Override
                    public void onFailure(Call<IntrusionResponse> call, Throwable t) {
                        Toast.makeText(MainActivity.this, "서버와 연결할 수 없습니다.", Toast.LENGTH_SHORT).show();
                    }
                });

                // 일정 시간 후 다시 체크
                handler.postDelayed(this, 5000); // 5초마다 서버에 상태 확인 요청
            }
        };

        handler.post(checkIntrusionRunnable);
    }
}
