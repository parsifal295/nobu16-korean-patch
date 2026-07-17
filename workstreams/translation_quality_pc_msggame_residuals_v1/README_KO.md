# PC `msggame` 번역 품질 잔존 후보 v1

이 작업은 Steam PC판의 `MSG/JP/msggame.bin` 및 `MSG_PK/JP/msggame.bin`만 대상으로 한다. 스위치 한국어, 과거 한국어 산출물, 범용 한국어 오버레이는 열거나 비교 기준으로 사용하지 않는다.

## 근거 범위

- 기준 원문: 보존한 Steam PC JP `msggame.bin`
- 대조: 현재 Steam PC 한글, PC EN·SC·TC `msggame.bin`
- 보조 앵커: 같은 PC JP 원문이 현재 base `msggame`에 정확히 존재하며, PK 대상이 실질적으로 잘려 있는 경우에만 현재 PC base 한글을 복구안으로 사용한다.

동일 원문의 단순한 문체 차이는 후보가 아니다. 자동 후보는 현재 한글이 `!`, `.`, `→`, 한두 글자 같은 조각으로 잘려 있고 같은 PC JP 원문의 PC base 한글이 완전한 경우에만 생성한다. 수동 후보도 원문과 PC 다국어 문맥상 뜻 오류·누락이 직접 확인되는 항목만 포함한다.

## 산출물

- `private/candidates.v1.jsonl` — 원문·현재문·제안문·PC 다국어 근거를 포함한 로컬 비공개 후보 목록 (`private/`는 Git 무시 경로)
- `private/holds.v1.jsonl` / `private/rejections.v1.jsonl` — 런타임 리터럴 결합 검토로 generic 입력에서 제외한 후보의 로컬 비공개 기록
- `validation.v1.json` — 원문을 노출하지 않는 해시·좌표·서식/런타임 보존 검증 기록
- `tmp/translation_quality_pc_msggame_residuals_v1/pk_msggame_candidates.v1.jsonl` — generic correction builder 입력용 정규화 PASS 페이로드. `pk_msggame`, `b:r:l` 좌표, 현재/제안 한글과 UTF-16LE 해시, 빈 `allowed_format_delta`만 포함하며 JP·EN·SC·TC 원문은 포함하지 않는다.

`build_pc_msggame_residuals_v1.py --write`는 게임 파일을 수정하지 않는다. 실행 전 Steam PC 입력 파일 SHA-256을 고정값과 대조하고, 각 후보에 대해 현재 텍스트 해시, 제안 텍스트 해시, 줄바꿈·줄별 선행/후행 공백·런타임 마커 보존을 확인한다. 또한 같은 PK JP 리터럴이 반복된 경우에도 JP가 정확히 같은 좌표만 골라 PC EN·SC·TC 레코드 문맥을 대조하며, 이 의미 대조가 가능한 항목만 `PASS` 후보로 남긴다. 독립 런타임 결합·opcode 경계 검토에서 HOLD·REJECT로 판정된 항목은 PASS와 generic 입력에서 제외한다. 현재 PASS는 수동 61개와 exact-JP 앵커 36개, 합계 97개다. 그 뒤 private PASS 후보 JSONL을 다시 읽어 정규화 페이로드를 만들며, `validation.v1.json`에는 페이로드의 SHA-256과 건수만 기록한다. Steam·오버레이 파일에는 쓰지 않는다.

이미 만든 private 후보만으로 generic 입력을 다시 만들 때는 `--write-normalized`를 사용한다. 이 경로는 Steam 파일을 읽거나 쓰지 않고, private PASS JSONL과 이 workstream의 source-free validation만 읽어 `tmp` 페이로드와 validation 메타데이터만 갱신한다.

이 작업은 검토 후보 산출물이며, Steam 적용·푸시·릴리스에 대한 권한을 포함하지 않는다.
