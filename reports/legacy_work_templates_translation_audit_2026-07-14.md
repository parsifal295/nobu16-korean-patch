# Legacy work-template translation audit — 2026-07-14

## 결론

`data/work_templates`와 `data/work_templates_clean`은 현재 작업 파이프라인의 원본으로 보존할 필요가 없다. 삭제 전에 실제로 재사용할 가치가 있는 이름 번역 초안 63건만 `data/translations/legacy_migrated_names.v0.1.json`으로 옮겼다.

- `work_templates`: 103개 파일, 4,599,163바이트.
- `work_templates_clean`: 4개 파일, 113,723바이트.
- `work_templates_clean`의 CSV 4개/1,678행에는 한글 `translated_ko`가 한 건도 없다.
- 감사 시작 시점의 기존 `data/translations`는 전부 `msgui`/메인 메뉴 범위였다. 현재 `msgui.catalog.p4.jsonl`은 5,100행이다.
- 레거시 `msgui` 한글 49건은 모두 현재 P4 카탈로그에서 같은 EN 원문에 대응하는 한글 번역을 이미 가진다. 레거시 표현이 다른 경우에도 현재 번역을 우선한다.
- 이름 초안 63건은 현재 번역 범위에 없어서 별도 마이그레이션했다: `msgdata` 33건, `msgev` 30건.
- 마이그레이션에서 상용 원문 문자열은 제거했다. EN 리소스명/인코딩/오프셋, 레거시 ID, 한글 목표만 남겼다.

## 마이그레이션 산출물

- 파일: `data/translations/legacy_migrated_names.v0.1.json`
- SHA-256: `082D75F7EDB331DA8F181C4F62B43574D0653A57B2B4D850E1E8E6934FA5E6B5`
- 항목: 63 (`msgdata` 33, `msgev` 30)
- 원본 카탈로그: `master_msgpk_en_catalog.v16_ko_stable_safe.csv`
- 원본 SHA-256: `D2BE233F40242D21B0D4CAE3F39F0CC27C04E27A4D710B616A7FD6873C687201`
- 상태: 모두 `legacy_draft_needs_review`. 미래의 구조화된 SC 메시지 ID와 대조하고 이름 표기/순서를 검토하기 전에는 자동 병합하지 않는다.

`msgev` 레거시 ID 44는 EN 런이 앞에서 잘린 `sai Aisu`이고 번역도 신뢰할 수 없어 제외했다. 나머지 이름은 완전한 성씨 또는 인명 런으로 보이며 초벌 음역 자료로는 재사용 가치가 있다.

## 보존하지 않은 한글 데이터

- `msgui`: 레거시 49건 모두 현재 카탈로그에 이미 존재한다. 예전 자동 번역보다 현재 용어집/문맥 번역을 우선한다.
- `msggame`: v16의 한글 18건은 구조화된 메시지가 아니라 UTF-16 런 조각이다. `Do yo`, `contr`, `sults!`, `S AMBITION`처럼 잘린 조각을 포함하고 오프셋 기반 런 ID라 새 SC 테이블에 안전하게 대응시킬 수 없다.
- `msgbre`: 유일한 한글 1건도 `ga. His son...`으로 시작하는 앞부분 절단 런이다.
- `v15_ko_full_token_fill`과 전체 suggestion map은 자동 추측으로 채운 잘린 토큰이 대량 포함되어 있다. v16이 이를 되돌린 사실도 확인되므로 재사용하지 않는다.
- 이름 전용 v1 파일의 각 7건은 마스터 v16에 포함된 중복 샘플이다.

따라서 마이그레이션 파일을 보존한 뒤 두 레거시 디렉터리 전체를 삭제해도 번역 자산 손실은 없다.

## 파일별 행/항목 수

`Hangul targets`는 CSV의 `translated_ko`에 한글이 있는 행 수다. JSON은 최상위 키/값 맵의 한글 값 수이며 summary JSON은 행 카탈로그가 아니다.

### work_templates

