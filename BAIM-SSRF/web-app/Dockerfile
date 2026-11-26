# Obie usługi korzystają z tej samej, lekkiej wersji interpretera Python.
FROM python:3.12-slim
# Katalog roboczy wewnątrz kontenera aplikacji.
WORKDIR /app
# Wspólny manifest zależności znajduje się w katalogu głównym kontekstu builda.
COPY requirements.txt .
# Instalacja jest wykonywana przy budowaniu obrazu, nie na komputerze hosta.
RUN pip install --no-cache-dir -r requirements.txt
# Do obrazu web-app kopiujemy tylko jej kod, szablony i pliki statyczne.
COPY web-app/ .
# Flask nasłuchuje wewnątrz kontenera na tym porcie.
EXPOSE 5000
# Start aplikacji bez trybu debug.
CMD ["python", "app.py"]
