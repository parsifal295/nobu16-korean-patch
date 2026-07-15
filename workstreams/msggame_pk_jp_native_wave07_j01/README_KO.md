# Steam JP `msggame` wave07 J01

Steam PK 1.1.7 일본어판 `MSG_PK/JP/msggame.bin`의 미번역 J01 배치를
완역했다. 블록 17의 480개 레코드에서 선택된 970개 좌표 전부를 다루며,
동일 원문 해시를 묶은 613개 한국어 번역을 970개 좌표로 확장한다.

- 선택 좌표: 970/970
- 고유 원문 해시: 613/613
- 반복 원문 해시: 116개, 최대 34회
- 다른 J 배치와 겹치는 좌표: 0
- 불변식 위반·원문 문자 유출·미번역: 각각 0

공개 오버레이의 항목은 좌표, 일본어 UTF-16LE SHA-256, 한국어만 포함한다.
번역에 사용한 상하 레코드 문맥과 타 언어 원문은 비공개 `tmp` 입력에만
있으며 이 작업 스트림에는 들어 있지 않다.

```powershell
python build_wave07_j01.py build
python build_wave07_j01.py verify
python -m unittest -v test_wave07_j01.py
```

