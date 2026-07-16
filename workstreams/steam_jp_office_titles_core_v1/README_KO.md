# Steam JP 관직 목록 코어 정규화 v1

이 작업 스트림은 이슈 #48의 고신뢰 중앙 관직명만 대상으로 하는 후속 `MSG_PK/JP/msgdata.bin` 오버레이입니다. Steam 일본어 1.1.7의 초기 v0.8 `msgdata.bin` 후보를 기준으로 하며, 설치된 게임 파일이나 SC 경로를 읽거나 수정하지 않습니다.

- display ID 범위: `16399–16463`, `16474–16491`, `16527–16553`, `16568–16586`, `16588–16591`, `16601–16613`
- 범위 안 display 관직은 정확히 146개이며, 대응 독음 ID는 각각 `+271`이다.
- display는 한국 한자음 관직명으로 표기한다. 예: `관백`, `우대신`, `대납언`, `정이대장군`.
- 독음/furigana는 일본식 발음의 한글 표기를 유지한다. 예: `간파쿠`, `우다이진`, `다이나곤`, `세이이다이쇼군`.
- 따라서 주요 쌍은 `16399/16670 → 관백/간파쿠`, `16402/16673 → 우대신/우다이진`, `16404/16675 → 대납언/다이나곤`, `16613/16884 → 정이대장군/세이이다이쇼군`이다.
- 이미 맞는 독음 138개는 그대로 보존한다. 실제 변경은 display 113개와 독음 8개, 합계 121개다. 이미 정규화된 display 33개도 보존한다.

독음 보정 8개는 `16424`, `16425`, `16446`, `16447`, `16585`, `16601`, `16603`, `16613`에만 명시 사전으로 적용한다. 일반 한자 변환이나 일괄 독음 변환은 사용하지 않는다.

`X守`, `X介`, `X守護` 계열의 지리·수령 명칭과 Bakufu ID `16614–16624`는 이 코어 범위 밖으로 명시적으로 제외한다. 별도 Bakufu 레이어에서는 한국 한자음 대신 일본 역사 독음 표기 `간레이`, `단다이` 정책을 사용한다.

공개 JSON에는 프로젝트가 작성한 한글과 행별 SHA-256만 포함하며, 일본어 원문과 완전한 게임 바이너리는 포함하지 않는다. 기준 입력은 아래 해시로 fail-closed 고정한다.

- Steam JP 원본 `msgdata.bin`: `13498FBFFF6D33F0BFB0915B6F365F076FE8E78046EE411BB8478235C86C2C9E`
- initial v0.8 기준 후보: `5469F26B0E75A2214969F2EBA66CD0C850D7BFEC9E3D344ECBC4DBD171110AA6`
- 이 작업 스트림 단독 후보(추적하지 않음): `96CA306D8F1DAC69CB6927A29D98E5D845B89952EFA357947988DE384875183B`

재생성·검증·개인 후보 생성 명령은 다음과 같다.

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\steam_jp_office_titles_core_v1\build_steam_jp_office_titles_core_v1.py verify
& $py -B workstreams\steam_jp_office_titles_core_v1\build_steam_jp_office_titles_core_v1.py build --output-root tmp\steam_jp_office_titles_core_v1_manual_candidate
```

`build`는 새 `tmp` 하위 디렉터리에만 후보와 private manifest를 쓴다. 공개 작업 트리는 바이너리를 추적하지 않으며, 실제 Steam 적용·릴리즈 조합은 상위 통합 작업이 별도로 수행한다.

## 후속 레이어 조합 API

후속 후보 작성기는 `apply_to_packed(stock_root, baseline_packed)`를 사용해 clan·전법 등 선행 `msgdata.bin` 레이어 위에 이 관직 코어를 합성할 수 있다. 이 API는 121개 변경 행뿐 아니라 146쌍 전체(292 좌표)의 원본 JP 해시와 initial v0.8 기준 해시를 모두 검증한다. 따라서 관직 영역을 이미 수정한 입력은 실패하며, 검증된 선행 레이어의 비대상 텍스트는 그대로 유지된다.

반환값은 `(candidate_bytes, metrics)`이며 `metrics["input_baseline"]`, `metrics["candidate"]`, `metrics["translation"]`, `metrics["scope"]`, `metrics["anchors"]`, `metrics["proofs"]`를 제공한다. 이 API도 설치 파일을 쓰지 않는다.
