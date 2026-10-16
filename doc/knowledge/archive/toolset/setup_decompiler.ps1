$ErrorActionPreference = 'Stop'
$runtimeDir = Join-Path $PSScriptRoot 'runtime'
New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
$packages = @(
    @{Name='ghidra.zip'; Url='https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.1.4_build/ghidra_12.1.4_PUBLIC_20260921.zip'; Hash='ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db'},
    @{Name='jdk.zip'; Url='https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.4.1%2B1/OpenJDK25U-jdk_x64_windows_hotspot_25.0.4.1_1.zip'; Hash='00c847d804f4a78e9f04f2683faf14fed898535b177b7fc704486cb0284e9283'}
)
foreach ($package in $packages) {
    $archive = Join-Path $runtimeDir $package.Name
    if (-not (Test-Path -LiteralPath $archive)) {
        Invoke-WebRequest -Uri $package.Url -OutFile $archive
    }
    if ((Get-FileHash -LiteralPath $archive).Hash.ToLowerInvariant() -ne $package.Hash) {
        throw "Checksum mismatch for $($package.Name)"
    }
    Write-Output "Verified $($package.Name)"
    $expanded = Join-Path $runtimeDir ($package.Name.Replace('.zip',''))
    if (-not (Test-Path -LiteralPath $expanded)) {
        Expand-Archive -LiteralPath $archive -DestinationPath $expanded
    }
    Write-Output "Extracted $($package.Name)"
}
$packages | ConvertTo-Json | Set-Content (Join-Path $runtimeDir 'downloads.json')
