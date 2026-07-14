# v0.1 입력 계약

이 디렉터리에는 미완성 레시피나 빈 자리표시자 파일을 넣지 않는다. 빌더는 다음 네 입력이
모두 완성돼 있을 때만 패키지를 만든다.

- `msgui`: `workstreams/msgui_full/release_p4_vnext/inputs/message/msgui_sc.recipe.json`
- `msgdata`: `workstreams/officer_names/full_v0.1/public/msgdata_sc.recipe.json`
- `msgev`: `workstreams/officer_names/full_v0.1/public/msgev_sc.recipe.json`
- `font-v5`: `workstreams/officer_names/font_v5/public/`

하나라도 없거나 고정 SHA-256·source-free 계약과 다르면 빌더는 출력 폴더를 만들기 전에
실패한다. 기존 3명 probe 레시피와 Font-v4 레시피는 배포 내용이 아니다. 빌더가 각 레시피의
exact size+SHA-256과 target 해시를 모두 고정 검증한 뒤, 설치된 predecessor 상태를 식별하는
마이그레이션 핀으로만 읽는다.

12건 교정과 Font-v5 재생성을 마친 뒤 실제 `final_pins.json`을 만들었다. 이 파일은
`nobu16.officer-names-final-pins.v1` 스키마로 네 리소스 각각의 stock, 최종 target, 최종 recipe
SHA-256과 Font-v5의 두 OFL 라이선스, `metrics/glyphs.jsonl`, 두 `.pixels` 파일의 정확한 상대
경로·크기·SHA-256을 담는다. Font-v5 recipe도 같은 다섯 파일을 정확히 열거해야 하며, 공개
루트에 여섯 번째 파일이 섞이면 빌드를 거부한다. 임시 해시나 빈 문자열을 넣은 자리표시자 파일을
만들지 않는다.
`font_artifacts` 배열 순서는 라이선스 두 파일, metrics, entry 6 pixels, entry 7 pixels의 위 고정
경로 순서여야 한다.

기본 `Development` 모드는 위 최종 핀만 사용하고 `release_eligible=false`로 만든다. 실기 검증이
끝난 뒤 `ReleaseCandidate`로 승격하려면 다음 세 파일이 모두 있어야 한다.

- `candidate_pins.json`: `nobu16.officer-names-candidate-pins.v1`; 아래 두 증명의 크기와 SHA-256
- `four_resource_recipe_e2e.json`: 최종 네 stock/recipe/target 핀의 E2E 재생성 통과 증명
- `runtime_qa.json`: 같은 최종 target 네 해시, `working_directory=game_root`,
  `error_9001_observed=false`인 실기 통과 증명

세 파일은 recipe E2E와 실제 게임 runtime QA 통과 뒤 작성한다. 하나라도 없거나 검토한 크기·
SHA-256과 다르면 `-Mode ReleaseCandidate`는 출력 폴더 생성 전에 반드시 실패한다.

완성 게임 리소스, 공식 원문 전체, EXE/DLL, 메모리 패치 코드는 이 입력 트리와 배포본에
포함하지 않는다.
