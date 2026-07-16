# Steam JP `strdata` P0 통합 후보

이 스트림은 활성 Steam JP v6 `MSG/JP/strdata.bin` 단일 baseline에서 P0-01~04의 1,400개 한글 치환을 통합한다. P0-05의 6개 공식 엔딩 크레딧은 번역/변조하지 않고 별도 source-free 보류 증명으로만 포함한다.

통합 전 확인 항목:

- 각 입력 오버레이의 SHA-256, active JP packed/raw pin, 원문 UTF-16LE hash
- 다섯 P0 묶음의 좌표 수 1,406과 묶음 간 중복 0
- 한글 1,400개에 대한 제어 코드·줄바꿈·printf 불변성
- P0-05 공식 크레딧 6개는 해시 검증 후 무변경
- 선택 외 30,911개 텍스트 좌표·inner header·slot 구조 보존과 두 번의 바이트 동일 빌드

공개 통합 오버레이에는 원문과 완전한 게임 리소스가 없다. 실제 후보는 `tmp/steam_jp_strdata_p0_integrated_v1/` 안에만 쓴다. 게임 설치·릴리즈·GitHub·로고/타이틀 아트(`/3`, `/24` 포함)는 변경하지 않는다.
