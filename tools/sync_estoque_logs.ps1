$ErrorActionPreference = "SilentlyContinue"

$SourceDir = "\\192.168.1.170\C$\Users\estoque\AppData\Roaming\RelatorioEstoque"
$TargetDir = "D:\relatorioEstoque\remote_logs"
$IntervalSeconds = 2

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

Write-Host "Sincronizando logs do estoque..."
Write-Host "Origem:  $SourceDir"
Write-Host "Destino: $TargetDir"
Write-Host "Pressione Ctrl+C para parar."

while ($true) {
    if (Test-Path -LiteralPath $SourceDir) {
        Get-ChildItem -LiteralPath $SourceDir -Filter "*.log" -File | ForEach-Object {
            $target = Join-Path $TargetDir $_.Name
            Copy-Item -LiteralPath $_.FullName -Destination $target -Force
        }
    }
    Start-Sleep -Seconds $IntervalSeconds
}
