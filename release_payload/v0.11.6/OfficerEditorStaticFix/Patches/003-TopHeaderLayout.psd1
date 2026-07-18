@{
    Id = '003'
    Name = 'Korean top-header horizontal layout'
    Sites = @(
        @{ Name = 'top-header panel width'; Offset = 0x01CA7B08; Before = 'B8020000'; After = '0A030000' }
        @{ Name = 'ruler-name textbox width'; Offset = 0x01CA7C68; Before = 'D8000000'; After = '7A010000' }
        @{ Name = 'prestige icon X'; Offset = 0x01CA7C70; Before = 'FB010000'; After = '83020000' }
        @{ Name = 'prestige value X'; Offset = 0x01CA7C80; Before = '1B020000'; After = 'A3020000' }
        @{ Name = 'labor icon X'; Offset = 0x01CA7C90; Before = '6B020000'; After = 'E5020000' }
        @{ Name = 'labor value X'; Offset = 0x01CA7CA0; Before = '8B020000'; After = '05030000' }
        @{ Name = 'labor value width'; Offset = 0x01CA7CA8; Before = '62000000'; After = '40000000' }
        @{ Name = 'book icon X'; Offset = 0x01CA7CB0; Before = 'E7020000'; After = '4F030000' }
        @{ Name = 'book value X'; Offset = 0x01CA7CC0; Before = '07030000'; After = '6F030000' }
        @{ Name = 'book value width'; Offset = 0x01CA7CC8; Before = '38000000'; After = '2A000000' }
        @{ Name = 'prestige interaction anchor X'; Offset = 0x01CA7D00; Before = '12020000'; After = '99020000' }
        @{ Name = 'book interaction anchor X'; Offset = 0x01CA7D10; Before = 'FD020000'; After = '5E030000' }
    )
}
