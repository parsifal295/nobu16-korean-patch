@{
    Id = '010'
    Name = 'Expanded event message auto-wrap limit'
    Kind = 'BytePatch'
    Sites = @(
        @{ Name = 'expand primary event auto-wrap limit from 40 to 60'; Offset = 0x0085BDD4; Before = '27'; After = '3B' }
        @{ Name = 'expand alternate event auto-wrap limit from 40 to 60'; Offset = 0x0088EAF1; Before = '27'; After = '3B' }
    )
}
