# Wave 51 — block 13·14 정적 품질 후보

이 작업공간은 Steam PC의 현재 W45 한국어 msggame.bin을 입력으로 하여,
PC 일본어 원문이 명확하고 런타임 토큰이 전혀 없는 항목만 private candidate로
만든다. Steam 게임 파일, Git, 네트워크, 릴리스, 트랜잭션에는 접근하거나 쓰지
않는다.

생성물은 다음 private 경로에만 생긴다.

tmp/pc_dialogue_quality_wave51_static_blocks13_14_v1/candidate

## 포함 범위

총 54 레코드(Base 19, PK 35)만 변경한다.

- 組頭 표기: 구미가시라/조장 → 조두
  - Base 13:83,174,383, 14:32,113,117
  - PK 13:83,174, 14:48,51
  - 13:83,174는 일반 대사 3줄 재배치까지 포함하며 목표 폭은
    456/816/888px이다.
- 制度改新: 제도 개혁 → 제도 개신
  - Base 13:444–447,483,504–505
  - PK 13:362,482–485,491–492,527,548–549,580–585,597
- UI 기능 해금 문맥의 解放: 해방 → 해금
  - Base 13:338,360,445,447,481,505, 14:16
  - PK 13:361,392,483,485,525,549, 14:23
- 분리된 ┝ 아이콘 뒤 목적격: )를 → )을
  - Base 14:34,109
  - PK 14:52,53,151,228,229
  - PK 14:228의 중복 '무장을 선택하면('도 제거한다. 아이콘 literal과
    marker/opaque topology는 그대로 보존한다.
- PK 명백한 오기·조사: 14:9,10,112,233,242
  - 헌책→헌언, "이벤트 합전"가→…이, 병력력→병력,
    예정를→예정을.

모든 포함 레코드는 현재 한국어와 PC 일본어 원문 양쪽에서 02xx와 0143
명령이 없고, marker topology·opaque span·terminator가 일치해야 한다.

## 검증 계약

- W45 Steam 입력의 파일 크기·SHA-256을 고정한다.
- PC 일본어 Base/PK 원문 파일 크기·SHA-256을 고정한다.
- 각 레코드에 현재/PC 일본어/목표 record SHA-256, literal hash,
  marker topology, opaque span, terminator, 런타임 opcode, 0143 명령,
  폰트 line width와 fallback 여부를 audit.v1.json에 기록한다.
- 레코드 증거 전체의 canonical JSON SHA-256과 Base/PK packed·raw 출력
  SHA-256을 빌더에 고정한다.
- 대상은 줄 수를 바꾸지 않고 현재 최대 폭을 늘리지 않으며 fallback glyph를
  허용하지 않는다.

## 의도적으로 제외한 항목

- 시동→시종: 용어 정책 보류.
- Base/PK 13:213: 수동 개행 재배치 보류.
- Base 13:8,14:57, PK 13:8,14:81,14:156–157: 도움말/표/UI 폭 QA 보류.
- PK 13:563,573,590, 14:97–98,221: 문장 재번역 또는 의미 검수 보류.
- block 4 설정 화면 수동 개행 전부: 실게임 설정 UI QA 보류.
- block 13의 02xx/0143 레코드와 PK 14:109: 런타임·형태소 처리 보류.

원문 조건 자체가 상충하는 Base 14:112, PK 14:154–155의 능력치 설명도
번역 후보가 아니라 실게임 조건 검수 대상으로 남긴다.

## 실행

PowerShell에서 저장소 루트 기준으로 실행한다.

~~~powershell
python -B .\workstreams\pc_dialogue_quality_wave51_static_blocks13_14_v1\build_pc_dialogue_quality_wave51_static_blocks13_14_v1.py build
python -B .\workstreams\pc_dialogue_quality_wave51_static_blocks13_14_v1\build_pc_dialogue_quality_wave51_static_blocks13_14_v1.py verify-private
python -B -m unittest .\workstreams\pc_dialogue_quality_wave51_static_blocks13_14_v1\test_pc_dialogue_quality_wave51_static_blocks13_14_v1.py
~~~

derive-pins는 재현 확인용이며, 출력이 빌더의 고정 pin과 다르면 build가
실패한다. 생성물은 검토용이며 Steam 적용 권한을 포함하지 않는다.
