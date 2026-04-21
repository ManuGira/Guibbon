#!/usr/bin/env pwsh
# Run local CI checks

Write-Host "Running tests..." -ForegroundColor Cyan
uv run pytest tests
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`nRunning ruff..." -ForegroundColor Cyan
uv run ruff check --fix
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ruff checks failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`nRunning ty..." -ForegroundColor Cyan
uv run ty check
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ty checks failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`nAll checks passed! ✓" -ForegroundColor Green
