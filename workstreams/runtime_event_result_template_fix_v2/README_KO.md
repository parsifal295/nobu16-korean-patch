# 이벤트 결과 문구 동적 조사 교정 v2

이벤트 일람의 결과 상세·요약 문구는 런타임에서 이름과 가문명을 템플릿에 그대로
대입합니다. 완성된 이름의 받침을 검사해 한국어 조사를 고르는 기능은 없습니다.
따라서 `가문가`, `성로`, `신겐로`처럼 동적 값에 고정 조사가 붙어 깨지는 문장은
명사형 또는 레이블형 결과 문구로 교정했습니다.

변경 범위:

- Base `MSG/JP/ev_strdata.bin` 28행
- PK `MSG_PK/JP/msgev.bin` 28행
- 결과 상세용과 결과 목록 요약용 중복 행을 함께 교정
- 변수 순서, 변수 형식, 제어 코드, 행 구분은 보존

주요 교정 유형:

- 세력 탄생·멸망
- 본거 이전
- 동맹·정전·종속
- 무장 소속·조건부 소속 변경
- 조건부 사망·행방불명
- 당주 승계·해임
- 조건부 제압
- 개명
- 결과 목록의 세력 탄생·동맹·관계 해소 안내

빌드:

```powershell
python workstreams/runtime_event_result_template_fix_v2/build_runtime_event_result_template_fix_v2.py `
  --input-root tmp/v090_dialogue_runtime_final_integration_v6/target `
  --output-root tmp/runtime_event_result_template_fix_v2/candidate
```

빌더는 입력·출력 packed/raw 해시, 문자열 수, 원문 행 해시, 변수 토큰 순서,
정확한 변경 ID 집합을 검증하며 Steam 설치 폴더에는 쓰지 않습니다.
