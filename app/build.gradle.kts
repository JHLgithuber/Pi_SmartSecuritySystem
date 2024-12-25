plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.example.embedded_pj"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.embedded_pj"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }

    // 뷰 바인딩 활성화
    viewBinding {
        enable = true
    }
}

dependencies {
    // AndroidX 및 Material 라이브러리
    implementation(libs.appcompat)
    implementation(libs.material)
    implementation(libs.activity)
    implementation(libs.constraintlayout)
    // 네트워크 요청 및 이미지 로딩 라이브러리 추가
    implementation("com.squareup.retrofit2:retrofit:2.9.0")             // Retrofit for API requests
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")       // Retrofit converter for JSON
    implementation("com.github.bumptech.glide:glide:4.12.0")           // Glide for image loading
    annotationProcessor("com.github.bumptech.glide:compiler:4.12.0")   // Glide annotation processor
    // 테스트 라이브러리
    testImplementation(libs.junit)
    androidTestImplementation(libs.ext.junit)
    androidTestImplementation(libs.espresso.core)
    // 코루틴을 이용한 비동기 네트워크 처리 (선택 사항)
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.6.0")
}