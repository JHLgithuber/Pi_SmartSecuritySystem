package com.example.embedded_pj;

import retrofit2.Call;
import retrofit2.http.GET;

public interface ApiService {
    // 침입 기록 상태를 확인하기 위한 GET 요청
    @GET("getIntrusionStatus")  // 서버의 API 엔드포인트. 실제 서버 URL에 맞춰 변경 필요
    Call<IntrusionResponse> getIntrusionStatus();
}
