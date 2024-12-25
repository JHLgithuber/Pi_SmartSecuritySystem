package com.example.embedded_pj;

import android.os.Parcel;
import android.os.Parcelable;

public class RecordDetails implements Parcelable {
    private String recordTime;
    private String detectedObject;
    private String riskLevel;
    private String duration;

    public RecordDetails(String recordTime, String detectedObject, String riskLevel, String duration) {
        this.recordTime = recordTime;
        this.detectedObject = detectedObject;
        this.riskLevel = riskLevel;
        this.duration = duration;
    }

    protected RecordDetails(Parcel in) {
        recordTime = in.readString();
        detectedObject = in.readString();
        riskLevel = in.readString();
        duration = in.readString();
    }

    public static final Creator<RecordDetails> CREATOR = new Creator<RecordDetails>() {
        @Override
        public RecordDetails createFromParcel(Parcel in) {
            return new RecordDetails(in);
        }

        @Override
        public RecordDetails[] newArray(int size) {
            return new RecordDetails[size];
        }
    };

    public String getRecordTime() {
        return recordTime;
    }

    public String getDetectedObject() {
        return detectedObject;
    }

    public String getRiskLevel() {
        return riskLevel;
    }

    public String getDuration() {
        return duration;
    }

    @Override
    public int describeContents() {
        return 0;
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeString(recordTime);
        dest.writeString(detectedObject);
        dest.writeString(riskLevel);
        dest.writeString(duration);
    }
}
