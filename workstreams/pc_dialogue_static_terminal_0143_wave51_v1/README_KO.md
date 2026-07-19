# PC 대사 정적 terminal 0143 Wave 51

W45 Steam PC 대사 입력에서 승인된 40 physical record만 private 후보로 재구성한다. 한국어 literal은 한 글자도 바꾸지 않고, 각 record 끝의 검증된 정적 01 43 명령 1개만 제거한다.

- Base 4건: 7:267, 7:2766, 8:1181, 8:1187
- PK 36건: 2:226,247,327,328,498,528,552,567; 6:546,548,553,1134,1138,1140,3421,3560,3561,3562,3566,3569,3572,3608,3664,3772,4647,4687,4688,4700,4840,4858; 7:271,2832; 8:1106,1114,1197,1203
- Base W45: F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB
- PK W45: 0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092

검증 항목:

- PC JP와 Base PC SC/TC, PK PC EN/SC/TC 원문 앵커 및 파일 해시
- record별 현재/목표 SHA-256·크기·opaque span·marker topology·terminal 명령 offset
- 02xx와 runtime 014301 부재, terminator 보존, literal 무변경
- 최대 3줄·888px (PK 8:1106, 8:1114의 2-literal topology를 별도 검증)
- W46/W48 builder 해시와 실제 scope를 읽어 교집합 0을 executable guard로 검증
- packed/raw 출력 핀, private output 경로 제한

실행:

    & 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe' .\build_pc_dialogue_static_terminal_0143_wave51_v1.py build
    & 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe' .\build_pc_dialogue_static_terminal_0143_wave51_v1.py verify-private
    & 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe' -m unittest -v .\test_pc_dialogue_static_terminal_0143_wave51_v1.py

후보는 KR_PATCH_RELEASE_V0116/tmp/pc_dialogue_static_terminal_0143_wave51_v1/candidate에만 작성된다. Steam 적용, Git write, 네트워크, 릴리즈 작업은 구현하지 않는다.
