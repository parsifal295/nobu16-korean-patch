# 장수명 `msgdata` 성·이름 동기화 보고서

## 결과

full `msgev` 장수 2,207명의 한국어 이름은 모두 유지된다. 이 가운데 SC/JP/EN 세 언어의
성·이름 조각이 정확히 일치하는 2,152명을 `msgdata` 분리 슬롯에 동기화했다.

| 항목 | 수량 |
|---|---:|
| full `msgev` 번역 | 2,207명 |
| `msgdata` exact split 확정 | 2,152명 |
| `msgdata` split만 보수적 제외 | 55명 |
| 성 슬롯 | 1,051개 |
| 이름 슬롯 | 2,781개 |
| 공개 오버레이 전체 슬롯 | 3,832개 |

55명은 full-name 번역에서 빠진 인원이 아니다. full `msgev`에는 모두 한국어 이름이 있고,
분리 슬롯을 확정할 수 없는 경우에만 `msgdata` 적용을 생략했다. 제외 사유는 다음과 같다.

| 제외 사유 | 인원 |
|---|---:|
| 단일명·칭호 등 두 조각이 아닌 이름 | 39명 |
| SC/JP/EN exact component pair 없음 | 9명 |
| 같은 component에 서로 다른 한국어 표기 충돌 | 6명 |
| 성·이름이 같은 `msgdata` ID를 가리킴 | 1명 |

## 안전한 매칭 기준

- full-name의 SC/JP 접두·접미와 EN 정상/역순 조합을 모두 검사한다.
- 동일한 `msgdata` 행의 SC/JP/EN 세 값이 전부 일치할 때만 component로 채택한다.
- 영문 독음만 같은 별개 성은 일괄 치환하지 않는다.
- 복수 exact pair, component 번역 충돌, 성·이름 ID 겹침은 적용하지 않고 비공개 보고서로
  분리한다.
- 성에는 후행 ASCII 공백 하나와 `allow_edge_whitespace_change=true`를 사용한다.
- 이름에는 공백을 넣지 않는다.

유명 장수 12명과 가장 긴 한국어 이름 3명, 총 15명을 고정 회귀 대상으로 검사했다.
모두 full SC/JP/EN 재조합, 성·이름 ID, 한국어 표기와 공백 규칙을 통과했다.

## 공개 산출물

- `data/public/msgdata_ko_officer_names_0000_2399.v0.1.json`
- `workstreams/officer_names/full_v0.1/public/msgdata.build-manifest.json`
- `workstreams/officer_names/full_v0.1/public/msgdata_sc.recipe.json`

공개 오버레이 SHA-256:
`D4133D989D103730DEF9DB9ED92D67D70E6C557C564A55ACEAC4702CF5A0618F`

공개 manifest SHA-256:
`DFC3368FA71C01E65703664A7BA0F5A80417C89E5D34A919E504CC4A719C27E8`

공개 recipe SHA-256:
`798F337F7AB0509829181CD4C45FBBD913A1379E15BD37EA4379E78CFEA0154C`

격리 빌드 target SHA-256:
`08AA813CD6459E17F7E94DF3C405AE1B228B171D8ED1B43E836A8C1E2540CE0B`

manifest와 recipe는 원자적으로 각 파일을 교체해 내보냈다. 기존 `msgev` manifest와 recipe는
각각 아래 해시를 유지해 두 리소스가 같은 공개 디렉터리에 병존한다.

- `msgev.build-manifest.json`:
  `6233C63EAAFBFFA69FCFE96C026808EF5063CD7CECD106CD3A4C3DAC1BAE4F63`
- `msgev_sc.recipe.json`:
  `CA87C0E8077B87D68AA474E24278EAE36213901DC45740ABA1637D2CDEF38C3A`

## 배포 경계와 검증

- 공개 overlay·manifest·recipe의 CJK 통합한자 수: 0개
- 상업 원문 필드 및 완성 게임 리소스 포함: 없음
- 공개 recipe로 격리 stock을 재생한 결과: tmp build target과 바이트 동일
- 독립 build A/B: target·manifest·recipe 모두 바이트 동일
- stock 백업과 SC/EN/JP 입력: 해시 불변
- 설치된 `MSG_PK/SC/msgdata.bin`: 읽기·쓰기 대상에서 제외
- 전체 단위 테스트: 43/43 통과

재현 명령은 다음과 같다.

```powershell
python tools/generate_officer_name_components.py `
  --full-catalog data/translations/msgev_officer_names_0000_2399.v0.1.json `
  --full-report tmp/officer_names_full/generation_report.v0.1.json `
  --msgdata-sc backups/officer_name_probe_v0_1/msgdata.SC.stock.bin `
  --msgdata-en ../MSG_PK/EN/msgdata.bin `
  --msgdata-jp ../MSG_PK/JP/msgdata.bin `
  --private-output data/translations/msgdata_officer_names_0000_2399.v0.1.json `
  --public-output data/public/msgdata_ko_officer_names_0000_2399.v0.1.json `
  --report-output tmp/officer_name_components/generation_report.v0.1.json `
  --verification-root tmp/officer_name_components/verification `
  --public-build-output-root workstreams/officer_names/full_v0.1/public
```
