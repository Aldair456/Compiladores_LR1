# 🚀 Mi Proyecto Vercel

Un proyecto moderno construido con Next.js, TypeScript y Tailwind CSS, optimizado para desplegarse en Vercel.

## ✨ Características

- ⚡ **Next.js 14** - Framework React de última generación
- 🎨 **Tailwind CSS** - Estilos modernos con glassmorphism
- 📱 **Responsive Design** - Adaptable a todos los dispositivos
- 🔧 **TypeScript** - Tipado estático para mejor desarrollo
- 🚀 **Vercel Ready** - Configurado para deploy automático

## 🛠️ Stack Tecnológico

- **Frontend**: Next.js, React, TypeScript
- **Styling**: Tailwind CSS
- **Deployment**: Vercel
- **Linting**: ESLint

## 🚀 Instalación y Desarrollo

### Prerrequisitos

- Node.js 18+ 
- npm o yarn

### Pasos para ejecutar localmente

1. **Instalar dependencias**
   ```bash
   npm install
   ```

2. **Ejecutar en modo desarrollo**
   ```bash
   npm run dev
   ```

3. **Abrir en el navegador**
   ```
   http://localhost:3000
   ```

### Scripts disponibles

- `npm run dev` - Ejecuta el servidor de desarrollo
- `npm run build` - Construye la aplicación para producción
- `npm run start` - Ejecuta la aplicación en modo producción
- `npm run lint` - Ejecuta el linter

## 🌐 Despliegue en Vercel

### Opción 1: Deploy automático con Git

1. **Conectar repositorio**
   - Sube tu código a GitHub, GitLab o Bitbucket
   - Ve a [vercel.com](https://vercel.com)
   - Conecta tu repositorio

2. **Deploy automático**
   - Vercel detectará automáticamente que es un proyecto Next.js
   - El deploy se realizará automáticamente en cada push

### Opción 2: Deploy manual

1. **Instalar Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Hacer login**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```

## 📁 Estructura del Proyecto

```
├── app/
│   ├── globals.css      # Estilos globales con Tailwind
│   ├── layout.tsx      # Layout principal
│   └── page.tsx        # Página de inicio
├── public/             # Archivos estáticos
├── package.json        # Dependencias y scripts
├── tailwind.config.js  # Configuración de Tailwind
├── tsconfig.json       # Configuración de TypeScript
├── vercel.json         # Configuración de Vercel
└── README.md          # Este archivo
```

## 🎨 Personalización

### Cambiar colores
Edita `tailwind.config.js` para personalizar la paleta de colores:

```javascript
theme: {
  extend: {
    colors: {
      primary: '#667eea',
      secondary: '#764ba2',
    }
  }
}
```

### Agregar páginas
Crea nuevos archivos en la carpeta `app/`:
- `app/about/page.tsx` → `/about`
- `app/contact/page.tsx` → `/contact`

### Modificar estilos
Los estilos personalizados están en `app/globals.css` con clases como:
- `.gradient-text` - Texto con gradiente
- `.card` - Tarjetas con efecto glassmorphism
- `.btn-primary` - Botones con gradiente

## 🔧 Configuración Adicional

### Variables de entorno
Crea un archivo `.env.local` para variables locales:

```env
NEXT_PUBLIC_API_URL=https://api.ejemplo.com
```

### Dominio personalizado
En Vercel Dashboard:
1. Ve a tu proyecto
2. Settings → Domains
3. Agrega tu dominio personalizado

## 📚 Recursos Útiles

- [Documentación de Next.js](https://nextjs.org/docs)
- [Documentación de Tailwind CSS](https://tailwindcss.com/docs)
- [Documentación de Vercel](https://vercel.com/docs)
- [Guía de TypeScript](https://www.typescriptlang.org/docs)

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

¡Construido con ❤️ para Vercel!
