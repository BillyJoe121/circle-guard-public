# Jenkins y Kubernetes - Preparacion

## 1. Kubernetes en Docker Desktop

En Docker Desktop:

1. Abrir Settings.
2. Entrar a Kubernetes.
3. Activar Enable Kubernetes.
4. Apply & Restart.

Validar en PowerShell:

```powershell
kubectl config get-contexts
kubectl config use-context docker-desktop
kubectl get nodes
```

Debe aparecer un nodo `docker-desktop` en estado `Ready`.

## 2. Jenkins

El contenedor `jenkins-controller` ya tiene Docker CLI y Git. Debe tener tambien:

- Java 21 en el PATH.
- `kubectl`.
- Python 3 con `venv`.
- Acceso al `kubeconfig` de Docker Desktop.

Validacion:

```powershell
docker exec jenkins-controller sh -lc "java -version && docker --version && kubectl version --client && python3 --version"
```

## 3. Instalar kubectl dentro del contenedor Jenkins

Ejecutar:

```powershell
docker exec -u root jenkins-controller sh -lc "curl -L -o /usr/local/bin/kubectl https://dl.k8s.io/release/v1.34.1/bin/linux/amd64/kubectl && chmod +x /usr/local/bin/kubectl"
```

Validar:

```powershell
docker exec jenkins-controller sh -lc "kubectl version --client"
```

## 4. Instalar Python dentro del contenedor Jenkins

Ejecutar:

```powershell
docker exec -u root jenkins-controller sh -lc "apt-get update && apt-get install -y python3 python3-pip python3-venv"
```

Validar:

```powershell
docker exec jenkins-controller sh -lc "python3 --version"
```

## 5. Darle kubeconfig a Jenkins

Crear carpeta:

```powershell
docker exec -u root jenkins-controller mkdir -p /var/jenkins_home/.kube
```

Copiar kubeconfig:

```powershell
docker cp "$env:USERPROFILE\.kube\config" jenkins-controller:/var/jenkins_home/.kube/config
docker exec -u root jenkins-controller chown -R jenkins:jenkins /var/jenkins_home/.kube
```

Validar:

```powershell
docker exec jenkins-controller sh -lc "kubectl config get-contexts && kubectl get nodes"
```

## 6. Jobs Jenkins

Crear tres Pipeline jobs:

- `circleguard-dev`: usar `Jenkinsfile.dev`.
- `circleguard-stage`: usar `Jenkinsfile.stage`.
- `circleguard-master`: usar `Jenkinsfile.master`.

Repositorio:

```text
https://github.com/BillyJoe121/circle-guard-public.git
```

Branch:

```text
taller2
```

Parametros iniciales:

- `REGISTRY`: tu usuario/namespace de Docker Hub o GHCR, por ejemplo `billyjoe121`.
- `PUSH_IMAGES`: `true` para que Kubernetes pueda descargar las imagenes creadas por Jenkins.

Como Jenkins usa Docker-in-Docker, las imagenes construidas por Jenkins no quedan automaticamente en el Docker Desktop del host. Por eso, para ejecuciones reales de `stage` y `master`, usar un registry y activar `PUSH_IMAGES=true`.

## 7. Credencial Docker Registry

Crear una credencial Jenkins:

- Kind: `Username with password`.
- ID: `docker-registry`.
- Username: usuario del registry.
- Password: token o password del registry.

Los Jenkinsfiles hacen login automaticamente cuando `PUSH_IMAGES=true`.
