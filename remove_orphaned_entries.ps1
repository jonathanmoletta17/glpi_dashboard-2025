# Script para Remover Entradas Órfãs e Suspeitas do Menu de Contexto
# Remove especificamente entradas de IDEs desinstaladas e outras entradas problemáticas

param(
    [switch]$Force = $false
)

# Verificar se está executando como administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERRO: Execute como Administrador!" -ForegroundColor Red
    exit 1
}

Write-Host "=== REMOÇÃO DE ENTRADAS ÓRFÃS DO MENU DE CONTEXTO ===" -ForegroundColor Cyan
Write-Host "Data/Hora: $(Get-Date)" -ForegroundColor Gray
Write-Host ""

# Criar backup antes de fazer alterações
$backupFile = "context_menu_cleanup_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').reg"
Write-Host "Criando backup do registro: $backupFile" -ForegroundColor Yellow

try {
    reg export "HKEY_CLASSES_ROOT\*\shell" "$backupFile" /y 2>$null
    reg export "HKEY_CLASSES_ROOT\Directory\shell" "$backupFile" /y 2>$null
    reg export "HKEY_CLASSES_ROOT\Directory\Background\shell" "$backupFile" /y 2>$null
    Write-Host "✓ Backup criado com sucesso" -ForegroundColor Green
} catch {
    Write-Host "✗ Erro ao criar backup: $($_.Exception.Message)" -ForegroundColor Red
    if (-not $Force) {
        Write-Host "Use -Force para continuar sem backup" -ForegroundColor Yellow
        exit 1
    }
}

# Lista de entradas suspeitas conhecidas para verificar
$suspiciousEntries = @(
    @{
        Path = "HKEY_CLASSES_ROOT\*\shell\Cursor"
        Name = "Cursor IDE (possivelmente desinstalado)"
        CheckPath = "C:\Users\jonathan-moletta.PPIRATINI\AppData\Local\Programs\cursor\Cursor.exe"
    },
    @{
        Path = "HKEY_CLASSES_ROOT\Directory\Background\shell\Cursor"
        Name = "Cursor IDE Background (possivelmente desinstalado)"
        CheckPath = "C:\Users\jonathan-moletta.PPIRATINI\AppData\Local\Programs\cursor\Cursor.exe"
    }
)

# Função para verificar se uma entrada é órfã
function Test-OrphanedEntry {
    param(
        [string]$RegistryPath,
        [string]$ExecutablePath
    )
    
    if ([string]::IsNullOrEmpty($ExecutablePath)) {
        return $false
    }
    
    # Limpar o caminho removendo aspas e argumentos
    $cleanPath = $ExecutablePath -replace '"', '' -replace '%[^%]*%', '' -split ' ' | Select-Object -First 1
    
    return -not (Test-Path $cleanPath -ErrorAction SilentlyContinue)
}

# Função para detectar caracteres suspeitos
function Test-SuspiciousText {
    param([string]$text)
    
    if ([string]::IsNullOrEmpty($text)) { return $false }
    
    # Detectar caracteres chineses, japoneses, coreanos
    $cjkPattern = '[\u4e00-\u9fff\u3400-\u4dbf\uac00-\ud7af\u3040-\u309f\u30a0-\u30ff]'
    if ($text -match $cjkPattern) { return $true }
    
    # Detectar caracteres de controle ou não imprimíveis
    if ($text -match '[\x00-\x1f\x7f-\x9f]') { return $true }
    
    # Padrões suspeitos específicos
    $suspiciousPatterns = @('口口条', '[\u2600-\u26FF]', '[\u2700-\u27BF]')
    foreach ($pattern in $suspiciousPatterns) {
        if ($text -match $pattern) { return $true }
    }
    
    return $false
}

Write-Host "Analisando entradas do menu de contexto..." -ForegroundColor Yellow

$entriesToRemove = @()

