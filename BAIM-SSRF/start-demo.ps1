# Zatrzymaj skrypt przy bledzie PowerShell zamiast kontynuowac niepelny start.
$ErrorActionPreference = "Stop"

# Docker Compose uruchamia obie uslugi oraz ich wspolna siec.
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker CLI was not found. Install and start Docker Desktop."
}

# Uzyj folderu skryptu jako katalogu projektu, bez wzgledu na biezacy folder.
Push-Location $PSScriptRoot
try {
    # Zbuduj obrazy w razie potrzeby i uruchom uslugi na pierwszym planie.
    docker compose up --build
    # Sprawdz kod procesu Docker po zakonczonym poleceniu.
    if ($LASTEXITCODE -ne 0) {
        throw "docker compose failed with exit code $LASTEXITCODE."
    }
}
finally {
    # Przywroc poprzedni katalog takze wtedy, gdy start sie nie powiedzie.
    Pop-Location
}
