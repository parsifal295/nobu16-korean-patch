@{
    Id = '007'
    Name = 'Compact event message typography'
    Kind = 'BytePatch'
    Sites = @(
        @{ Name = 'reduce event message line spacing from 10 to 8'; Offset = 0x0089957A; Before = 'BF000A0000'; After = 'BF00080000' }
        @{ Name = 'reduce event message font size from 36 to 30'; Offset = 0x008995BC; Before = 'B924000000'; After = 'B91E000000' }
    )
}
