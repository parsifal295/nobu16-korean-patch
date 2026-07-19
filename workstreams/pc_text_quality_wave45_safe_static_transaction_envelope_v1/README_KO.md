# Wave 45 보수적 텍스트 통합 transaction envelope

Wave 42 이벤트 26건과 Wave 44 인물 대사 51건을 하나의 PC-only 11파일 후보로 합친다. 실제로 달라지는 리소스는 이벤트 2개와 대사 2개뿐이며 나머지 7개는 현재 Steam 파일과 byte-identical로 유지한다.

이 작업물은 private 후보를 만드는 것만 수행한다. 게임 프로세스가 실행 중일 때 Steam 파일을 쓰지 않으며, 실제 적용은 별도의 process-gated transaction dry-run과 화면 QA 이후에만 가능하다.
