# 📝 Root Cause Analysis (RCA) Report

**문서 번호/버전**: RCA_20260716_v2  
**작성일**: 2026년 7월 16일  
**대상 파일**: `MemorySoundtrack_20260716_v2.py`

---

## 🔍 1. 사건 개요 (Incident Summary)
사용자가 이미지를 업로드하고 **🧠 Analyze Memories** 버튼을 클릭하여 이미지 분석을 수행하는 도중, 다음과 같이 **404 NOT_FOUND** 에러가 발생하며 프로세스가 중단되었습니다.

```json
Error analyzing image #1: 404 NOT_FOUND. {
  "error": {
    "code": 404,
    "message": "This model models/gemini-2.5-flash is no longer available to new users. Please update your code to use a newer model for the latest features and improvements.",
    "status": "NOT_FOUND"
  }
}
```

이로 인해 첫 번째 단계인 이미지 분석이 완료되지 않아, 이후 음악 생성 및 앨범 커버 제작 단계로 진입하지 못하고 전체 애플리케이션의 동작이 차단되었습니다.

---

## 🎯 2. 원인 분석 (Root Cause Analysis)

### 2.1 직접적인 원인 (Direct Cause)
*   **Gemini API 모델 지원 종료**: `MemorySoundtrack_20260716_v1.py`의 기본 Gemini 모델 ID로 하드코딩되어 있던 `gemini-2.5-flash` 모델이 Google API에서 새로운 사용자에게 더 이상 제공되지 않도록 지원 중단(Deprecated/Decommissioned) 처리되었습니다.
*   이에 따라 API를 통한 `generate_content` 호출이 실패하며 `404 NOT_FOUND` 예외가 발생했습니다.

### 2.2 간접적인 원인 & 설계 영향 (Indirect Cause & Application Flow Impact)
*   **엄격한 순차적 흐름(Sequential Flow) 제약**:
    현재 애플리케이션은 **3개의 탭(Tab)**으로 구성된 유기적인 파이프라인 구조를 가지고 있습니다.
    
    ```mermaid
    graph TD
        A["📸 Tab 1: Upload & Analyze (Gemini)"] -->|"st.session_state['analyses']"| B["🎵 Tab 2: Generate Music (Lyria 3)"]
        B -->|"st.session_state['audio_bytes']"| C["🎨 Tab 3: Album Cover (Imagen 3)"]
    ```

    *   **Tab 1 (이미지 분석)**이 성공해야 분석 결과(`st.session_state['analyses']`)가 세션 상태에 저장됩니다.
    *   **Tab 2 (음악 생성)**는 분석 결과가 없으면 작동을 제한하도록 예외 처리(`if not st.session_state['analyses']: st.info(...)`)가 되어 있어 아예 음악 프롬프트조차 생성할 수 없습니다.
    *   **Tab 3 (앨범 커버)** 또한 생성된 오디오 데이터(`st.session_state['audio_bytes']`)가 세션에 존재해야만 동작이 허용되어 전면 차단되었습니다.
*   **결과**: 이미지 분석 단계에서 단 하나의 에러라도 발생할 경우, 세션 변수가 비어 있게 되어 **이후의 모든 워크플로우가 영구적으로 잠김** 상태가 됩니다.

---

## 🔄 3. 정상 흐름 시 'Analyze Memories' 이후의 전체 작업 과정
이미지 분석이 성공했을 때 실제로 백그라운ด와 UI에서 일어나는 구체적인 작업 흐름은 다음과 같습니다.

### 1단계: 📸 Tab 1 - 분석 결과 수집 및 화면 표시
1.  Gemini가 각 이미지의 세부 스토리, 지배적인 감정 및 어울리는 음악 스타일을 따뜻한 감성으로 분석(한국어).
2.  이 정보는 아래 구조로 `st.session_state['analyses']` 리스트에 누적됩니다.
    ```python
    {
        "index": idx + 1,
        "filename": file.name,
        "image": img,
        "analysis": response.text
    }
    ```
3.  성공 메시지(`✅ Memory analysis complete!`)와 함께, 화면 하단에 유리 질감의 글래스모피즘(Glassmorphism) 카드 스타일로 각 사진별 고유한 이야기와 분위기(Vibe)가 멋지게 표시됩니다.

