# PK 다케다 노부시게·나베시마 나오시게/히코쓰루 이벤트 전수 감사

범위는 PK `MSG_PK/JP/msgev.bin` ID `3527–3564`의 다케다 노부시게 가훈 장면과
나베시마 나오시게·히코쓰루 장면, 총 38행이다. 한국어 입력은 처음에는 Wave 100
후보를 지정했지만, 작업 중 생성된 Wave 101 후보가 바로 앞의 비중첩 범위
`3489–3526`만 바꾼 것을 확인했다. 따라서 이 감사는 Wave 101의
`tmp/pc_event_kanto_quality_wave101_v1/candidate-final/MSG_PK/JP/msgev.bin`를
strict 입력으로 사용하고, ID `3527–3564`가 Wave 100과 바이트상 문자열까지 같은지
검증한다.

순정 Steam PC JP와 설치된 PC EN/SC/TC는 뜻·고유명사·보호 구조 대조에만 썼다.
JP의 원래 줄바꿈은 한국어 레이아웃 권위로 쓰지 않았다.

## 감사 결과

- 38행 전부를 직접 대조했다.
- 20행은 `static_high_confidence` 제안이다.
  - 의미·문법 복원: `3529`, `3530`, `3539–3542`, `3548`, `3550`, `3551`,
    `3554`, `3561`, `3563`, `3564`
  - 한국어 의미 단위 개행/공백 정리: `3532`, `3533`, `3536`, `3546`, `3547`,
    `3555`, `3559`
- 나머지 18행은 원문과 PC 다국어를 대조한 뒤 현재 문안과 문맥 개행을 유지한다.
- `3548`의 `[bm1251]`은 strict 이름표 전체 이름 예약 폭으로만 측정했다.
  런타임 접두사 렌더링은 추측하지 않았고 `runtime_proven=false`다.
- 보류할 런타임/별도 UI 렌더링 문제는 이 범위에서 확인되지 않았다.

대표적인 복원은 다음과 같다.

- `3550`: `내조로 받친` 오기와 축약된 류조지 가문의 전략 참모·사랑하는 아내라는
  정보를 `내조의 공으로 뒷받침`하는 문장으로 복원한다.
- `3551`, `3563`, `3564`: `見初めた`, `機転を利かせて`, `率先して`,
  `戦国時代としては` 등 기존 문안에서 빠진 인연의 시작·재치·솔선·전국시대 맥락을
  되살린다. 문장을 축약하거나 삭제하지 않는다.
- `3536`, `3546`, `3547`, `3555`, `3559`: 단어 중간처럼 보이던 수동 줄바꿈과
  다음 줄 선행 공백만 한국어 의미 단위로 재배치한다.

## Static Patch 007 레이아웃 기준

- PK 이벤트 대사 글자 크기 30px, 줄 간격 8, 유효 폭 912px, 최대 4줄
- 원본 G1N 폭: 전각 48px / 반각 24px
- `effective_width_px = ceil(raw_g1n_width_px * 30 / 48)`
- 통과 상한: 원본 G1N 1440px / 실효 912px

공개 JSON의 모든 행에는 현재·제안 표시 문자열, 원본 G1N 폭, 환산 실효 폭,
전각/반각 문자 수, 줄 수, 912px 초과 여부를 기록한다. 제안 행에는 런타임 이름
예약 폭도 함께 기록한다. 태그 내부에는 줄바꿈을 넣지 않았고 제어 코드·색상 태그·
런타임 토큰·종료 구조를 보존한다.

## 실행

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_event_takeda_hikotsuru_audit_v1\build_pc_event_takeda_hikotsuru_audit_v1.py build
& $py -B workstreams\pc_event_takeda_hikotsuru_audit_v1\build_pc_event_takeda_hikotsuru_audit_v1.py verify
& $py -B -m unittest -v workstreams\pc_event_takeda_hikotsuru_audit_v1\test_pc_event_takeda_hikotsuru_audit_v1.py
```

이 workstream은 `public/`의 읽기 전용 감사 보고서와 검증 기록만 만든다. 후보
바이너리, Steam 적용, Git 조작, 푸시, 릴리즈, 네트워크 작업은 수행하지 않는다.
