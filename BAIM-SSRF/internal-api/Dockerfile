# Wewnętrzny serwis używa tej samej wersji Pythona co web-app.
FROM python:3.12-slim
# Ujednolicony katalog roboczy w kontenerze.
WORKDIR /app
# Manifest jest wspólny dla obu usług i leży w katalogu głównym build context.
COPY requirements.txt .
# Instalacja zależności przy budowaniu obrazu kontenera.
RUN pip install --no-cache-dir -r requirements.txt
# Kopiujemy wyłącznie kod wewnętrznego API do jego obrazu.
COPY internal-api/ .
# Port jest osiągalny w sieci Compose; host nie mapuje go bezpośrednio.
EXPOSE 5001
# Start API bez trybu debug.
CMD ["python", "app.py"]
