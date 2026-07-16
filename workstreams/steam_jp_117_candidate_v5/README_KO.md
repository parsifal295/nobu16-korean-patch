# Steam PK 1.1.7 일본어 경로 v0.8.0 정식 배포 검증 기록

이 작업물은 Steam build `18823764` / PK `1.1.7`의 일본어(`JP`) 경로용 파일 전용 한글 패치 v0.8.0의 검증 기록입니다. SC 경로, 메모리 패치, DLL 주입, 후킹, EXE·레지스트리 변경을 사용하지 않습니다.

v5는 기존 12파일 후보에 실제 PK 실행 시 함께 읽히는 기본판 대사 파일 두 개를 추가한 **exact-14** 조합입니다.

- `MSG/JP/msggame.bin`: Switch v1.3 대조가 가능한 22,924개 레코드. 지도 튜토리얼 대사도 이 파일에 포함됩니다.
- `MSG/JP/ev_strdata.bin`: Switch v1.3 대조가 가능한 13,045개 레코드.

## exact-14 대상

- `MSG/JP/ev_strdata.bin`
- `MSG/JP/msggame.bin`
- `MSG/JP/strdata.bin`
- `MSG_PK/JP/msgbre.bin`
- `MSG_PK/JP/msgdata.bin`
- `MSG_PK/JP/msgev.bin`
- `MSG_PK/JP/msggame.bin`
- `MSG_PK/JP/msgire.bin`
- `MSG_PK/JP/msgstf.bin`
- `MSG_PK/JP/msgui.bin`
- `RES_JP/res_lang.bin`
- `RES_JP_PK/res_lang_pk.bin`
- `RES_JP_PK_PORT/res_lang_pk_port1.bin`
- `RES_JP_PK_PORT/res_lang_pk_port2.bin`

## 검증 상태

- 후보 단위 테스트: 9/9 통과
- 읽기 전용 조합 검증: 통과
- `verification.v5.json` SHA-256: `BF0CC287FC2E2FBADB0A3CB29055C2BF7F6BAC10CDF9C686514CB64B5A4BC2E3`
- 14파일 ZIP: `NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.8.0.zip`
- ZIP SHA-256: `8167B09DE5DC56C1F195AF0A913336F552D189B0DB320C2A4F5EC863BBC58D08`

Steam 설치본에는 게임 종료 상태에서 exact-14 파일 전용 트랜잭션을 적용했고 14개 복원 백업을 확인했습니다. 사용자가 실제 화면에서 한글 출력을 확인했으며, v0.8.0은 이 exact-14 벡터로 정식 배포합니다.

## 재검증

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B -m unittest workstreams\steam_jp_117_candidate_v5\test_steam_jp_117_candidate_v5.py -q
& $py -B workstreams\steam_jp_117_candidate_v5\build_steam_jp_117_candidate_v5.py verify --port-stock-root <검증용_원본_PORT_폴더>
```

공개 저장소에는 원본 게임 파일이나 Switch 배포 원문을 넣지 않습니다. 저장소에는 source-free 오버레이, 계약, 검증 결과만 둡니다.
