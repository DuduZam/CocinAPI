-- app/db/init_db.sql

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    genero VARCHAR(50),
    edad INTEGER,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recetas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    instrucciones JSONB,
    tiempo_preparacion INTEGER,
    tiempo_coccion INTEGER,
    porciones INTEGER,
    es_publica BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ingredientes (
    id SERIAL PRIMARY KEY,
    receta_id INTEGER REFERENCES recetas(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    cantidad REAL NOT NULL,
    unidad_medida VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS tag_recetas (
    id SERIAL PRIMARY KEY,
    receta_id INTEGER REFERENCES recetas(id) ON DELETE CASCADE,
    tag VARCHAR(50) NOT NULL
);
