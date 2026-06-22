INSERT INTO comunas (id,nombre,ingreso_promedio_hogar)
VALUES
(1,'Puente Alto',950000),
(2,'Maipu',1100000),
(3,'San Bernardo',980000),
(4,'Pudahuel',1050000);

INSERT INTO paraderos (id,codigo,latitud,longitud,comuna_id)
VALUES
(1,'PA101',-33.6111,-70.5755,1),
(2,'MA102',-33.5100,-70.7600,2);

INSERT INTO recorridos
(id,nombre,empresa_operadora,capacidad_pasajeros)
VALUES
(1,'Bus 210','Red Movilidad',90),
(2,'Bus 405','Red Movilidad',100);

INSERT INTO monitoreo_viajes
(id,fecha_hora,paradero_id,recorrido_id,
 tiempo_promedio_viaje,flujo_pasajeros,velocidad_promedio)
VALUES
(1,'2026-06-01 08:00:00',1,1,45,500,18),
(2,'2026-06-01 08:15:00',2,2,60,800,12);