# PC 대사 품질 Wave 23 — 정적 `0143` 제거 후보

이 workstream은 Steam PC용 private 후보만 만든다. 게임 설치본, Steam 적용 경로, Git 상태, 원격 저장소와 릴리즈에는 쓰지 않는다.

## 입력과 출력

- 유일한 입력은 완료된 Wave 22 11파일 후보 `tmp/pc_dialogue_quality_wave22_static_inflection_v1/candidate`다.
- Wave 22의 11파일 SHA-256·크기와 audit/manifest 증적을 모두 고정한다.
- 출력은 `tmp/pc_dialogue_quality_wave23_static_inflection_v1/candidate` 아래에만 생성한다.
- 변경 파일은 `MSG/JP/msggame.bin`, `MSG_PK/JP/msggame.bin` 두 개이며, 20쌍·40레코드만 변경한다.

## 검증 원칙

- 각 대상은 Wave 22 후보의 Base/PK 한국어 preimage, pristine PC JP, PC PK EN/SC/TC의 전체 레코드 SHA-256과 크기로 앵커링한다. Switch 자료는 읽지 않는다.
- 기존 리터럴 마커 수와 topology, 수동 개행 수(최대 3행), 종단 `05 05 05`를 유지한다.
- opaque span에서는 완전한 `01 43 xx xx xx xx` 명령만 제거하고, 나머지 opaque byte는 그대로 보존한다.
- 활성 PC JP 폰트 `RES_JP/res_lang.bin`의 실제 glyph advance만 사용한다. 누락 glyph fallback은 허용하지 않으며, 모든 줄은 912px 이하다.
- `13:107↔13:107`, `13:121↔13:121`은 한국어 리터럴 UTF-16LE payload를 byte-identical로 유지하고 정적 `0143`만 제거한다.

## 품질 재검토 반영

PC JP/EN/SC/TC 문맥을 다시 대조해 다음 다섯 문구를 자연스러운 사극체와 조건·결론 구조로 바로잡았다.

- `15:253↔15:256`: 유언비어·환술, 장치 준비 비용, 더 많은 적 유인의 흐름을 복원했다. 폭 `768/912/888px`.
- `15:261↔15:264`: 자금 → 교서 호소 → 선동 성공의 조건 구조를 복원했다. 폭 `768/408/720px`.
- `15:1626↔15:1656`: 직역인 “손이 빈 자”를 “여유가 있는 자”로 교체했다. 폭 `816/672/840px`.
- `15:1822↔15:1852`: “관계에 유의할 세력”의 부자연스러운 결합을 고쳤다. 폭 `840/648/888px`.
- `15:1862↔15:1892`: “피폐해질 기다리는” 문법 오류를 “피폐해질 때를 기다리는”으로 고쳤다. 폭 `744/648/912px`.

## 실행

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B -m unittest KR_PATCH_WORK\workstreams\pc_dialogue_quality_wave23_static_inflection_v1\test_pc_dialogue_quality_wave23_static_inflection_v1.py
& $py -B KR_PATCH_WORK\workstreams\pc_dialogue_quality_wave23_static_inflection_v1\build_pc_dialogue_quality_wave23_static_inflection_v1.py hash
& $py -B KR_PATCH_WORK\workstreams\pc_dialogue_quality_wave23_static_inflection_v1\build_pc_dialogue_quality_wave23_static_inflection_v1.py build
& $py -B KR_PATCH_WORK\workstreams\pc_dialogue_quality_wave23_static_inflection_v1\build_pc_dialogue_quality_wave23_static_inflection_v1.py verify-private --candidate-root KR_PATCH_WORK\tmp\pc_dialogue_quality_wave23_static_inflection_v1\candidate
```

최종 출력 11파일 프로필은 build manifest와 audit에 고정되며, 실제 게임 QA와 Steam 적용은 이 workstream 범위 밖이다.
