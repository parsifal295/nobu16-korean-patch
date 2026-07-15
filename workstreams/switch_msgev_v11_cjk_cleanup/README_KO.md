# Switch v1.1 PK `msgev` CJK·kana 정리 20개

이 작업은 기존 Switch v1.1 엄격 이식본이 한자 또는 kana가 남아 있어 제외한
PK `MSG_PK/SC/msgev.bin` 항목 20개를, 검토한 한글 전용 문장으로 보완한다.
완전 리소스나 원문은 만들지 않으며, 게임 설치 파일도 변경하지 않는다.

## 입력과 범위

- 선행 overlay: `workstreams/switch_msgev_v11/public/msgev_ko_switch_v11_ported_7025.v1.json`
- Switch 입력: `tmp/third_party_switch_v11/NobunagaShinsei_KoreanPatch_v1.1.zip`
- PC 비교 입력: `MSG/JP/ev_strdata.bin`, `MSG_PK/JP/msgev.bin`, 보존된 PK SC stock
- 대상: PK `MSG_PK/SC/msgev.bin`의 20개 ID만

선행 7,025개와 기존 공개 PK `msgev` 소유 ID 5,469개를 합친 12,494개와의
중복은 실패로 처리한다.

## 실패-폐쇄형 게이트

각 후보는 다음을 모두 통과해야 한다.

1. 선행 이식본에서 제외된 정확한 20개 ID여야 한다.
2. 같은 숫자 ID에서 PC 기본 JP와 PK JP가 바이트 단위로 같아야 한다.
3. 동일 JP 원문에 연결되는 의미 있는 Switch 한국어 값이 정확히 하나여야 한다.
4. 검토한 정리 문장은 한글을 포함하고 한자·kana를 포함하지 않아야 한다.
5. PK SC의 printf, ESC 순서, 일반 제어문자, 줄바꿈, private-use 문자,
   앞뒤 공백, 대괄호 토큰이 모두 보존되어야 한다.
6. 모든 공개 산출물은 원문이 없는지 검사하고, 서로 격리한 두 번의 build와
   최종 build가 바이트 단위로 같아야 한다.

## 산출물

- `public/msgev_ko_switch_v11_cjk_kana_cleanup_20.v1.json`: 배포 가능한 20개 overlay
- `evidence/switch_v11_cjk_kana_cleanup_alignment.v1.json`: 해시 기반 정렬 근거
- `review/switch_v11_cjk_kana_cleanup_review.v1.json`: PC PK 화면 검토 대기 표식
- `validation.v1.json`: 재현성·안전성·대상 리소스 검증

## 재생성 및 검증

```powershell
python -B workstreams/switch_msgev_v11_cjk_cleanup/build_switch_msgev_v11_cjk_cleanup.py
python -B -m unittest workstreams.switch_msgev_v11_cjk_cleanup.tests.test_switch_msgev_v11_cjk_cleanup -v
```

이 workstream은 설치·복원·배포 작업을 수행하지 않는다. 상위 PK payload 조립기가
이 overlay를 명시적으로 채택할 때에만 최종 파일에 반영할 수 있다.
