package com.example.embedded_pj;

import com.google.gson.annotations.SerializedName;

public class IntrusionResponse {
    @SerializedName("intrusionDetected")  // 서버 JSON 응답에서 intrusionDetected 필드를 매핑
    private boolean intrusionDetected;

    // Getter 메서드
    public boolean isIntrusionDetected() {
        return intrusionDetected;
    }

    // Setter 메서드 (선택 사항으로, 서버에서 데이터만 읽어온다면 필요 없음)
    public void setIntrusionDetected(boolean intrusionDetected) {
        this.intrusionDetected = intrusionDetected;
    }
}
