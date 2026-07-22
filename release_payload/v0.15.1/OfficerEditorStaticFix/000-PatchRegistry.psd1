@{
    Schema = 'nobu16.static-exe-patch-registry.v3'
    Release = 'v0.15.1'
    AllAppliedSha256 = 'C1E9123539506055C1ACB96A15A446C43952AED607DEA2C9646F690813FA53D5'
    Profiles = @{
        Vertical = @{
            PatchIds = @('001', '002', '003', '007', '009', '010')
            OutputSha256 = '3964E160B789982E1E197F77CBA3F592AFF0144F063E7AFCAC4DCEB4C6C99CB4'
        }
        Horizontal = @{
            PatchIds = @('001', '002', '003', '004', '005', '006', '007', '008', '009', '010')
            OutputSha256 = 'C1E9123539506055C1ACB96A15A446C43952AED607DEA2C9646F690813FA53D5'
        }
    }
    Patches = @(
        @{
            Id = '001'
            File = 'Patches/001-OfficerEditorNameValidation.psd1'
            Size = 671
            Sha256 = '63250365F02264B974A8916037BE3D05795A5B9B72605EF8625B5533CF647F96'
        }
        @{
            Id = '002'
            File = 'Patches/002-FictionalPrincessNameValidation.psd1'
            Size = 565
            Sha256 = '9CFCD1656022DA48F5185854D5C5EE0BE1BF2A5D90FD2E1930D45A38ED831DDF'
        }
        @{
            Id = '003'
            File = 'Patches/003-TopHeaderLayout.psd1'
            Size = 1322
            Sha256 = '60F3932617C5486E5FF75A56C48C897C721BDC8677090D51E18587320B356996'
        }
        @{
            Id = '004'
            File = 'Patches/004-HorizontalMapLabelsDynamicWidth.psd1'
            Size = 16177
            Sha256 = 'D009D596ACC5E1B3A4FC7D74913B5D17F87FA199B38956FBAC456130DEDA754B'
        }
        @{
            Id = '005'
            File = 'Patches/005-DualResolutionAndHorizontalLandmarks.psd1'
            Size = 7335
            Sha256 = '31B31DDD996A403C8FEA1AA710FB709F352DA91AEEE35E050C98C2BF4BBE5E64'
        }
        @{
            Id = '006'
            File = 'Patches/006-HorizontalMapStatusIcons.psd1'
            Size = 1294
            Sha256 = '47B668CD1988C1393F051C4253FE2E895F42D4D1228C50174232F2EB96806625'
        }
        @{
            Id = '007'
            File = 'Patches/007-EventMessageTypography.psd1'
            Size = 378
            Sha256 = 'B9370AA005202CB2E3D2FA22B5F33265517D8354851B434B4A3844EC50796F78'
        }
        @{
            Id = '008'
            File = 'Patches/008-HorizontalMapAuxiliaryIndicators.psd1'
            Size = 1362
            Sha256 = '91DFFF797E00D62567494519E7772ED42A3A966B5D25E488C31BD1B0DD8F0D6F'
        }
        @{
            Id = '009'
            File = 'Patches/009-EventMessageParentWidth.psd1'
            Size = 245
            Sha256 = 'CB70279E78F1B7C2B7F5ED633C5B966D34D8680EEB595BC7C00A8BE1FC57133E'
        }
        @{
            Id = '010'
            File = 'Patches/010-EventMessageAutoWrapLimit.psd1'
            Size = 364
            Sha256 = 'D16D8CA248563EE9A595D0E7BD3D5E2544C1181193ADDCA49B881BCA3FAEEECC'
        }
    )
}
