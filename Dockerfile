# Usamos la imagen oficial de Python 3.13.1 (versión ligera)
FROM python:3.13.1-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Instalamos pipenv
RUN pip install --no-cache-dir pipenv

# Copiamos los archivos de dependencias primero para aprovechar la caché de Docker
COPY Pipfile Pipfile.lock ./

# Instalamos las dependencias en el sistema (sin crear un entorno virtual dentro del contenedor)
RUN pipenv install --system --deploy

# Copiamos el resto del código del proyecto
COPY . .

# Exponemos el puerto de la API
EXPOSE 8000

# Comando para ejecutar la aplicación con recarga automática para desarrollo
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
