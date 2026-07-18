# PC 대사 품질 Wave 25 — 정적 일관성

Wave 25는 검증된 Wave 24 private 후보를 유일한 11파일 preimage로 고정하고, PC PK `MSG_PK/JP/msggame.bin`의 리터럴 두 개만 고치는 private 후보 생성 작업이다.

- `(2,283):0` — 전투 대사를 1인칭 결의 표현으로 보정한다.
- `(13,221):0` — 메뉴 경로를 ` > 군사 > 성 역할`로 통일한다.

나머지 7개 정적 일관성 후보군은 화자 문체, 런타임 조각, 또는 구두점 차이라서 이번 일괄 치환에서 제외했다. 각각의 JP group hash, PC 좌표 표본, 보류 사유는 `audit.v1.json`의 `retained_consistency_groups`에 기록한다.

## 입력과 근거

입력은 다음 Wave 24 private 후보의 정확한 11파일 profile뿐이다.

`tmp/pc_event_layout_wave24_v1/candidate`

Wave 24 audit/manifest의 SHA와 크기도 빌더가 고정 검증한다. 문맥 anchor는 PC 원본 JP와 PC EN/SC/TC 파일만 읽는다. Switch 한국어 자료는 입력·근거·대조에 사용하지 않는다.

## 실행

```powershell
python -B .\workstreams\pc_dialogue_quality_wave25_static_consistency_v1\build_pc_dialogue_quality_wave25_static_consistency_v1.py build
python -B .\workstreams\pc_dialogue_quality_wave25_static_consistency_v1\test_pc_dialogue_quality_wave25_static_consistency_v1.py
```

생성 위치는 아래 세 경로로 제한된다.

- `tmp/pc_dialogue_quality_wave25_static_consistency_v1/candidate`
- `tmp/pc_dialogue_quality_wave25_static_consistency_v1/audit.v1.json`
- `tmp/pc_dialogue_quality_wave25_static_consistency_v1/build_manifest.v1.json`

빌더는 두 좌표 외의 레코드 변경, 리터럴 marker/opaque span/종단 토큰 변경, 폰트 폭 초과, Wave24 profile/evidence drift를 모두 실패 처리한다. Steam 게임 파일 적용, Git staging/commit/push, 릴리스 생성은 지원하지 않으며 수행하지 않는다.
