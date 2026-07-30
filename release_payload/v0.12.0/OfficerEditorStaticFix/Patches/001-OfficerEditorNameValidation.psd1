@{
    Id = '001'
    Name = 'Officer editor Korean name validation'
    Sites = @(
        @{ Name = 'visible surname characters'; Offset = 0x00BAF630; Before = '0F84B4010000'; After = '909090909090' }
        @{ Name = 'visible given-name characters'; Offset = 0x00BAF640; Before = '0F84A4010000'; After = '909090909090' }
        @{ Name = 'surname reading characters'; Offset = 0x00BAF656; Before = '0F848E010000'; After = '909090909090' }
        @{ Name = 'given-name reading characters'; Offset = 0x00BAF667; Before = '0F847D010000'; After = '909090909090' }
        @{ Name = 'combined name length'; Offset = 0x00BAF6C8; Before = '7E0C'; After = 'EB0C' }
    )
}
