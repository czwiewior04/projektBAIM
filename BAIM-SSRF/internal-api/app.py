# Ten serwis udaje wewnętrzny API. Odpowiedzi zawierają wyłącznie fikcyjne dane.
from flask import Flask, jsonify

# Osobna instancja aplikacji dla usługi, która działa w drugim kontenerze.
app = Flask(__name__)


# Docker Compose odpytuje ten endpoint, zanim uzna usługę za gotową.
@app.get("/health")
def health():
    return jsonify(status="healthy")


# Zwykły endpoint informacyjny pokazuje, że wewnętrzne API działa.
@app.get("/")
def index():
    return jsonify(service="Internal API", purpose="SSRF demonstration")


# Endpoint używany przez przycisk „Wewnętrzny panel (demo)” w aplikacji webowej.
@app.get("/admin")
def admin():
    # Wyłącznie fikcyjne dane demonstracyjne.
    return jsonify(
        page="Internal administration panel",
        environment="DEMO",
        server="internal-api",
        message="This response was retrieved by the web application backend.",
        sample_records=[
            {"id": 101, "name": "Demo user A"},
            {"id": 102, "name": "Demo user B"}
        ]
    )


# Dodatkowy przykład danych z wewnętrznego serwisu raportowego.
@app.get("/internal")
def internal():
    return jsonify(
        service="Internal reporting service",
        network="docker-demo-net",
        classification="FICTIONAL TRAINING DATA"
    )

if __name__ == "__main__":
    # Port 5001 jest dostępny wewnątrz sieci Compose; Compose celowo
    # nie publikuje go jako portu hosta.
    app.run(host="0.0.0.0", port=5001, debug=False)
