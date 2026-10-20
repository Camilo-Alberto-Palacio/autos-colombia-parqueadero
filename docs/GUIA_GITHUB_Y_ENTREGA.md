# PARQUEADERO AUTOS COLOMBIA 24/7
## GUÍA DE PUBLICACIÓN EN GITHUB Y PROTOCOLO DE ENTREGA ACADÉMICA
### ITERACIÓN 1: CONTROL DE ENTRADA Y SALIDA
**Docente:** Reinaldo Rojas

---

## 1. PASOS PARA PUBLICAR EL PROYECTO EN GITHUB

Para cumplir con el requerimiento del docente de entregar el código fuente en un repositorio de GitHub público o compartido:

### Paso 1: Abrir Terminal en la Carpeta del Proyecto
Abre PowerShell o tu terminal en la ruta del proyecto:
```powershell
cd "$HOME\Documents\aplicacion de parqueo"
```

### Paso 2: Inicializar el Repositorio Local Git
Si aún no has inicializado Git en la carpeta:
```powershell
git init
```

### Paso 3: Agregar los Archivos y Realizar el Primer Commit
```powershell
git add .
git commit -m "Entrega Oficial Iteración 1: Control de Entrada y Salida Autos Colombia 24/7 - Docente Reinaldo Rojas"
```

### Paso 4: Crear el Repositorio en GitHub
1. Ingresa a [GitHub](https://github.com/) e inicia sesión.
2. Haz clic en **New repository** (+).
3. Nombre recomendado del repositorio: `autos-colombia-parqueadero` o `autos-colombia-iteracion1`.
4. Visibilidad: **Public** (Público) o **Private** (si es privado, recuerda agregar como colaborador la cuenta de GitHub del profesor Reinaldo Rojas).
5. **No** marques la opción de inicializar con README (ya tenemos el README completo en el proyecto).
6. Haz clic en **Create repository**.

### Paso 5: Vincular el Remoto y Subir el Código
Copia los comandos que te entrega GitHub (reemplazando tu usuario):
```powershell
git branch -M main
git remote add origin https://github.com/TU_USUARIO/autos-colombia-parqueadero.git
git push -u origin main
```

---

## 2. LISTA DE CHEQUEO DE ENTREGABLES (CHECKLIST DOCENTE)

Asegúrate de verificar cada uno de los 5 entregables exigidos por el docente antes de la entrega:

* [x] **1. Documentación Escrita Formal:**
  - Archivo: `docs/DOCUMENTACION_TECNICA_ITERACION_1.md`
  - Contenido: Portada, introducción, alcance exclusivo de Iteración 1, reglas de negocio, requerimientos funcionales (RF), requerimientos no funcionales (RNF) e historias de usuario (HU) en formato Gherkin.
  - *Tip:* Puedes abrir este archivo en VS Code o Typora y exportarlo directamente a formato PDF si el profesor lo solicita en formato `.pdf`.

* [x] **2. Modelado en StarUML:**
  - Archivos: `docs/MODELADO_STARUML_Y_ARQUITECTURA.md` y `docs/staruml_diagrams.puml`
  - Contenido: Arquitectura en capas, diagrama de casos de uso con actores, diagrama de clases del dominio con multiplicidades, diagrama de paquetes y diagramas de secuencia de entrada y salida.

* [x] **3. Base de Datos (MER, MR y SQL Físico):**
  - Documentación: `docs/BASE_DE_DATOS_MER_MR.md`
  - Script SQL Funcional: `database_schema.sql`
  - Base de Datos SQLite: `autos_colombia.db` (auto-generada al iniciar)
  - Celdas reglamentarias: Exactamente **80 celdas** (10 motos: `M-01` a `M-10` y 70 carros: `C-01` a `C-70`).
  - Clientes y vehículos de prueba pre-cargados (al día y vencidos para probar mora).

* [x] **4. Diseño Visual (Figma y Prototipo Stitch):**
  - Archivo de especificación: `docs/DISENO_VISUAL_FIGMA_Y_STITCH.md`
  - Archivos de diseño Stitch: Carpeta `stitch_parking_app_design/` con `DESIGN.md`, maquetas interactivas y capturas de alta definición para Figma.

* [x] **5. Código Fuente Funcional y Ejecutable:**
  - `app.py`: Servidor HTTP REST API nativo en Python (cero dependencias externas).
  - `models.py`: Lógica de negocio (asignación dinámica/aleatoria, validación de mensualidad, control de aforo).
  - `database.py`: Gestión de conexión SQLite y creación de tablas.
  - `static/`: Interfaz gráfica interactiva y mapa de 80 celdas en tiempo real.

---

## 3. CÓMO EJECUTAR LA APLICACIÓN (INSTRUCCIONES PARA EL PROFESOR)

En el documento de entrega o en el correo/plataforma para el profesor Reinaldo Rojas, puedes incluir estas instrucciones de ejecución rápida:

1. Clonar o descargar el repositorio.
2. Abrir una terminal en la carpeta del proyecto.
3. Ejecutar el servidor con Python:
   ```bash
   python app.py
   ```
4. Abrir cualquier navegador web e ingresar a:
   ```text
   http://localhost:8000
   ```
5. Realizar las pruebas interactivas con los botones rápidos:
   - Clic en `ABC-123` (Carro al día -> Autoriza ingreso y asigna celda aleatoria C-XX).
   - Clic en `MOT-808` (Moto al día -> Autoriza ingreso y asigna celda aleatoria M-XX).
   - Clic en `XYZ-999` (Carro con mensualidad vencida -> Deniega acceso bajo alerta de mora).
   - En la columna derecha, pulsar "Dar Salida" para liberar la celda inmediatamente.
   - Navegar a la pestaña "Mapa 80 Celdas" para ver en tiempo real la ocupación física del parqueadero.
