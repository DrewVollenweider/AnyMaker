param([Parameter(ValueFromRemainingArguments=$true)][string[]]$HeadlessArguments)
$ErrorActionPreference = 'Stop'
$runtime = Join-Path $PSScriptRoot 'runtime'
$ghidra = Join-Path $runtime 'ghidra\ghidra_12.1.4_PUBLIC'
$jdk = Get-ChildItem -LiteralPath (Join-Path $runtime 'jdk') -Directory | Select-Object -First 1
if (-not $jdk) { throw 'Portable JDK not found' }
$java = Join-Path $jdk.FullName 'bin\java.exe'
$state = Join-Path $runtime 'state'
New-Item -ItemType Directory -Path $state -Force | Out-Null
$vm = @('-Xmx2G', '-Xshare:off', '--enable-native-access=ALL-UNNAMED',
    '-Djava.system.class.loader=ghidra.GhidraClassLoader', '-Dfile.encoding=UTF8',
    '-Dsun.java2d.d3d=false', '-Dlog4j.skipJansi=true',
    "-Duser.home=$state", "-Dapplication.settingsdir=$state\settings",
    "-Dapplication.cachedir=$state\cache", "-Dapplication.tempdir=$state\tmp",
    '-Djavax.xml.accessExternalDTD=', '-Djavax.xml.accessExternalSchema=',
    '-Djavax.xml.accessExternalStylesheet=')
& $java @vm -cp (Join-Path $ghidra 'Ghidra\Framework\Utility\lib\Utility.jar') ghidra.Ghidra ghidra.app.util.headless.AnalyzeHeadless @HeadlessArguments
if ($LASTEXITCODE -ne 0) { throw "Ghidra exited with status $LASTEXITCODE" }
