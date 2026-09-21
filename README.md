# Vielma Moto-Repuestos — Sistema de Presupuestos

Sistema web para generar presupuestos profesionales en PDF para el taller Vielma Moto-Repuestos.
Funciona con autos, motos, camionetas y otros vehículos livianos.

---

## Instalación en una PC nueva (paso a paso)

### 1. Instalar Python

1. Descargar Python desde: https://www.python.org/downloads/
2. Ejecutar el instalador
3. **MUY IMPORTANTE:** En la primera pantalla, marcar la casilla:

   ✅ **Add Python to PATH**

   (Si no marcás esto, nada va a funcionar)

4. Clic en "Install Now"
5. Esperar a que termine y cerrar

> Con marcar "Add Python to PATH" durante la instalación es suficiente.
> No hace falta agregar variables de entorno manualmente.

---

### 2. Copiar la carpeta del sistema

Copiar toda la carpeta `vielma-moto-repuestos` a:

```
C:\vielma-moto-repuestos
```

**IMPORTANTE:** Si existe una carpeta `venv` dentro, eliminarla antes de copiar.
La vamos a crear nueva en el paso siguiente.

---

### 3. Instalar dependencias (solo una vez)

Abrir PowerShell (clic derecho en menú Inicio → Windows PowerShell) y ejecutar:

```powershell
cd C:\vielma-moto-repuestos
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Si aparece un error "no se puede ejecutar scripts", ejecutar primero:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Responder "S" (Sí) y repetir los comandos anteriores.

---

### 4. Probar que funciona

Con la terminal abierta:

```powershell
python app.py
```

Abrir el navegador en: http://127.0.0.1:5000

Si ves el sistema de presupuestos, todo está correcto. Presionar `Ctrl+C` para detener.

---

### 5. Inicio automático con Windows

El archivo `iniciar-presupuestos.bat` ya viene incluido en la carpeta.
Solo hay que crear un acceso directo en el Inicio de Windows:

1. Presionar `Windows + R`
2. Escribir: `shell:startup`
3. Presionar Enter (se abre una carpeta)
4. Clic derecho → Nuevo → Acceso directo
5. Ubicación del elemento: `C:\vielma-moto-repuestos\iniciar-presupuestos.bat`
6. Nombre: `Vielma Presupuestos`
7. Finalizar

**Resultado:** Cada vez que se encienda la PC:
- Se abre una ventana negra (terminal) — NO CERRARLA
- Se abre el navegador con el sistema automáticamente

---

### 6. Acceso directo en el escritorio (opcional)

1. Clic derecho en el Escritorio → Nuevo → Acceso directo
2. Ubicación: `C:\vielma-moto-repuestos\iniciar-presupuestos.bat`
3. Nombre: `Vielma Presupuestos`

---

## Uso diario

- Encender la PC → el sistema arranca solo
- Si no se abrió el navegador, ir a: http://127.0.0.1:5000
- **NO cerrar la ventana negra** mientras se use el sistema
- Para apagar: cerrar la ventana negra o presionar Ctrl+C

---

## Cómo generar un presupuesto

1. Seleccionar el tipo de vehículo (Moto, Auto, Camioneta, Otro)
2. Completar marca y modelo (color y año son opcionales)
3. Agregar repuestos con descripción, valor y cantidad
4. Verificar el total
5. Clic en "Generar presupuesto PDF"
6. Se descarga el PDF listo para imprimir

---

## Solución de problemas

| Problema | Solución |
|----------|----------|
| `python no se reconoce` | Reinstalar Python marcando "Add to PATH". Cerrar y abrir la terminal. |
| `no se puede ejecutar scripts` | Ejecutar: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| El navegador dice "no se puede acceder" | Verificar que la ventana negra esté abierta |
| La terminal se cierra sola | Abrir PowerShell manual y ejecutar los comandos uno por uno para ver el error |

---

## Datos técnicos

- **Tecnología:** Python + Flask + ReportLab
- **Puerto:** 5000
- **Dirección local:** http://127.0.0.1:5000
- **Python requerido:** 3.10 o superior
- **Dependencias:** Flask, ReportLab (se instalan con pip)

---

## Resumen rápido

```
1. Instalar Python (marcar "Add to PATH")
2. Copiar carpeta a C:\vielma-moto-repuestos
3. Abrir PowerShell:
   cd C:\vielma-moto-repuestos
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
4. Doble clic en iniciar-presupuestos.bat → listo
5. Poner acceso directo en shell:startup para inicio automático
```
