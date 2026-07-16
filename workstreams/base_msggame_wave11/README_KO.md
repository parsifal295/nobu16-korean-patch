# 본편 지도·조언 대사 Wave 11

이 작업선은 Steam 1.1.7 일본어 경로의 기본판 `MSG/JP/msggame.bin`에서, 앞선 Switch v1.3 엄격 이식 뒤에 남은 332개를 다음 후보용으로 정리한다. 현재 Steam 설치본, v5 후보, 릴리스 압축 파일, 루트 README는 바꾸지 않는다.

## 범위

| 구분 | 수 | 처리 |
| --- | ---: | --- |
| 앞선 엄격 이식 | 22,924 | 이미 반영된 기준선 |
| Wave 11 안전 계약 | 270 | 다음 후보에 이식 가능 |
| 용어 검토 보류 | 3 | 한자 병기 없는 한국어 용어를 확정한 뒤 수동 이식 |
| 비문자 형식 토큰 | 59 | 번역 행으로 세지 않고 그대로 유지 |

안전 계약 270개는 다음 세 범주뿐이다.

- Switch v1.3 결과를 그대로 쓰는 행: 207개
- 원문의 앞·뒤 공백만 맞추는 행: 62개
- 퍼센트 기호 하나만 전각으로 맞추는 행: 1개

각 행은 좌표, 원문 UTF-16LE 해시, 한국어 UTF-16LE 해시, 제어문자·줄바꿈·자리표시자 불변식으로 고정한다. 공개 오버레이에는 상용 원문이나 완성 리소스를 넣지 않는다. 가운데점은 한국어 목록 구분 기호로 허용하지만 한자·가나 문자는 거부한다.

## 입력 기준

검증은 라이브 Steam 폴더가 아니라 v0.8.0 적용 전 백업의 기본판 파일을 쓴다.

`F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.8.0/originals`

이로써 화면 검증용으로 이미 적용된 Steam 파일을 원본 입력으로 잘못 쓰지 않는다. Switch v1.3 고정 자산과 좌표가 맞는 270개만 사용하며, 좌표가 달라진 다른 Switch 배포판은 자동 이식 근거로 쓰지 않는다.

## 산출물

- `public/msggame_ko_base_jp_wave11_safe_270.v1.json` — 바로 이식할 한국어 오버레이
- `public/msggame_ko_base_jp_wave11_deferred_62.v1.json` — 용어 검토 3개와 비문자 토큰 59개의 보류 근거
- `validation.v1.json` — 메모리 후보 A/B 재현과 구조 보존 결과

원본 기준선 위에서 270개를 추가 조립한 메모리 후보는 다음과 같다.

- 변경 행: 23,194개
- 압축 SHA-256: `E54D7AB55CB981B7973FBF8657A276520EBFA881D3439BE94A2D14086B293177`
- 원시 데이터 SHA-256: `183F7867817FBDAAE8E8B1DE547AEAC9B80C6A818604DD26FBF57BABD2FC10E2`

위 후보는 검증 중 메모리에만 존재하며 저장하거나 배포하지 않는다.

## 검증

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\base_msggame_wave11\build_base_msggame_wave11.py verify
& $py -B -m unittest workstreams\base_msggame_wave11\test_base_msggame_wave11.py -q
```

다른 정품 원본 위치를 사용할 때만 `--stock-root`와 `--switch-zip`을 함께 명시한다. `generate`는 이 작업선의 source-free JSON만 다시 만들며 Steam 파일을 쓰지 않는다.
