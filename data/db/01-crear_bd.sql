CREATE TABLE comunas (
    id INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ingreso_promedio_hogar NUMERIC(12,2)
);

CREATE TABLE paraderos (
    id INT PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL,
    latitud NUMERIC(10,6),
    longitud NUMERIC(10,6),
    comuna_id INT NOT NULL,

    CONSTRAINT fk_comuna
        FOREIGN KEY (comuna_id)
        REFERENCES comunas(id)
);

CREATE TABLE recorridos (
    id INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    empresa_operadora VARCHAR(100),
    capacidad_pasajeros INT
);

CREATE TABLE monitoreo_viajes (
    id INT PRIMARY KEY,
    fecha_hora TIMESTAMP,
    paradero_id INT NOT NULL,
    recorrido_id INT NOT NULL,
    tiempo_promedio_viaje NUMERIC(10,2),
    flujo_pasajeros INT,
    velocidad_promedio NUMERIC(10,2),

    CONSTRAINT fk_paradero
        FOREIGN KEY (paradero_id)
        REFERENCES paraderos(id),

    CONSTRAINT fk_recorrido
        FOREIGN KEY (recorrido_id)
        REFERENCES recorridos(id)
);