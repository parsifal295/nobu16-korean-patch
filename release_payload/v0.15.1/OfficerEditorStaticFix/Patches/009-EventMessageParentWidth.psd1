@{
    Id = '009'
    Name = 'Expand event message parent width'
    Kind = 'BytePatch'
    Sites = @(
        @{ Name = 'expand event message parent width from 882 to 972'; Offset = 0x0151BD88; Before = '00805C44'; After = '00007344' }
    )
}
