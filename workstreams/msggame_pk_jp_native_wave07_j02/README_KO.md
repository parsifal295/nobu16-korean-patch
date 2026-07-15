# Steam JP `msggame` wave07 J02

Steam PK 1.1.7 일본어 경로의 `MSG_PK/JP/msggame.bin` 잔여분 가운데
J02에 배정된 블록 17의 969개 좌표를 모두 한국어로 번역했다.

- 대상 좌표: 969개, 정확 일치
- 고유 원문 해시: 607개
- 불변식이 있는 좌표: 482개, 전부 통과
- 반복 원문: 동일 한국어 강제, 충돌 0개
- 전체 레코드 문맥 검토: 969개 좌표
- 기존 시드 재분절·재번역: 111개 레코드, 246개 좌표
- 공개 오버레이: 원문 없이 좌표·원문 해시·한국어만 포함
- 결합 후 일본어 의미 문자열 잔여: 3,092개
- Steam 설치 파일 쓰기: 없음

옛 SC 기반 해시나 원문은 가져오지 않았다. 공개 엔트리는 Steam 빌더가
요구하는 다섯 필드만 사용하며, 상태와 불변식 증거는 오버레이 상위 메타와
별도 검증 JSON에 둔다. 비공개 문맥 파일은 `tmp` 아래에만 존재한다.

라이브 설치본은 이미 패치되어 있으므로 검증 시 트랜잭션 백업의 정확한
Steam 1.1.7 원본을 `--stock`으로 지정한다.

```powershell
$stock = 'F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msggame.bin'
python -B build_wave07_j02.py build --stock $stock --output-root ..\..\tmp\wave07_j02_candidate
python -B build_wave07_j02.py verify --stock $stock
python -B -m unittest -v test_wave07_j02.py
```
