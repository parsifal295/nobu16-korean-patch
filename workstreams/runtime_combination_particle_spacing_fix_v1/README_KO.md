# 런타임 조합형 결과문 조사·공백 수정

화면에서 확인된 `가문가`, 붙어 보이는 성명은 서로 다른 원인입니다.

- 결과문 조사는 `ev_strdata.bin`/`msgev.bin`의 `%s` 템플릿에 고정되어 있었습니다.
- 무장 성명은 `msgdata.bin`의 성씨 조각과 이름 조각을 런타임이 구분자 없이 직접 결합합니다.

Ghidra 정적분석으로 메시지 ID 조회, 치환 컨텍스트 등록, UTF-16 결과 버퍼 생성 경로를 확인했습니다. 런타임은 한국어 조사나 성명 사이 공백을 자동 보정하지 않습니다. 따라서 단순 결과문은 조사에 의존하지 않는 명사형으로 바꾸고, 성씨 조각은 기존 프로젝트 규칙대로 ASCII 공백 하나로 끝나게 합니다.

변경 범위:

- Base 결과문 3행
- PK 결과문 3행
- PK 성씨 조각 2행
- 조건부 결과문은 변경하지 않음

빌드:

```powershell
python workstreams/runtime_combination_particle_spacing_fix_v1/build_runtime_combination_particle_spacing_fix_v1.py `
  --input-root tmp/v090_dialogue_runtime_final_integration_v5/target `
  --output-root tmp/runtime_combination_particle_spacing_fix_v1/candidate
```

빌더는 입력 파일의 packed/raw 해시와 문자열 수, 각 대상 행의 원문 해시, 서식 토큰, 정확한 변경 ID, 최종 출력 해시를 모두 검증합니다. Steam 설치 폴더에는 쓰지 않습니다.
