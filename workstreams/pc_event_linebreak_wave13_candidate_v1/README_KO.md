# PC Base 이벤트 품질·수동 줄바꿈 Wave13 후보

이 작업공간은 NPC 표기 수정이 적용된 현재 Steam PC Base 이벤트 프로필을 입력으로 삼아 `MSG/JP/ev_strdata.bin`의 정적 이벤트 7개만 후보로 수정한다. Steam 설치본에 쓰는 기능, 적용 스크립트, 릴리즈·오버레이·Git stage/commit 기능은 없다.

Nintendo Switch 한글 자산은 읽거나 번역 참고로 사용하지 않는다. 의미 검토는 pristine Steam-PC 일본어의 해시 고정 좌표만 사용한다.

## 범위

- 리소스: `MSG/JP/ev_strdata.bin` 하나
- 입력 packed SHA-256: `CC77EE4B0587B371A901069FB3F39C2187886C3A3335D9748D275FA2881EB426`
- 수정 좌표: `3280, 4066, 5299, 6960, 7380, 8140, 8350`
- 예상 출력 packed SHA-256: `BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80`
- 변경 파일: 1개, 변경 논리 레코드: 7개

나머지 17,861개 텍스트 셀은 동일해야 하며, 공통 메시지 테이블에서 필수적으로 바뀌는 logical-size와 문자열 offset 이외의 헤더/opaque 바이트도 해시로 보존 확인한다. 각 대상 셀의 ESC 색 태그, printf, 런타임 토큰, PUA, 제어문자, 앞뒤 공백도 동일해야 한다.

## 수동 줄바꿈 계약

모든 후보는 현재 PC JP 이벤트 글꼴의 실제 advance로 계측한다.

- 최대 3행
- 이미 문맥 줄바꿈이 있던 3280, 4066, 5299, 6960, 8140은 줄바꿈 벡터를 그대로 보존
- 7380과 8350만 현재 1행으로 무너진 독백/대비 문장을 3행으로 복원
  - 7380: 위세 → 희망 → 천하인의 결론
  - 8350: 위세 → 희망 → 천하인의 성
- 선택된 기존 수동 줄바꿈 레코드에서 확인한 Base 이벤트 최대폭 1,104px 이하를 모든 대상 행에 적용

후보 행 폭은 다음과 같다.

| ID | 후보 행 폭(px) |
| --- | --- |
| 3280 | 192 / 840 / 792 |
| 4066 | 1008 / 984 / 984 |
| 5299 | 1008 / 696 / 720 |
| 6960 | 720 / 744 |
| 7380 | 912 / 912 / 672 |
| 8140 | 960 / 912 / 216 |
| 8350 | 888 / 912 / 744 |

정적 검증은 실제 게임 QA를 대체하지 않는다. 이 후보에는 Steam 쓰기 기능이 없고, 실게임 이벤트 진입 후의 3행 표시 검수는 별도로 필요하다.

## 실행

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B -m unittest -v workstreams\pc_event_linebreak_wave13_candidate_v1\test_pc_event_linebreak_wave13_candidate_v1.py
& $py -B workstreams\pc_event_linebreak_wave13_candidate_v1\build_pc_event_linebreak_wave13_candidate_v1.py
& $py -B workstreams\pc_event_linebreak_wave13_candidate_v1\build_pc_event_linebreak_wave13_candidate_v1.py --write
```

`--write`는 아래 private 경로에만 후보와 검증 산출물을 쓴다.

- `tmp/pc_event_linebreak_wave13_candidate_v1/candidate-build-1/MSG/JP/ev_strdata.bin`
- `tmp/pc_event_linebreak_wave13_candidate_v1/audit.v1.json`
- `tmp/pc_event_linebreak_wave13_candidate_v1/build_manifest.v1.json`
