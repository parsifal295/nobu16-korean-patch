# Switch v1.1 `msggame` → PK 이식

이 작업 스트림은 Switch 한국어 패치의 **문자열 대응 관계만** 검증해 PK판 간체중문 `msggame`용 한국어 오버레이를 만듭니다. 게임 EXE, DLL, 레지스트리, 메모리, 설치된 게임 파일은 건드리지 않습니다.

## 출처와 입력 고정값

- 제작자: `snake7594`
- 저장소: <https://github.com/snake7594/nobunaga-shinsei-korean-patch>
- 릴리스: [`v1.1`](https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/tag/v1.1)
- 검증 자산: [`NobunagaShinsei_KoreanPatch_v1.1.zip`](https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/download/v1.1/NobunagaShinsei_KoreanPatch_v1.1.zip)
- ZIP SHA-256: `931E7C5BDECD724E44987D722E71A12161448A1A583DFFB4A569A4FA58EC46F6`
- ZIP 내부 입력 경로: `NobunagaShinsei_KR/romfs/MSG/JP/msggame.bin`

빌더는 ZIP 내부 멤버를 메모리에서만 읽습니다. 압축 해제된 길이는 `0x16DD42`이고 마지막 블록 직후에만 정렬용 널 2바이트가 부족하므로, 파싱할 때만 메모리에 `00 00`을 붙입니다. ZIP, 내부 멤버, 원본 게임 파일을 추출하거나 기록하지 않습니다.

## 선택 규칙과 결과

기본판 JP 문자열 해시에서 유일한 Switch 한국어 값을 만든 뒤, PK JP 문자열 해시를 전역 조회합니다. 좌표가 같은 경우는 직접 대응으로 표기하고, 그 밖에는 동일 JP 해시를 근거로 이식합니다. PK SC 대상에서 표시 가능한 문자열인지와 서식·공백·제어문자·줄바꿈·PUA 불변식도 확인합니다.

| 항목 | 값 |
| --- | ---: |
| 기존 PK `msggame` 오버레이 좌표 합집합 | 3,300 |
| 전역 엄격 후보 | 8,375 |
| CJK/Kana 필터 제외 | 154 |
| 기존 오버레이와 중복 | 2,204 |
| 최종 이식 | **6,018** |
| 동일 좌표 직접 대응 | 395 |
| 전역 JP 해시 이식 | 5,623 |

선택된 한국어에는 CJK 통합 한자(`U+3400–U+4DBF`, `U+4E00–U+9FFF`, `U+F900–U+FAFF`) 및 Kana(`U+3040–U+30FF`, `U+31F0–U+31FF`)가 없습니다. 기존 카탈로그 좌표와 겹치는 값도 모두 제외합니다.

## 공개 산출물

- `public/msggame_ko_switch_v11_exact_source_hash.v0.1.json` — PK `MSG_PK/SC/msggame.bin`용 6,018건 오버레이
- `evidence/switch_v11_pk_msggame_alignment_evidence.v0.1.json` — 좌표·해시 대응 증거
- `review/switch_v11_pk_msggame_review_index.v0.1.json` — 화면 검토용 인덱스와 이식 방식
- `switch_v11_pk_msggame_validation.v0.1.json` — 입력 고정값, 재구성 결과, 안전성 검증

위 파일에는 Switch ZIP, 압축 해제 원문, 원본 게임 바이너리가 포함되지 않습니다. 공개 JSON은 CJK/Kana 스캔도 통과해야 합니다.

## 재현과 검증

작업 루트에서 다음을 실행합니다.

```powershell
python -B workstreams/switch_msggame_v11/build_switch_msggame_v11.py --out-root workstreams/switch_msggame_v11
python -B -m unittest workstreams.switch_msggame_v11.tests.test_switch_msggame_v11 -v
```

검증은 두 개의 격리 출력이 바이트 단위로 같은지, PK SC에서만 오프라인 재구성을 했을 때 목표 SHA-256이 일치하는지, 원본 입력이 전후로 바뀌지 않는지를 확인합니다. 화면 검토는 긴 줄바꿈, 서식 토큰, 다중 리터럴 레코드를 우선 대상으로 삼습니다.
