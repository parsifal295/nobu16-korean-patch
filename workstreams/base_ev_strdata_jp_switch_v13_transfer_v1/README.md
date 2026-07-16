# 기본판 이벤트 대사: Steam JP ← Switch v1.3 안전 이식

이 작업 스트림은 Steam PK 1.1.7의 `MSG/JP/ev_strdata.bin`만 대상으로 한다. 설치된 게임 파일, 현재 후보본, 배포 ZIP에는 쓰지 않는다.

## 결과

- Switch v1.3에서 한글이 포함된 슬롯: 13,090개
- 원문 문자(한자·가나)가 섞여 제외된 슬롯: 45개
- 제어문자·줄바꿈·자리표시자·Steam 원문 해시가 모두 일치해 이식 가능한 슬롯: 13,045개
- 재구축 후보 SHA-256: `AD1A442C3588E791DB442548C2B7878ABB4D53A686C591A94AB7F4FAB719A886`

공개 오버레이에는 한국어 결과, 슬롯 ID, Steam 원문 UTF-16LE 해시만 들어 있다. 상용 원문·완전한 게임 리소스·Switch 바이너리는 포함하지 않는다.

## 입력 고정값

- Steam 1.1.7 JP 원본: packed `EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB`
- Switch v1.3 ZIP: `F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4`
- Switch 대상 항목: `A5D70580790330EF845EC73FDB8D6ACC89EBAD8D026DFE1B1D873C50B43CAD5D`

입력 해시, 문자열 수(17,868), 각 슬롯의 원문 해시, 제어 시퀀스, 줄바꿈, 자리표시자를 모두 실패-폐쇄 방식으로 검사한다.

## 생성과 검증

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B .\build_base_ev_strdata_jp_switch_v13_transfer_v1.py emit-public
& $py -B .\build_base_ev_strdata_jp_switch_v13_transfer_v1.py build --output-root ..\..\tmp\base_ev_strdata_jp_switch_v13_transfer_v1_probe
& $py -B .\build_base_ev_strdata_jp_switch_v13_transfer_v1.py verify --candidate ..\..\tmp\base_ev_strdata_jp_switch_v13_transfer_v1_probe\candidate\MSG\JP\ev_strdata.bin
& $py -B .\test_base_ev_strdata_jp_switch_v13_transfer_v1.py
```

`build`는 저장소의 `tmp` 하위에만 후보 파일을 만든다. 설치 경로로 복사하는 동작은 이 스트림에 없다.

## 화면 검증 상태

이 파일이 PK 실행 중 어떤 이벤트 화면에서 실제 로드되는지는 아직 화면으로 확인하지 않았다. 따라서 이 작업물은 **통합 후보**이며, 실제 이벤트 화면에서 한국어 표시와 저장/재시작 안정성을 확인하기 전에는 배포 후보에 포함하지 않는다.

지도에서 확인된 튜토리얼 일본어 대사는 이 파일이 아니라 기본판 `MSG/JP/msggame.bin`의 별도 누락 경로다. 그 화면 문제는 이 이벤트 대사 오버레이만으로 해결되지 않는다.
