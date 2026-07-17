# `msgbre` PC-only 원문 사실 복원 v1

이 작업물은 PC 원문에 명시됐으나 현 한글에서 축약·변질된 인물전 사실을
복원한다. 현재 대상은 `msgbre:720`의 오토모 가문 가독 계승·소린의 모략과
`msgbre:768`의 주가 허락·기모쓰키 명적 복귀·쇼나이의 난 공적·류큐 출병이다.
`msgbre:776`은 기존 generic 교정에 이미 있어 중복 후보로 만들지 않는다.

- 판단 근거는 순정 PC JP와 같은 좌표의 PC EN/SC/TC뿐이다.
- 현재 PC 한글은 수정 전 문자열 hash gate로만 사용한다.
- Switch 한글, 과거 한글 백업은 열거나 참조하지 않는다.
- 후보는 제어문자·printf/runtime token·개행·앞뒤 공백 형식을 바꾸지 않는다.
- 출력은 `tmp/`의 private JSONL과 source-free 검증 계약뿐이며, Steam 게임
  파일·generic builder·커밋·릴리스에는 쓰지 않는다.

실행:

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
& $py -B workstreams\translation_quality_msgbre_restored_facts_v1\build_msgbre_restored_facts_v1.py --write --validate
```
