# Flask obsługuje interfejs i endpoint JSON; pozostałe moduły wspierają
# demonstracyjną walidację adresu i wykonanie żądania HTTP.
from flask import Flask, render_template, request, jsonify
from urllib.parse import urlparse
import ipaddress
import socket
import requests

# Flask odnajduje szablony i pliki statyczne względem lokalizacji tego modułu.
app = Flask(__name__)

# Nazwa usługi jest rozwiązywana przez DNS sieci Docker Compose.
INTERNAL_HOST = "internal-api"
# Ograniczamy ilość tekstu zwracaną w interfejsie, by duża odpowiedź
# nie zdominowała demonstracji ani pamięci procesu.
MAX_RESPONSE_CHARS = 5000
# Każde żądanie zewnętrzne ma limit czasu, aby nie wisiało bez końca.
TIMEOUT_SECONDS = 5


def protected_url_check(raw_url: str):
    """Demonstracyjna polityka: zezwalamy wyłącznie na https://example.com."""
    try:
        # Rozbijamy tekst URL na schemat, dane logowania, host i port,
        # aby sprawdzać każdy z tych elementów osobno.
        parsed = urlparse(raw_url)
        if parsed.scheme != "https":
            return False, "Dozwolony jest wyłącznie schemat HTTPS."
        # Dane logowania w URL mogą ukrywać rzeczywisty host przed czytelnikiem.
        if parsed.username or parsed.password:
            return False, "Adresy zawierające dane logowania są niedozwolone."
        # Demo dopuszcza tylko jeden jawnie wskazany host.
        if parsed.hostname != "example.com":
            return False, "Host nie znajduje się na allowliście (example.com)."
        # Brak portu oznacza domyślny port HTTPS; jawnie dopuszczamy też 443.
        if parsed.port not in (None, 443):
            return False, "Niedozwolony port."
        # Dodatkowa demonstracyjna kontrola DNS: sprawdzamy każdy adres IPv4/IPv6,
        # do którego może rozwiązać się dozwolona nazwa.
        addresses = {
            item[4][0]
            for item in socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
        }
        # Pusta lista oznacza, że nie mamy adresu, do którego można bezpiecznie
        # przypisać wynik weryfikacji.
        if not addresses:
            return False, "Nie udało się rozwiązać nazwy hosta."
        # Odrzucamy adresy specjalne, prywatne i inne, które nie są globalne.
        if any(not ipaddress.ip_address(addr).is_global for addr in addresses):
            return False, "Host rozwiązuje się do niedozwolonego adresu IP."
        return True, ""
    # Błędny port/URL lub nieudane zapytanie DNS nie powinny przechodzić walidacji.
    except (ValueError, socket.gaierror):
        return False, "Nieprawidłowy adres URL lub błąd DNS."


@app.get("/")
def index():
    # Zwracamy stronę UI; Flask renderuje szablon index.html.
    return render_template("index.html")


@app.post("/fetch")
def fetch_url():
    # Obsługujemy zarówno JSON wysyłany przez interfejs, jak i zwykłe formularze.
    data = request.get_json(silent=True) or request.form
    # Usuwamy odstępy z obu końców, żeby puste pole nie udawało adresu.
    raw_url = (data.get("url") or "").strip()
    # Domyślny tryb pozostaje podatny, żeby zachować charakter laboratorium.
    mode = data.get("mode", "vulnerable")

    # Nie wysyłamy żądania, jeśli użytkownik nie podał celu.
    if not raw_url:
        return jsonify(ok=False, error="Podaj adres URL."), 400

    if mode == "protected":
        # W Protected Mode sprawdzamy cel przed wykonaniem jakiegokolwiek żądania.
        allowed, reason = protected_url_check(raw_url)
        if not allowed:
            # Informujemy UI, że żądanie zostało celowo zablokowane przez politykę.
            return jsonify(
                ok=False,
                blocked=True,
                error=f"Żądanie zablokowane przez Protected Mode: {reason}",
            ), 403
    elif mode != "vulnerable":
        # Nieznane tryby są błędem żądania, a nie domyślną alternatywą.
        return jsonify(ok=False, error="Nieznany tryb aplikacji."), 400

    try:
        # Celowo podatny wariant: w Vulnerable Mode użytkownik kontroluje URL,
        # który pobiera backend — to właśnie demonstruje podstawowy mechanizm SSRF.
        # Przekierowania są wyłączone, by kolejne cele nie zmieniały wyniku ćwiczenia.
        response = requests.get(
            raw_url,
            timeout=TIMEOUT_SECONDS,
            allow_redirects=False,
            headers={"User-Agent": "SSRF-Demo/1.0"},
        )
        # Zachowujemy kod statusu i URL odpowiedzi, ale ograniczamy treść do limitu.
        body = response.text[:MAX_RESPONSE_CHARS]
        return jsonify(
            ok=True,
            status_code=response.status_code,
            final_url=response.url,
            # UI może pokazać użytkownikowi, że treść została skrócona.
            truncated=len(response.text) > MAX_RESPONSE_CHARS,
            body=body,
            mode=mode,
        )
    # Błędy połączenia, DNS i timeouty zwracamy jako odpowiedź bramy HTTP.
    except requests.RequestException as exc:
        return jsonify(ok=False, error=f"Błąd żądania: {exc.__class__.__name__}: {exc}"), 502


if __name__ == "__main__":
    # Nasłuch na wszystkich interfejsach kontenera umożliwia port-forwarding Dockera.
    # Tryb debug jest wyłączony, by nie uruchamiać debuggera podczas demonstracji.
    app.run(host="0.0.0.0", port=5000, debug=False)
