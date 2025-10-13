# LR1 Serverless Service (Python)

Este es un servicio serverless simple llamado LR1 que utiliza AWS Lambda y Serverless Framework con Python.

## Estructura del Proyecto

```
backend/
├── serverless.yml          # Configuración del Serverless Framework
├── requirements.txt        # Dependencias de Python
├── src/
│   └── handler.py         # Función Lambda principal
└── README.md              # Este archivo
```

## Características

- ✅ Servicio serverless con AWS Lambda
- ✅ Handler para métodos HTTP (GET, POST, PUT, DELETE)
- ✅ Configuración con Serverless Framework
- ✅ Soporte para desarrollo local con serverless-offline
- ✅ CORS habilitado
- ✅ Variables de entorno configurables

## Prerrequisitos

1. **Python** (versión 3.9 o superior)
2. **AWS CLI** configurado con credenciales
3. **Serverless Framework** instalado globalmente
4. **Docker** (para empaquetado de dependencias)

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Instalar Serverless Framework globalmente (si no está instalado):
```bash
npm install -g serverless
```

3. Instalar plugin de Python para Serverless:
```bash
npm install -g serverless-python-requirements
```

## Configuración AWS

Asegúrate de tener configuradas tus credenciales de AWS:

```bash
aws configure
```

O usando variables de entorno:
```bash
export AWS_ACCESS_KEY_ID=tu_access_key
export AWS_SECRET_ACCESS_KEY=tu_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## Desarrollo Local

Para ejecutar el servicio localmente (requiere serverless-offline):

```bash
serverless offline
```

El servicio estará disponible en: `http://localhost:3000`

## Despliegue

### Despliegue en desarrollo:
```bash
serverless deploy --stage dev
```

### Despliegue en producción:
```bash
serverless deploy --stage prod
```

### Despliegue genérico:
```bash
serverless deploy
```

## Endpoints Disponibles

Una vez desplegado, tendrás los siguientes endpoints:

- `GET /` - Endpoint principal
- `GET /lr1` - Endpoint específico del servicio LR1
- `POST /lr1` - Crear recursos
- `PUT /lr1` - Actualizar recursos
- `DELETE /lr1` - Eliminar recursos

## Comandos Útiles

```bash
# Ver logs en tiempo real
serverless logs -f lr1

# Invocar función directamente
serverless invoke -f lr1

# Eliminar el servicio completo
serverless remove

# Ver información del servicio
serverless info
```

## Variables de Entorno

El servicio utiliza las siguientes variables de entorno:

- `PYTHON_ENV`: Entorno de ejecución (dev/prod)
- `SERVICE_NAME`: Nombre del servicio
- `STAGE`: Etapa de despliegue
- `AWS_REGION`: Región de AWS

## Estructura de Respuesta

Todas las respuestas siguen el siguiente formato:

```json
{
  "message": "LR1 Service - [METHOD] request successful",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "service": "lr1-service",
  "stage": "dev"
}
```

## Personalización

Para personalizar el servicio:

1. Modifica `src/handler.py` para cambiar la lógica de negocio
2. Actualiza `serverless.yml` para cambiar la configuración de AWS
3. Ajusta `requirements.txt` para agregar nuevas dependencias de Python

## Troubleshooting

### Error de credenciales AWS:
```bash
aws configure list
```

### Error de permisos:
Verifica que tu usuario AWS tenga los permisos necesarios para Lambda, API Gateway y CloudFormation.

### Error de región:
Asegúrate de que la región especificada en `serverless.yml` sea válida y esté disponible.

### Error de dependencias Python:
Si tienes problemas con las dependencias, asegúrate de que Docker esté ejecutándose para el empaquetado automático.

### Error de runtime Python:
Verifica que tengas Python 3.9 instalado y que el runtime en `serverless.yml` coincida con tu versión local.
