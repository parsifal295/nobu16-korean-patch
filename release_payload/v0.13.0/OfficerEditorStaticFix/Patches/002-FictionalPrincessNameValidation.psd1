@{
    Id = '002'
    Name = 'Fictional princess Korean name validation'
    Sites = @(
        @{ Name = 'entered-name characters'; Offset = 0x00EB3BBF; Before = 'E84C6ECEFF'; After = 'B801000000' }
        @{ Name = 'entered-reading characters'; Offset = 0x00EB3BE0; Before = 'E8CB6ECEFF'; After = 'B801000000' }
        @{ Name = 'inherited-surname characters'; Offset = 0x00EB3C4F; Before = 'E8BC6DCEFF'; After = 'B801000000' }
        @{ Name = 'inherited-surname-reading characters'; Offset = 0x00EB3C78; Before = 'E8336ECEFF'; After = 'B801000000' }
    )
}
