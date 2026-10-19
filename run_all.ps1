# Equivalente de `make all` para Windows PowerShell. Uso:  .\run_all.ps1 [-Python python]
param([string]$Python = "python")
$ErrorActionPreference = "Stop"
$steps = @(
  @("-m","pytest","tests","-q"),
  @("-m","src.search"),
  @("-m","src.sample"),
  @("-m","src.extract","--pilot"),
  @("-m","src.extract","--trend","--scale"),
  @("-m","src.gold","evaluate"),
  @("-m","src.analyze"),
  @("-m","src.hypotheses"),
  @("-m","src.plots"),
  @("-m","src.report")
)
foreach ($s in $steps) { Write-Host ">> $Python $($s -join ' ')"; & $Python @s; if ($LASTEXITCODE -ne 0) { throw "fallo en: $($s -join ' ')" } }
