```md
# Guía de contribución
En este documento se definiran las normas de 
trabajo colaborativo del repositorio.
```  
---

## Estrategia de ramificación

Se utiliza la estragia de ramificación basada en **GitFlow**.

### Ramas principales
- `main`: versión estable
- `develop`: integración de cambios

### Ramas de trabajo
- `feature/*`: nuevas funcionalidades
- `hotfix/*`: correcciones urgentes en [ `main` ]
- `bugfix/*`: para corregir errores en [ `develop` ]


## Nombramiento (naming) de ramas

Formato:

- `feature/nombre-funcionalidad`
- `hotfix/nombre-correccion`
- `docs/nombre-documento`

### Ejemplos

- `feature/add-user-validations`
- `feature/filter-users-by-role`
- `feature/add-created-at-field`
- `feature/add-users-health-endpoint`
- `hotfix/fix-user-not-found-response`

## Convenciones de commits

Formato:

- `feat: nueva funcionalidad`
- `fix: corrección de error`
- `docs: documentación`
- `test: pruebas`
- `refactor: mejora de código`

### Ejemplos

- `feat: agrega validaciones de usuario`
- `feat: agrega filtro por rol`
- `feat: agrega campo createdAt`
- `fix: corrige respuesta usuario no encontrado`
- `docs: agrega README y CONTRIBUTING`


## Flujo de trabajo

### Features

1. Crear rama desde `develop`
2. Implementar funcionalidad
3. Hacer commits descriptivos
4. Subir rama
5. Crear Pull Request hacia `develop`
6. Revisar y aprobar
7. Merge

### Hotfix

1. Crear rama desde `main`
2. Aplicar corrección
3. Commit
4. Push
5. Pull Request hacia `main`
6. Merge
7. Sincronizar `develop`


## Reglas de merge

- No hacer push directo a `main`
- Todo cambio debe pasar por Pull Request
- Todo PR debe ser revisado
- Después de un hotfix, sincronizar `develop`

## Revisión de código

Cada Pull Request debe ser revisado por otro integrante.

### Validar:

- código funcional
- objetivo cumplido
- commits claros
- naming correcto
- sin errores

## Criterios de aprobación de PR

Un PR se aprueba solo si:

- compila correctamente
- los tests pasan
- el pipeline CI es exitoso
- cumple el objetivo
- mantiene buenas prácticas

## Integración continua

Se utiliza GitHub Actions.

### Ejecuta en:
- push a `develop`
- pull request a `main`

### Validaciones:
- instalación de dependencias
- tests
- build

## Responsabilidades

Cada integrante debe:

- seguir GitFlow
- usar nombres correctos
- hacer commits claros
- revisar PRs
- validar CI
- mantener documentación

## Objetivo

Mantener un flujo ordenado, colaborativo y trazable, alineado con buenas prácticas DevOps.