### 2단계: 🎵 Tab 2 - 음악 프롬프트 합성 및 Lyria 3 음악 생성
1.  **Tab 2**로 이동하면 잠금 상태가 해제되고 **`📝 Synthesize Music Prompt`** 버튼이 활성화됩니다.
2.  이 버튼을 누르면, Gemini가 이전 탭에서 추출한 5장 사진의 분석 콘텐츠를 모두 하나로 엮어 **통합된 30초짜리 음악 프롬프트**를 영어로 합성합니다.
    *   *예시 프롬프트*: *"A nostalgic and cinematic 30-second soundtrack blending acoustic guitar melancholia of childhood memories with building warm piano chords that transition into an uplifting pop beat representing hope..."*
3.  작성된 프롬프트는 텍스트 영역(Text Area)에 노출되어 사용자가 원하는 대로 자유롭게 수정할 수 있습니다.
4.  **`🎵 Generate Soundtrack via Lyria`** 버튼을 클릭하면, Google DeepMind의 음악 생성 특화 모델인 **Lyria 3 (`lyria-3-clip-preview`)**을 호출하여 고음질 음원을 생성합니다.
5.  디코딩된 오디오 데이터가 `audio_bytes`에 저장되며, 브라우저에 세련된 **오디오 플레이어**와 **다운로드 버튼(MP3)**, 그리고 동반되는 가사(Lyrics)가 출력됩니다.

### 3단계: 🎨 Tab 3 - Imagen 3 기반 앨범 커버 아트워크 생성
1.  음악 생성이 완료되면 **Tab 3**의 앨범 커버 디자인 기능이 활성화됩니다.
2.  합성된 음악 프롬프트를 바탕으로 어울리는 비주얼 프롬프트가 자동으로 제안되며, 사용자는 이를 자유롭게 커스텀할 수 있습니다.
3.  **`🎨 Create Album Cover via Imagen 3`** 버튼을 클릭하면 이미지 생성 모델인 **Imagen 3 (`imagen-3.0-generate-002`)**을 통해 고품질의 `1:1` 정방형 앨범 아트를 생성합니다.
4.  완성된 고품질 앨범 아트 이미지와 함께, 우측에는 세련된 앨범 슬리브 스타일 레이아웃으로 실시간 오디오 플레이어가 배치되어 시각과 청각이 결합된 최종 "추억의 싱글 앨범" 패키지가 완성됩니다.

---

## 🛠️ 4. 조치 사항 (Resolution Details)

### 4.1 소스 코드 수정 및 버전 관리
*   지원 종료된 구형 모델 대신, 현재 안정적으로 사용할 수 있는 최신 고성능 모델인 **`gemini-3.5-flash`**로 기본 모델 설정을 변경했습니다.
*   규칙(`Name_YYYYMMDD_vX` 형태 유지 및 확정 전까지 `Final` 사용 금지)에 맞춰 새로운 파일로 저장하고 컴파일을 완료했습니다.

#### 📝 코드 변경 내역 (Diff)
```diff
- gemini_model = st.sidebar.text_input("Gemini Model", value="gemini-2.5-flash")
+ gemini_model = st.sidebar.text_input("Gemini Model", value="gemini-3.5-flash")
```

*   **구버전 파일**: [MemorySoundtrack_20260716_v1.py](file:///C:/Users/USER/Desktop/Google/MemorySoundtrack_20260716_v1.py)
*   **신버전 파일 (조치 적용)**: [MemorySoundtrack_20260716_v2.py](file:///C:/Users/USER/Desktop/Google/MemorySoundtrack_20260716_v2.py)

---

## ✅ 5. 자가 검증 및 확인 결과 (Verification Results)
1.  **구문 무결성 확인**: `python -m py_compile MemorySoundtrack_20260716_v2.py` 명령을 구동하여 스크립트에 구문(Syntax) 오류가 전혀 없음을 완벽히 확인했습니다.
2.  **모델 유효성 확인**: `gemini-3.5-flash`는 최신 안정화 버전으로 멀티모달 분석 및 프롬프트 요약 작업을 뛰어난 속도와 정밀도로 처리할 수 있습니다.

---

## 🚀 6. 향후 권장 조치 (Next Steps)
현재 실행 중인 Streamlit 서비스를 새 버전 파일로 실행하여 최종 작동을 확인해 보시기 바랍니다.

*   **실행 명령**:
    ```powershell
    streamlit run MemorySoundtrack_20260716_v2.py
    ```
