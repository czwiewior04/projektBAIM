# SSRF Demonstration

Lokalne laboratorium edukacyjne pokazujące Server-Side Request Forgery (SSRF). Aplikacja webowa pobiera wskazany adres po stronie backendu, a drugi serwis udostępnia fikcyjne zasoby osiągalne wyłącznie z sieci kontenerów.

> Projekt służy wyłącznie do nauki na lokalnych, fikcyjnych danych. Nie używaj go do testowania cudzych systemów.

## Wymagania

- Docker Desktop (Windows/macOS) albo Docker Engine z Docker Compose
- Przeglądarka internetowa
- Dostęp do Internetu podczas pierwszego budowania obrazów

## Szybki start

### Windows — PowerShell

Uruchom Docker Desktop, otwórz PowerShell w katalogu `BAIM-SSRF` i wpisz:

```powershell
.\start-demo.ps1
```

Jeśli PowerShell zablokuje skrypt, zezwól na jego uruchamianie tylko w bieżącym oknie i uruchom go ponownie:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\start-demo.ps1
```

Zmiana polityki dotyczy tylko tego okna PowerShell i przestaje obowiązywać po jego zamknięciu. Skrypt buduje obrazy i uruchamia obie usługi. Gdy będą gotowe, otwórz <http://localhost:5000>. Zatrzymaj usługi skrótem `Ctrl+C`.

Możesz też uruchomić Compose bez skryptu:

```powershell
docker compose up --build
```

### macOS / Linux

W terminalu, w katalogu `BAIM-SSRF`, uruchom:

```bash
docker compose up --build
```

Następnie otwórz <http://localhost:5000>. Zatrzymaj usługi skrótem `Ctrl+C`.

## Uruchomienie bez Dockera

Można uruchomić oba pliki Python osobno, ale pełny scenariusz demonstracyjny wymaga Docker Compose. Poza siecią Dockera nazwa hosta `internal-api` nie jest rozpoznawana przez komputer.

1. W pierwszym terminalu przejdź do katalogu projektu, zainstaluj wspólne zależności i uruchom aplikację webową:

   ```powershell
   cd C:\ścieżka\do\projektu\BAIM-SSRF
   python -m pip install -r requirements.txt
   python .\web-app\app.py
   ```

2. W drugim terminalu, również z katalogu `BAIM-SSRF`, uruchom usługę wewnętrzną:

   ```powershell
   cd C:\ścieżka\do\projektu\BAIM-SSRF
   python .\internal-api\app.py
   ```

W takim trybie strona webowa działa pod <http://localhost:5000>, a kontrola zdrowia usługi wewnętrznej pod <http://localhost:5001/health>. Jednak przycisk „Wewnętrzny panel (demo)” nie zadziała, bo aplikacja webowa szuka hosta `internal-api`, którego DNS udostępnia tylko sieć Compose.

## Scenariusz demonstracyjny

1. Pozostaw `Vulnerable Mode` i pobierz `https://example.com`.
2. Wybierz przycisk `Wewnętrzny panel (demo)`.
3. W `Vulnerable Mode` backend powinien pobrać fikcyjną odpowiedź z usługi `internal-api`.
4. Przełącz na `Protected Mode` i ponów próbę. Żądanie do wewnętrznego serwisu powinno zostać odrzucone.
5. W `Protected Mode` pobierz ponownie `https://example.com`; ten host jest na demonstracyjnej allowliście.

## Jak połączone są usługi?

| Usługa | Port kontenera | Dostęp z komputera | Rola |
| --- | ---: | --- | --- |
| `web-app` | 5000 | `http://localhost:5000` | Interfejs i backend pobierający podane adresy |
| `internal-api` | 5001 | Brak mapowania portu hosta | Wewnętrzny serwis demonstracyjny |

`internal-api` jest osiągalne po nazwie usługi wyłącznie z sieci Docker `demo-net`. Celowo nie ma mapowania `ports`, więc użytkownik nie otworzy go bezpośrednio z komputera. Stan usług można sprawdzić poleceniem `docker compose ps`.

## Zatrzymywanie i porządkowanie

Jeśli usługi zostały uruchomione w tle albo chcesz zatrzymać je z innego terminala, wykonaj w katalogu projektu:

```powershell
docker compose down
```

To polecenie zatrzymuje i usuwa kontenery oraz sieć Compose; nie usuwa kodu projektu.

## Ograniczenia demonstracji

- `Vulnerable Mode` celowo nie waliduje celu żądania i ilustruje ryzyko SSRF.
- `Protected Mode` to uproszczona demonstracja: dopuszcza HTTPS do `example.com` i sprawdza wyniki DNS.
- Nie jest to kompletna ochrona produkcyjna. Rzeczywista aplikacja wymaga m.in. ochrony przed DNS rebindingiem i TOCTOU, kontroli każdego adresu docelowego i przekierowań, obsługi IPv4/IPv6 oraz ograniczeń ruchu wychodzącego na poziomie sieci.
- Dane zwracane przez wewnętrzne endpointy są fikcyjne.
