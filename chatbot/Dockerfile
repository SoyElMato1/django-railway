# Dockerfile para el chatbot
FROM python:3.10.0

WORKDIR /app

# Copiar requirements.txt e instalar dependencias
RUN pip install rasa
RUN pip install supervisor  # Para gestionar múltiples procesos

# Copiar el resto del código
COPY . .

# Entrenar el modelo de Rasa
RUN rasa train

# Exponer los puertos para Rasa
EXPOSE 5005 5055

# Configurar supervisord para ejecutar Rasa y sus acciones
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Comando para iniciar supervisord
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
