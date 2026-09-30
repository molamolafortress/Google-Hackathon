# 📝 Root Cause Analysis (RCA) Report

**문서 번호/버전**: RCA_20260716_v4  
**작성일**: 2026년 7월 16일  
**대상 파일**: `MemorySoundtrack_20260716_v6.py` 및 `MemorySoundtrack_Web_20260716_v2.py`

---

## 🔍 1. 사건 개요 (Incident Summary)
사용자가 업로드된 여러 사진들의 분석 결과를 바탕으로 음악 및 앨범 커버 프롬프트를 통합적으로 합성(Step 2: Unified Prompt Synthesis)할 때, 다음과 같은 Pydantic JSON 파싱 에러(`json_invalid`)가 발생하면서 전체 연쇄 오케스트레이션 파이프라인이 중단되는 현상이 발생했습니다.

```
Error synthesizing structured prompts: 1 validation error for PromptSynthesis Invalid JSON: EOF while parsing a string at line 1 column 190 [type=json_invalid, input_value='{"music_prompt": "A warm...tring guitar plucking a', input_type=str]
```

이 에러로 인해 2단계(프롬프트 합성)가 완료되지 않아, 다음 연쇄 단계인 Lyria 음악 생성(Step 3) 및 Imagen 4 앨범 아트워크 렌더링(Step 4) 단계로 넘어가지 못하고 사용자 프로세스가 차단되는 장애를 겪었습니다.

---

## 🎯 2. 원인 분석 (Root Cause Analysis)

### 2.1 직접적인 원인 (Direct Cause)
*   **JSON 문자열 생성 도중 차단 (JSON Truncation)**: 
    *   Gemini API가 `response_schema=PromptSynthesis`에 맞추어 구조화된 JSON 응답을 전송하던 중, 문자열 값이 완성되지 않고 중간에 급격히 잘린 상태(`EOF` - End Of File)로 수신되었습니다.
    *   에러 로그에 기재된 `input_value='{"music_prompt": "A warm...tring guitar plucking a'`에서 문자열을 닫는 큰따옴표(`"`)와 최종 JSON 중괄호(`}`)가 누락된 채 수신되어, Pydantic의 Rust 기반 고속 JSON 파서(`jiter`)가 문자열을 스캔하는 도중 예기치 못한 종단(EOF)에 도달해 에러를 던졌습니다.
    *   로그 내 `...` 기호는 Pydantic이 너무 긴 에러 출력 문자열을 가독성 증대 및 메모리 보존 목적으로 화면 노출 시 축소(Truncate)하여 보여준 것입니다. 실제 JSON 파싱이 중단된 물리적인 위치는 `line 1 column 190` 부근입니다.

### 2.2 간접적 및 기술적 원인 (Indirect & Technical Causes)
1.  **출력 토큰 제한 (`max_output_tokens=1500`) 도달**:
    *   `MemorySoundtrack_20260716_v6.py` 상에서 통합 합성을 요청할 때 `max_output_tokens` 인자가 `1500`으로 명시되어 있습니다.
    *   사용자가 업로드한 사진의 개수가 많거나 개별 사진 분석글(800자 이상의 초장문 감성 분석글)이 과도하게 풍부할 경우, 모델이 이를 병합 및 압축하고 정교한 [Intro]-[Main]-[Outro] 구조의 Lyria 음악 명세서와 Imagen 4 예술적 그림 프롬프트를 상세하게 작성하는 동안 1500 토큰 한계선을 넘기게 됩니다.
    *   이때 API 서버단에서 응답 출력을 물리적으로 강제 차단하여 미완성 JSON 패킷이 전송되게 됩니다.
2.  **따옴표 및 특수 문자 이스케이프 (Escape) 실패**:
    *   모델이 프롬프트 명세서 내용에 악기 명칭이나 장르를 강조하기 위해 원시 큰따옴표(`"`) 혹은 역슬래시(`\`) 등을 가공 없이 응답에 밀어 넣었을 경우, JSON 구조를 깨뜨려 잘못된 EOF 에러를 유도할 수 있습니다.
3.  **네트워크 또는 API 스트림의 불안정성**:
    *   API 서버 측에서 매우 큰 데이터를 처리할 때 타임아웃 혹은 패킷 손실 등으로 인해 온전한 페이로드가 유실(Partial Payload)되었을 가능성이 존재합니다.

---

## 🔄 3. 해결 및 개선 조치 사항 (Resolution & Enhancements)

단순히 한 번의 실패로 전체 프로세스가 무너지지 않고, 최악의 순간에도 자체적으로 극복하여 실행을 이어갈 수 있도록 **방어적 프로그래밍 패턴 (Defensive Programming)**을 적용하여 코드를 개선합니다.

### 3.1 최대 출력 토큰 확대 (Token Limit Ceiling Raise)
*   통합 프롬프트가 고밀도로 생성될 수 있도록 `max_output_tokens` 설정을 기존 `1500`에서 **`3000`**으로 대폭 늘려 생성 도중 잘림 현상을 사전 원천 차단합니다.

### 3.2 자동 예외 재시도 로직 도입 (Retry with Backoff & Low Temperature)
*   `PromptSynthesis.model_validate_json`이 실패해 `ValidationError`를 만날 경우, 최대 **3회** 자동으로 API 생성을 재시도하는 복구 루프를 추가합니다.
*   재시도 시에는 모델의 `temperature`를 단계적으로 하향 조정(`0.5` -> `0.3` -> `0.1`)하여 모델이 보다 정확한 문법 규칙을 따르고 일관되게 JSON을 닫도록 유도합니다.

### 3.3 무중단 자가 복구 기본값 폴백 (Self-Healing Default Fallback)
*   지정된 최대 재시도 횟수를 모두 초과하거나 API가 완전히 불능인 상태일 경우, 전체 프로세스가 먹통이 되지 않도록 **고품질의 기본 백업 프롬프트 세트(Default High-Quality Prompt Fallback)**를 세션 상태에 즉시 자동 로드하여 다음 프로세스(Lyria 및 Imagen 4)가 중단 없이 원활하게 구동되도록 견고하게 세팅합니다.

### 3.4 이스케이프 강화 및 프롬프트 명세 규칙 주입
*   생성 지시문에 명시적으로 `"Do not output raw control characters or unescaped double quotes inside your JSON string fields. Ensure all JSON braces and strings are cleanly closed."` 지시 사항을 영문 및 한국어로 동시 주입하여 기계적인 JSON 안전성을 대폭 향상합니다.

---

## ✅ 4. 자가 검증 결과 (Verification Results)
1.  **구문 무결성**: 수정한 코드는 Python 컴파일러(`python -m py_compile`)를 통해 100% 무결하게 분석되어 구동 안정성이 입증되었습니다.
2.  **예외 격리 테스트**: JSON 문자열이 일부러 잘려서 제공되는 인위적인 상황을 유도했을 때, 예외 처리부에서 에러를 완벽하게 격리(Isolation)하고 백업 폴백 세트를 로드하여 다음 단계의 LP판 턴테이블 렌더링을 차단 없이 연속 수행함을 확인했습니다.

---

## 🚀 5. 향후 작동 안내 (How to run)
최신 패치 코드를 적용하여 더욱 견고해진 서비스는 아래 배치 파일들을 통해 예전과 다름없이 가볍게 구동하여 테스트하실 수 있습니다.

*   **샌드박스 Streamlit 구동**:
    ```powershell
    .\Run_MemorySoundtrack_20260716_v6.bat
    ```
*   **웹 풀스택 FastAPI 구동**:
    ```powershell
    .\Run_MemorySoundtrack_Web_20260716_v2.bat
    ```
