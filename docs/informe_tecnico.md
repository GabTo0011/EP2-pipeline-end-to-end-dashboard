# 📑 Informe Técnico de Ingeniería: Pipeline, API y Dashboard (MTT)
**Asignatura:** Programación para la Ciencia de Datos  
**Caso de Estudio:** Matrices de Viajes - Red Movilidad 2026  
**Rol Asociado:** Compañero 1 (Ingeniero de Datos / Desarrollador Backend)

---

## 1. Arquitectura de la Solución e Integración
La solución se diseñó siguiendo una arquitectura desacoplada en tres capas para asegurar la escalabilidad del sistema:
1. **Capa de Datos (ETL):** Un pipeline robusto que procesa el dataset masivo del MTT, aplicando limpieza, consistencia y optimización de memoria.
2. **Capa de Servicio (API REST):** Construida sobre FastAPI, encargada de exponer los endpoints de predicción. Cuenta con un sistema de control de fallos (*fallback*) que permite simular respuestas con lógica de negocio real si los modelos `.pkl` de Machine Learning no están presentes.
3. **Capa de Presentación (Dashboard):** Una interfaz interactiva en Streamlit que se comunica con el sistema **únicamente mediante peticiones HTTP (API REST)**, respetando la restricción de diseño de no cargar datos ni modelos directamente en la interfaz.

---

## 2. Decisiones de Optimización a Gran Escala
El archivo original `Subidas_Paradero_Estacion_2026.04_v3.xlsx` cuenta con un volumen alto de registros (**761,557 filas**). Para evitar desbordamientos de memoria RAM (errores de *Out-Of-Memory*) tanto en desarrollo local como en el posterior despliegue en contenedores Docker, se aplicaron dos técnicas clave:
* **Casteo Explícito a Categorías:** Las columnas con alta cardinalidad repetitiva (`Tipo_dia`, `Modo`, `Comuna`, `Media_hora`) se transformaron al tipo `category` de Pandas.
* **Reducción de Precisión Numérica:** La columna `Subidas_Promedio` se transformó a `float32`.

**Resultados del Pipeline ETL:**
* **Uso de Memoria Inicial:** 96.74 MB  
* **Uso de Memoria Optimizado:** 30.39 MB  
* **Eficiencia/Ahorro de RAM:** **68.59% de optimización de recursos.**

---

## 3. Control de Calidad y Manejo de Errores
El sistema implementa un estándar de **Logging Profesional** que registra eventos críticos, advertencias y fallos tanto en archivos físicos (`pipeline_etl.log` y `api_server.log`) como en la consola. 
* Se validó el esquema de datos rechazando ejecuciones si faltan columnas operacionales obligatorias.
* Se eliminaron registros nulos en llaves operacionales (`Comuna`, `Paradero`) y se forzó la consistencia de negocio eliminando valores de subidas negativos.

---

## 4. Guía de Ejecución y Pruebas del Sistema

### Paso 1: Procesamiento de los Datos (ETL)
Ejecutar el pipeline para generar el set de datos limpio y optimizado en la carpeta procesada:
```bash
python etl/pipeline.py