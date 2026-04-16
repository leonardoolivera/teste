param(
    [ValidateSet('install', 'backoffice', 'portal', 'build', 'lint')]
    [string]$Target = 'backoffice'
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$nodeDir = Join-Path $projectRoot '.tools\node'
$npm = Join-Path $nodeDir 'npm.cmd'
$frontendDir = Join-Path $projectRoot 'frontend'

if (-not (Test-Path $npm)) {
    throw 'Node portatil nao encontrado em .tools\node. Rode a etapa de provisionamento antes de usar o frontend.'
}

$env:Path = "$nodeDir;$env:Path"

Push-Location $frontendDir
try {
    if ($Target -eq 'install' -or -not (Test-Path (Join-Path $frontendDir 'node_modules'))) {
        & $npm install
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    }

    switch ($Target) {
        'install' {
            Write-Host 'Dependencias do frontend instaladas com sucesso.'
        }
        'backoffice' {
            & $npm run dev --workspace @biblioteca-ifms/backoffice
        }
        'portal' {
            & $npm run dev --workspace @biblioteca-ifms/portal-leitor
        }
        'build' {
            & $npm run build
        }
        'lint' {
            & $npm run lint
        }
    }

    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}