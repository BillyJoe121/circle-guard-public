# Taller 2 - CI/CD CircleGuard

## Servicios seleccionados

Se seleccionaron seis microservicios conectados entre si para permitir pruebas unitarias, integracion, E2E y rendimiento:

- `circleguard-auth-service`: autenticacion y emision de tokens.
- `circleguard-identity-service`: anonimizacion de identidades.
- `circleguard-form-service`: encuestas de salud y eventos Kafka.
- `circleguard-promotion-service`: motor de estados, Neo4j, Redis y eventos.
- `circleguard-notification-service`: consumidores Kafka y despacho de alertas.
- `circleguard-gateway-service`: validacion de QR contra estado de salud en Redis.

Flujo principal cubierto: identidad -> autenticacion -> encuesta -> promocion de estado -> cache Redis -> validacion de ingreso -> notificaciones.

## Herramientas verificadas

- Java: Temurin JDK 21.
- Gradle: wrapper `./gradlew`, Gradle 8.14.
- Docker: Docker Desktop.
- Kubernetes: Docker Desktop Kubernetes, Minikube o Kind.
- Jenkins: controlador con Java 21.
- Python: requerido para pruebas externas con Pytest y Locust.

## Pipelines

### Dev

Archivo: `Jenkinsfile.dev`

Fases:

1. Checkout del fork.
2. Pruebas unitarias nuevas del taller mediante `ci/run-unit-tests.sh`.
3. Construccion de imagenes Docker.
4. Despliegue en namespace `circleguard-dev`.

### Stage

Archivo: `Jenkinsfile.stage`

Fases:

1. Checkout.
2. Build y pruebas unitarias nuevas del taller mediante `ci/run-unit-tests.sh`.
3. Construccion de imagenes Docker.
4. Despliegue en namespace `circleguard-stage`.
5. Pruebas de integracion y E2E contra servicios desplegados en Kubernetes.

### Master

Archivo: `Jenkinsfile.master`

Fases:

1. Checkout.
2. Build y pruebas unitarias nuevas del taller mediante `ci/run-unit-tests.sh`.
3. Construccion de imagenes de release.
4. Despliegue en namespace `circleguard-master`.
5. Pruebas de sistema.
6. Pruebas de rendimiento y estres con Locust.
7. Generacion automatica de `release-notes.md`.

## Kubernetes

Los manifiestos estan en:

- `k8s/base`: recursos comunes, infraestructura y deployments.
- `k8s/dev`: overlay dev.
- `k8s/stage`: overlay stage.
- `k8s/master`: overlay master.

Validacion local de render:

```bash
kubectl kustomize k8s/dev
kubectl kustomize k8s/stage
kubectl kustomize k8s/master
```

Despliegue manual:

```bash
bash ci/deploy-k8s.sh dev circleguard dev
```

## Pruebas agregadas

Unitarias Java:

- `QrTokenServiceWorkshopTest`: valida subject y expiracion de QR.
- `SymptomMapperWorkshopTest`: valida respuestas nulas, dificultad respiratoria y seleccion multiple de sintomas.

Integracion Pytest:

- `tests/integration/test_service_communication.py`

E2E Pytest:

- `tests/e2e/test_user_flows.py`

Rendimiento:

- `tests/performance/locustfile.py`

Ejecucion local de unitarias nuevas:

```bash
bash ci/run-unit-tests.sh
```

En Windows sin Bash, ejecutar el equivalente:

```powershell
.\gradlew.bat :services:circleguard-auth-service:test --tests "com.circleguard.auth.service.QrTokenServiceWorkshopTest" `
  :services:circleguard-form-service:test --tests "com.circleguard.form.service.SymptomMapperWorkshopTest" `
  --console=plain --no-daemon
```

Nota: el repositorio base trae algunas pruebas heredadas inestables que dependen de Postgres local, claves JWT de prueba debiles y Testcontainers. Los pipelines del taller ejecutan las pruebas nuevas controladas y luego validan el sistema real con Pytest y Locust sobre Kubernetes.

Ejecucion de integracion/E2E contra servicios expuestos localmente:

```bash
python -m pip install -r tests/system/requirements.txt
pytest tests/integration tests/e2e
```

Ejecucion Locust headless:

```bash
locust -f tests/performance/locustfile.py --headless --users 20 --spawn-rate 5 --run-time 1m --csv build/locust/circleguard --html build/locust/report.html
```

## Evidencias requeridas

Para el informe y video tomar pantallazos de:

- Configuracion del job Jenkins usando cada Jenkinsfile.
- Credenciales configuradas sin mostrar secretos.
- Consola de ejecucion exitosa de cada pipeline.
- Resultados JUnit publicados.
- Pods y services de Kubernetes:

```bash
kubectl get pods -n circleguard-dev
kubectl get svc -n circleguard-dev
kubectl get pods -n circleguard-stage
kubectl get pods -n circleguard-master
```

- Imagenes Docker generadas:

```bash
docker images | findstr circleguard
```

- Reporte HTML/CSV de Locust.
- Release notes archivadas por Jenkins.

## Analisis esperado de rendimiento

En el reporte deben interpretarse:

- Tiempo promedio de respuesta.
- Percentiles p50, p95 y p99.
- Throughput en requests por segundo.
- Tasa de errores.
- Endpoint mas lento y posible causa.
- Comparacion entre carga normal y estres.