| File | Bytes | Rows/items | Hangul targets |
|---|---:|---:|---:|
| master_msgpk_en_catalog.csv | 12394 | 139 | 0 |
| master_msgpk_en_catalog.pending.csv | 6613 | 73 | 0 |
| master_msgpk_en_catalog.v1.csv | 14226 | 139 | 62 |
| master_msgpk_en_catalog.v10_ko_level_token.csv | 25019 | 224 | 130 |
| master_msgpk_en_catalog.v11_ko_drum_results.csv | 25097 | 224 | 132 |
| master_msgpk_en_catalog.v12_ko_more_tokens.csv | 25208 | 224 | 135 |
| master_msgpk_en_catalog.v13_ko_phrase_tokens.csv | 25657 | 224 | 147 |
| master_msgpk_en_catalog.v14_ko_more_guess_tokens.csv | 26101 | 224 | 159 |
| master_msgpk_en_catalog.v15_ko_full_token_fill.csv | 27592 | 224 | 198 |
| master_msgpk_en_catalog.v16_ko_stable_safe.csv | 25097 | 224 | 132 |
| master_msgpk_en_catalog.v2.csv | 16623 | 139 | 114 |
| master_msgpk_en_catalog.v2.pending.csv | 105 | 0 | 0 |
| master_msgpk_en_catalog.v3.csv | 24414 | 224 | 114 |
| master_msgpk_en_catalog.v3.sample_ko.csv | 24450 | 224 | 115 |
| master_msgpk_en_catalog.v4.ko_v2.csv | 24638 | 224 | 119 |
| master_msgpk_en_catalog.v4_ko_v2_auto.csv | 24638 | 224 | 119 |
| master_msgpk_en_catalog.v5_ko_v3.csv | 24800 | 224 | 124 |
| master_msgpk_en_catalog.v6_ko_v4_draft.csv | 24837 | 224 | 125 |
| master_msgpk_en_catalog.v7_ko_tool_pipeline.csv | 24837 | 224 | 125 |
| master_msgpk_en_catalog.v8_ko_tool_suggestmap.csv | 24837 | 224 | 125 |
| master_msgpk_en_catalog.v9_ko_days_token.csv | 24905 | 224 | 127 |
| msgbre_en_ko_template.csv | 530374 | 6683 | 0 |
| msgdata_en_names_template.le.csv | 1303 | 32 | 0 |
| msgdata_en_names_template.le.summary.json | 3789 | 4 | 0 |
| msgdata_en_names_template.le.v1.csv | 1504 | 32 | 7 |
| msgev_en_ko_template.csv | 1489543 | 18746 | 0 |
| msgev_en_names_template.le.csv | 1521 | 31 | 0 |
| msgev_en_names_template.le.summary.json | 3922 | 4 | 0 |
| msgev_en_names_template.le.v1.csv | 1810 | 31 | 7 |
| msggame_ascii_u16_runs_template.csv | 6949 | 85 | 0 |
| msggame_ascii_u16_runs_template.ko_v2.csv | 7173 | 85 | 5 |
| msggame_ascii_u16_runs_template.ko_v3.csv | 7335 | 85 | 10 |
| msggame_ascii_u16_runs_template.ko_v4_draft.csv | 7372 | 85 | 11 |
| msggame_ascii_u16_runs_template.sample_ko_v1.csv | 6985 | 85 | 1 |
| msggame_ascii_u16_runs_template.sample_v1.csv | 6994 | 85 | 0 |
| msggame_ascii_u16_runs_template.summary.json | 5320 | 4 | 0 |
| msggame_ascii_u16_runs_template.v10_ko_level_token.draft.csv | 7554 | 85 | 16 |
| msggame_ascii_u16_runs_template.v10_ko_level_token.known.csv | 7335 | 85 | 10 |
| msggame_ascii_u16_runs_template.v11_ko_drum_results.draft.csv | 7632 | 85 | 18 |
| msggame_ascii_u16_runs_template.v11_ko_drum_results.known.csv | 7335 | 85 | 10 |
| msggame_ascii_u16_runs_template.v12_ko_more_tokens.draft.csv | 7743 | 85 | 21 |
| msggame_ascii_u16_runs_template.v12_ko_more_tokens.known.csv | 7335 | 85 | 10 |
| msggame_ascii_u16_runs_template.v13_ko_phrase_tokens.draft.csv | 8192 | 85 | 33 |
| msggame_ascii_u16_runs_template.v13_ko_phrase_tokens.known.csv | 7335 | 85 | 10 |
| msggame_ascii_u16_runs_template.v14_ko_more_guess_tokens.draft.csv | 8636 | 85 | 45 |
| msggame_ascii_u16_runs_template.v14_ko_more_guess_tokens.known.csv | 7335 | 85 | 10 |
| msggame_ascii_u16_runs_template.v15_ko_full_token_fill.draft.csv | 10127 | 85 | 84 |
| msggame_ascii_u16_runs_template.v15_ko_full_token_fill.known.csv | 7335 | 85 | 10 |
| msggame_ascii_u16_runs_template.v16_ko_stable_safe.draft.csv | 7632 | 85 | 18 |
| msggame_ascii_u16_runs_template.v16_ko_stable_safe.known.csv | 7335 | 85 | 10 |
| msggame_ascii_u16_runs_template.v7_ko_tool_pipeline.draft.csv | 7372 | 85 | 11 |
| msggame_ascii_u16_runs_template.v7_ko_tool_pipeline.known.csv | 7335 | 85 | 10 |
| msggame_ascii_u16_runs_template.v8_ko_tool_suggestmap.draft.csv | 7372 | 85 | 11 |
| msggame_ascii_u16_runs_template.v8_ko_tool_suggestmap.known.csv | 7335 | 85 | 10 |
| msggame_ascii_u16_runs_template.v9_ko_days_token.draft.csv | 7440 | 85 | 13 |
| msggame_ascii_u16_runs_template.v9_ko_days_token.known.csv | 7335 | 85 | 10 |
| msggame_context_candidates.long_v2.top40.csv | 9113 | 40 | 0 |
| msggame_context_candidates_v1.csv | 3699 | 27 | 0 |
| msggame_context_template.csv | 8640 | 85 | 0 |
| msggame_context_template.long_v2.csv | 12379 | 85 | 0 |
| msggame_context_template.long_v2.summary.json | 8457 | 4 | 0 |
| msggame_context_template.long_v4.csv | 14079 | 85 | 0 |
| msggame_context_template.long_v4.summary.json | 8877 | 4 | 0 |
| msggame_context_template.summary.json | 6363 | 4 | 0 |
| msggame_context_template.v10_ko_level_token.csv | 14079 | 85 | 0 |
| msggame_context_template.v10_ko_level_token.summary.json | 8877 | 4 | 0 |
| msggame_context_template.v11_ko_drum_results.csv | 14079 | 85 | 0 |
| msggame_context_template.v11_ko_drum_results.summary.json | 8877 | 4 | 0 |
| msggame_context_template.v12_ko_more_tokens.csv | 14079 | 85 | 0 |
| msggame_context_template.v12_ko_more_tokens.summary.json | 8877 | 4 | 0 |
| msggame_context_template.v13_ko_phrase_tokens.csv | 14079 | 85 | 0 |
| msggame_context_template.v13_ko_phrase_tokens.summary.json | 8877 | 4 | 0 |
| msggame_context_template.v14_ko_more_guess_tokens.csv | 14079 | 85 | 0 |
| msggame_context_template.v14_ko_more_guess_tokens.summary.json | 8877 | 4 | 0 |
| msggame_context_template.v15_ko_full_token_fill.csv | 14079 | 85 | 0 |
| msggame_context_template.v15_ko_full_token_fill.summary.json | 8877 | 4 | 0 |
| msggame_context_template.v16_ko_stable_safe.csv | 14079 | 85 | 0 |
| msggame_context_template.v16_ko_stable_safe.summary.json | 8877 | 4 | 0 |
| msggame_context_template.v7_ko_tool_pipeline.csv | 14079 | 85 | 0 |
| msggame_context_template.v7_ko_tool_pipeline.summary.json | 8877 | 4 | 0 |
| msggame_context_template.v8_ko_tool_suggestmap.csv | 14079 | 85 | 0 |
| msggame_context_template.v8_ko_tool_suggestmap.summary.json | 8877 | 4 | 0 |
| msggame_context_template.v9_ko_days_token.csv | 14079 | 85 | 0 |
| msggame_context_template.v9_ko_days_token.summary.json | 8877 | 4 | 0 |
| msggame_en_ko_template.csv | 1373685 | 16769 | 0 |
| msggame_review_pack.ko_v3.long_v2.csv | 18408 | 85 | 10 |
| msggame_review_pack.ko_v4_draft.long_v4.csv | 18429 | 85 | 11 |
| msggame_review_pack.v10_ko_level_token.csv | 18500 | 85 | 10 |
| msggame_review_pack.v11_ko_drum_results.csv | 18542 | 85 | 10 |
| msggame_review_pack.v12_ko_more_tokens.csv | 18599 | 85 | 10 |
| msggame_review_pack.v13_ko_phrase_tokens.csv | 18832 | 85 | 10 |
| msggame_review_pack.v14_ko_more_guess_tokens.csv | 19060 | 85 | 10 |
| msggame_review_pack.v15_ko_full_token_fill.csv | 19831 | 85 | 10 |
| msggame_review_pack.v16_ko_stable_safe.csv | 18542 | 85 | 10 |
| msggame_review_pack.v7_ko_tool_pipeline.csv | 18408 | 85 | 10 |
| msggame_review_pack.v8_ko_tool_suggestmap.csv | 18408 | 85 | 10 |
| msggame_review_pack.v9_ko_days_token.csv | 18440 | 85 | 10 |
| msggame_suggestion_map.json | 1622 | 76 | 75 |
| msggame_suggestion_map.safe.json | 243 | 10 | 10 |
| msgui_en_ko_template.be.csv | 2065 | 52 | 0 |
| msgui_en_ko_template.be.sample_ko.csv | 2129 | 52 | 3 |
| msgui_en_ko_template.be.summary.json | 3814 | 4 | 0 |
| msgui_en_ko_template.be.v1.csv | 3407 | 52 | 48 |

### work_templates_clean

| File | Bytes | Rows/items | Hangul targets |
|---|---:|---:|---:|
| msgbre_en_ko_template.clean.csv | 19850 | 297 | 0 |
| msgev_en_ko_template.clean.csv | 42093 | 630 | 0 |
| msggame_en_ko_template.clean.csv | 46436 | 681 | 0 |
| msgpk_en_utf16a0_ascii_template.csv | 5344 | 70 | 0 |

## 검증 메모

- `legacy_migrated_names.v0.1.json`은 JSON 파싱 성공.
- 선언 항목 수 63 = 실제 항목 수 63.
- `msgdata` 33 + `msgev` 30 = 63.
- 각 엔트리에는 상용 EN 원문 필드가 없다.
- 이 감사에서는 게임 파일을 수정하거나 실행하지 않았고, 레거시 디렉터리를 삭제하지 않았다.