# Verificar entradas conhecidas suspeitas
foreach ($entry in $suspiciousEntries) {
    Write-Host "Verificando: $($entry.Name)" -ForegroundColor Gray
    
    try {
        $regResult = reg query $entry.Path 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Entrada encontrada no registro" -ForegroundColor Yellow
            
            if (Test-OrphanedEntry -RegistryPath $entry.Path -ExecutablePath $entry.CheckPath) {
                Write-Host "  ✗ Executável não encontrado: $($entry.CheckPath)" -ForegroundColor Red
                $entriesToRemove += $entry
            } else {
                Write-Host "  ✓ Executável existe: $($entry.CheckPath)" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "  Erro ao verificar entrada: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Buscar por entradas com caracteres suspeitos
Write-Host ""
Write-Host "Procurando por entradas com caracteres suspeitos..." -ForegroundColor Yellow

$registryPaths = @(
    "HKEY_CLASSES_ROOT\*\shell",
    "HKEY_CLASSES_ROOT\Directory\shell",
    "HKEY_CLASSES_ROOT\Directory\Background\shell"
)

foreach ($regPath in $registryPaths) {
    try {
        $entries = reg query $regPath /s 2>$null
        if ($LASTEXITCODE -eq 0) {
            $currentKey = ""
            $currentName = ""
            
            foreach ($line in $entries) {
                if ($line -match "^HKEY_") {
                    $currentKey = $line.Trim()
                    $currentName = ""
                }
                elseif ($line -match "^\s+\(padrão\)\s+REG_.*?\s+(.+)$") {
                    $currentName = $matches[1]
                    
                    if (Test-SuspiciousText $currentName) {
                        Write-Host "  ✗ Entrada suspeita encontrada: $currentKey -> $currentName" -ForegroundColor Red
                        $entriesToRemove += @{
                            Path = $currentKey
                            Name = "Entrada suspeita: $currentName"
                            CheckPath = ""
                        }
                    }
                }
            }
        }
    } catch {
        Write-Host "Erro ao verificar $regPath : $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Mostrar resumo das entradas a serem removidas
Write-Host ""
Write-Host "=== RESUMO DAS ENTRADAS A SEREM REMOVIDAS ===" -ForegroundColor Red

if ($entriesToRemove.Count -eq 0) {
    Write-Host "Nenhuma entrada órfã ou suspeita encontrada." -ForegroundColor Green
    Write-Host ""
    Write-Host "Análise concluída. O menu de contexto parece estar limpo." -ForegroundColor Green
    exit 0
}

foreach ($entry in $entriesToRemove) {
    Write-Host "• $($entry.Name)" -ForegroundColor Yellow
    Write-Host "  Caminho: $($entry.Path)" -ForegroundColor Gray
    if ($entry.CheckPath) {
        Write-Host "  Executável: $($entry.CheckPath)" -ForegroundColor Gray
    }
    Write-Host ""
}

# Confirmar remoção
if (-not $Force) {
    Write-Host "Deseja remover essas entradas? (S/N): " -ForegroundColor Yellow -NoNewline
    $confirmation = Read-Host
    if ($confirmation -notmatch '^[SsYy]') {
        Write-Host "Operação cancelada pelo usuário." -ForegroundColor Yellow
        exit 0
    }
}

# Remover entradas
Write-Host ""
Write-Host "=== INICIANDO REMOÇÃO ===" -ForegroundColor Red

$removedCount = 0
foreach ($entry in $entriesToRemove) {
    Write-Host "Removendo: $($entry.Name)" -ForegroundColor Yellow
    
    try {
        $regPath = $entry.Path.Replace("HKEY_CLASSES_ROOT", "HKCR")
        reg delete $regPath /f 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Removida com sucesso" -ForegroundColor Green
            $removedCount++
        } else {
            Write-Host "  ✗ Falha na remoção (código: $LASTEXITCODE)" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ✗ Erro: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Limpar cache do Windows Explorer
Write-Host ""
Write-Host "Limpando cache do Windows Explorer..." -ForegroundColor Yellow
try {
    # Parar Windows Explorer
    Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    # Limpar cache de ícones
    $iconCachePath = "$env:LOCALAPPDATA\IconCache.db"
    if (Test-Path $iconCachePath) {
        Remove-Item $iconCachePath -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Cache de ícones limpo" -ForegroundColor Green
    }
    
    # Reiniciar Windows Explorer
    Start-Process explorer
    Write-Host "  ✓ Windows Explorer reiniciado" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Erro ao limpar cache: $($_.Exception.Message)" -ForegroundColor Red
}

# Relatório final
Write-Host ""
Write-Host "=== LIMPEZA CONCLUÍDA ===" -ForegroundColor Green
Write-Host "Entradas removidas: $removedCount de $($entriesToRemove.Count)" -ForegroundColor White
Write-Host "Backup salvo em: $backupFile" -ForegroundColor Yellow
Write-Host ""
Write-Host "PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Teste o menu de contexto clicando com o botão direito em arquivos e pastas" -ForegroundColor White
Write-Host "2. Verifique se as entradas suspeitas foram removidas" -ForegroundColor White
Write-Host "3. Se houver problemas, restaure o backup usando:" -ForegroundColor White
Write-Host "   reg import `"$backupFile`"" -ForegroundColor Gray
Write-Host ""
Write-Host "Limpeza concluída em $(Get-Date)" -ForegroundColor Gray