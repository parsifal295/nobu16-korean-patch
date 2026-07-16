# Steam JP v0.9 — Switch v2.3 줄바꿈 보정

이 작업은 Steam 1.1.7 일본어 경로의 `MSG/JP/ev_strdata.bin`만 대상으로 한다. 설치된 게임 파일, EXE, 레지스트리, 메모리, DLL을 수정하지 않는다. 공개 산출물은 한국어 오버레이와 검증 메타데이터뿐이며 완성 리소스나 Switch 바이너리를 포함하지 않는다.

## 고정 근거

- Switch v2.2 → v2.3의 같은 리소스를 좌표 단위로 비교한다.
- v2.3 텍스트 멤버가 v2.4와 byte-identical임을 먼저 검증한다.
- 원본 변경 1,329행 중 강제 줄바꿈 제거 좌표는 640행, 토큰은 1,121개다.
- 481행은 줄바꿈 2개, 159행은 1개를 가진다.
- 남은 686행의 전각/문장부호 변화는 별도 fullwidth 작업으로 넘기며, 분류 불가 3행은 이 작업에서 적용하지 않는다.

## 적용 모델

- 625행: Switch v1.3, v2.2, Steam v0.9의 한국어 preimage가 완전히 같은 좌표다.
- 11행: Steam v0.9의 최신 한국어 문구를 보존한 재베이스다. 줄바꿈 벡터와 printf/ESC/control/PUA 벡터가 source 좌표와 같을 때만 허용한다.
- 4행: v0.9에 일본어 잔존 문구가 있어 `manual_korean_residual_translation_and_linebreak_repair`로 분리한다. 일본어 preimage와 Switch 참고 문구는 해시만 남기며, `ko` 출력은 기존 프로젝트 용어 사용처를 확인한 CJK/kana 없는 한국어로만 만든다.

줄바꿈 전용 636행은 각 `CRLF`/`CR`/`LF` 토큰 하나를 ASCII 공백 하나로 바꿀 뿐이며, 전각 문자나 중간점은 바꾸지 않는다. 임의의 newline strip이나 정규화는 금지한다.

## fullwidth 합성 전제

두 작업은 같은 Steam v0.9 preimage에서 출발하므로 단순 순차 적용은 per-cell hash gate에서 실패할 수 있다. 따라서 이 빌더는 외부 fullwidth 메타데이터를 받아 교집합의 경우 다음 순서를 검증하는 합성 API를 제공한다.

`v0.9 → safe ASCII-width punctuation → hard-break-to-ASCII-space`

검증 JSON에는 fullwidth `ev_strdata` operation 수, 교집합 수/ID 해시, 합성 순서, 수동 잔존번역 교집합 여부를 기록한다. 현재 `U+00B7 → U+30FB` 중간점 변화는 Steam JP 폰트 선행 조건이 해결될 때까지 합성에서 제외한다.

safe ASCII-only fullwidth 모델과의 고정 교집합은 28행이며, ID 벡터 SHA-256은 `53705CCD9BCE75A1C5974D250C16AFB4E258A3A8B4F79562A8DF792A26D8D147`이다. 수동 잔존번역 4행과의 교집합은 0이어야 한다.

## 실행

먼저 safe ASCII-only fullwidth 메타데이터가 있어야 한다.

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
& $py -X utf8 -B .\build_steam_jp_switch_v23_linebreak_v1.py generate-public `
  --fullwidth-metadata ..\steam_jp_fullwidth_normalization_v1\public\steam_jp_fullwidth_normalization.v1.json
& $py -X utf8 -B .\build_steam_jp_switch_v23_linebreak_v1.py verify `
  --fullwidth-metadata ..\steam_jp_fullwidth_normalization_v1\public\steam_jp_fullwidth_normalization.v1.json
```

`build`는 후보 리소스를 메모리에서만 만들고 디스크에 게임 파일을 쓰지 않는다. `apply_composed_fullwidth_and_linebreak_to_baseline()`은 외부 safe fullwidth operation model을 인자로 받아 overlap을 합성 검증하는 API이며, fullwidth operation 자체를 이 작업의 공개 오버레이에 복사하지 않는다.
