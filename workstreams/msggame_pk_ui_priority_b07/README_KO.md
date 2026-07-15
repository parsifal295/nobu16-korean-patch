# PK msggame UI 우선 B07

`MSG_PK/SC/msggame.bin`의 미등록 번역 대상 중 실제 플레이에 노출되는 협상, 전투·재해·반란 상태 보고, 내정, 랜드마크, 튜토리얼 및 도움말 300개 좌표를 번역한 소스 비포함 작업 묶음이다. 서사 중심 블록 16·17과 문장 의미가 없는 구두점·배치 기호 슬롯은 포함하지 않았다.

## 범위

- 블록 6: 협상·직접 담판·튜토리얼 28개
- 블록 8: 전투 행동, 재해·반란, 통치·개발, 랜드마크 및 방침 보고 227개
- 블록 13: 튜토리얼·공성전 안내 28개
- 블록 14: 시스템 도움말 17개
- 좌표 SHA-256: `51D54B18F1E4BB88F8123DF0B16DF4630B52D8A04958648F6B11591FAA9178ED`

선정 입력은 B06까지 등록된 33개 오버레이, 11,422개 좌표로 고정된다. B07 자체가 진행률에 등록된 상태와 이후 배치가 추가된 상태에서도 같은 결과를 선택하며, 이후 배치는 소스 비포함·대상 카탈로그 내부·기존 좌표와 비중복 조건을 통과해야 한다.

## 결과물

- `public/msggame_ko_pk_ui_priority_b07_300.v1.json`: 배포용 소스 비포함 오버레이
- `evidence/msggame_pk_ui_priority_b07_evidence.v1.json`: 다국어 구조·너비·불변조건 근거
- `review/msggame_pk_ui_priority_b07_review.v1.json`: 300개 좌표 검토 색인
- `msggame_pk_ui_priority_b07_validation.v1.json`: 단독 및 전체 후보 바이너리 재구성 검증

배포 오버레이 SHA-256은 `6292D829DA64C1E3A0476CF0B3248161E7317AB53D6F0D00B98663F5BAF74BD6`이고, B06까지의 등록분과 합친 11,722개 전체 후보 바이너리 SHA-256은 `D5365A49945582D1F82BF5137CA898EC9EBE270B5F8B90513497E6ADC68E9AD9`이다.

## 재현 및 검증

```powershell
python workstreams/msggame_pk_ui_priority_b07/build_msggame_pk_ui_priority_b07.py
python -m unittest -v workstreams/msggame_pk_ui_priority_b07/test_msggame_pk_ui_priority_b07.py
```

검증은 좌표 보존, 비대상 리터럴 보존, 형식·제어·줄바꿈·PUA 불변조건, 다국어 표시 폭 예산, 원문 중복 번역 일치, 소스 문자 비포함, 자체·미래 등록 필터의 재현성을 확인한다. 공유 진행률, 저장소 README, 설치된 게임 파일은 이 작업 묶음에서 수정하지 않는다.
