# Switch v1.3 strdata 직접 이식 작업선

이 작업선은 Switch v1.3 배포본의 `strdata.bin`을 PC 파일로 통째로 복사하지 않는다. 고정된 PC 순정 `MSG/SC/strdata.bin`을 기준으로 블록·슬롯 좌표가 같고 형식 불변식, 대괄호 자리표시자, 한글 존재, 한자·가나 부재 조건을 모두 만족한 값만 좌표 단위로 이식한다.

- 전체 좌표: 32,311
- 자동 안전 판정: 24,525
- 기존 B00 우선 보존: 100
- 기존 공용 UI 우선 보존: 1
- 신규 공개 오버레이: 24,424
- 신규 블록별 수량: 19,020 / 3,081 / 2,203 / 120 / 0
- 수동 검토 제외: 1,431
- 사용 불가 제외: 6,355

후보 파일은 기존 101개 좌표의 번역을 우선 적용한 뒤 신규 24,424개 좌표를 더해 총 24,525개 좌표만 바꾼다. 나머지 7,786개 좌표와 5개 블록 구조는 그대로 보존된다. 후보는 `tmp/` 아래에서만 생성하며 게임 설치 파일, 진행률 JSON, 루트 README는 이 작업선에서 수정하지 않는다.

재현 명령:

```powershell
python workstreams/switch_strdata_v13_direct_transfer/build_switch_strdata_v13_direct_transfer.py
python -m unittest discover -s workstreams/switch_strdata_v13_direct_transfer/tests -v
```

공개 산출물은 한·일·중 원문을 포함하지 않고, 기준 문자열은 UTF-16LE SHA-256으로만 기록한다. 자동 이식 항목도 문맥·표기·화면 폭에 대한 사람 검토와 실제 게임 화면 검증은 별도로 남아 있다.
