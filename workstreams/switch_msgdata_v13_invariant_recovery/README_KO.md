# Switch v1.3 `msgdata` 포맷 복구 배치

이 작업은 Switch 한글 패치 v1.3의 `strdata.bin`을 이용해 PC PK의 `MSG_PK/SC/msgdata.bin`에서 기존 엄격 이식이 제외했던 항목만 다시 검토한다. v1.3의 텍스트 멤버는 v1.1과 바이트 단위로 동일하며, 이미지 변경분과는 독립적이다.

잔여 후보는 148개였다. 이 가운데 ID 18048은 원본 SC가 빈 슬롯이므로 진행률 대상에서 제외했다. ID 22594는 Switch 의미와 SC의 ESC·printf 계약이 서로 다르고, ID 25546은 SC가 `dummy`라 `%d` 인자 계약을 증명할 수 없어 번역으로 세지 않았다. 따라서 자동 안전성이 증명된 결과는 145개다.

선택된 145개의 주 복구 유형은 다음과 같다.

- PUA 구분자 복원 85개
- 줄바꿈·가장자리 공백 복원 43개
- 일본어 중점 제거 8개
- printf 복원 6개
- 퍼센트 리터럴 복원 3개

모든 선택 항목은 기존 여섯 `msgdata` 오버레이의 유효 ID 합집합 20,683개와 겹치지 않고, 원본 SC의 nonblank 대상에 포함된다. printf, ESC, 제어문자, 줄바꿈, PUA, 가장자리 공백, 사용자 정의 대괄호 토큰을 다시 검사한다. CJK 통합한자와 가나는 결과물에 남지 않는다.

전체 진행률에 이 오버레이가 등록되기 전과, 정확한 경로로 한 번 등록된 뒤를 모두 지원한다. 등록 뒤 재생성할 때는 자기 오버레이 145개를 prior claims에서 명시적으로 제외하고 기존 소유자 합집합 20,683개만 비교하므로 결과가 사라지거나 달라지지 않는다.

공개 산출물에는 상용 원문과 완성 게임 리소스가 없다. 빌더는 고정된 원본을 읽고 메모리에서만 재구성 검증하며 설치본, 전체 진행률, 루트 README, 폰트, 게임 파일을 수정하지 않는다.

```powershell
python -B workstreams/switch_msgdata_v13_invariant_recovery/build_switch_msgdata_v13_invariant_recovery.py --out-root workstreams/switch_msgdata_v13_invariant_recovery
python -B -m unittest workstreams.switch_msgdata_v13_invariant_recovery.tests.test_switch_msgdata_v13_invariant_recovery -v
```

출처는 GitHub 사용자 `snake7594`의 [`nobunaga-shinsei-korean-patch`](https://github.com/snake7594/nobunaga-shinsei-korean-patch)와 [`v1.3`](https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/tag/v1.3) 릴리스다.
