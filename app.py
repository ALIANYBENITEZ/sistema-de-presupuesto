"""
Vielma Moto-Repuestos - Sistema de Presupuestos para Autos y Motos.
Aplicación principal Flask.
"""

from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify
from datetime import datetime
import os

from pdf.presupuesto import generar_pdf, formatear_guaranies

app = Flask(__name__)
# En producción (PythonAnywhere) la clave se toma de la variable de entorno
# SECRET_KEY. En local usa un valor por defecto para no requerir configuración.
app.secret_key = os.environ.get('SECRET_KEY', 'vielma-moto-repuestos-2026-clave-fija')
app.config['SESSION_COOKIE_NAME'] = 'vielma_session'


def obtener_siguiente_numero():
    """
    Genera el siguiente número de presupuesto.
    Utiliza un archivo de texto simple como contador persistente.
    """
    contador_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'contador.txt')

    if os.path.exists(contador_path):
        with open(contador_path, 'r') as f:
            contenido = f.read().strip()
            numero = int(contenido) if contenido else 0
    else:
        numero = 0

    numero += 1

    with open(contador_path, 'w') as f:
        f.write(str(numero))

    return f"PRES-{numero:06d}"


def validar_vehiculo(datos):
    """Valida los datos del vehículo. Retorna lista de errores."""
    errores = []

    tipo_vehiculo = datos.get('tipo_vehiculo', '').strip()
    marca = datos.get('marca', '').strip()
    modelo = datos.get('modelo', '').strip()
    color = datos.get('color', '').strip()
    anio = datos.get('anio', '').strip()

    if not tipo_vehiculo or tipo_vehiculo not in ('Moto', 'Auto', 'Camioneta', 'Otro'):
        errores.append("Debe seleccionar el tipo de vehículo.")
    if not marca:
        errores.append("La marca del vehículo es obligatoria.")
    if not modelo:
        errores.append("El modelo del vehículo es obligatorio.")
    if anio:
        try:
            anio_int = int(anio)
            if anio_int < 1900 or anio_int > datetime.now().year + 2:
                errores.append("El año del vehículo no es válido.")
        except ValueError:
            errores.append("El año del vehículo debe ser un número válido.")

    return errores


def validar_repuestos(repuestos):
    """Valida la lista de repuestos. Retorna lista de errores."""
    errores = []

    if not repuestos:
        errores.append("Debe agregar al menos un repuesto.")
        return errores

    for i, repuesto in enumerate(repuestos, 1):
        desc = repuesto.get('descripcion', '').strip()
        valor = repuesto.get('valor_unitario', '').strip()
        cantidad = repuesto.get('cantidad', '').strip()

        if not desc:
            errores.append(f"La descripción del repuesto #{i} es obligatoria.")

        if not valor:
            errores.append(f"El valor del repuesto #{i} es obligatorio.")
        else:
            try:
                valor_num = int(valor)
                if valor_num <= 0:
                    errores.append(f"El valor del repuesto #{i} debe ser mayor a 0.")
            except (ValueError, TypeError):
                errores.append(f"El valor del repuesto #{i} debe ser un número válido.")

        if not cantidad:
            errores.append(f"La cantidad del repuesto #{i} es obligatoria.")
        else:
            try:
                cant_num = int(cantidad)
                if cant_num <= 0:
                    errores.append(f"La cantidad del repuesto #{i} debe ser mayor a 0.")
            except (ValueError, TypeError):
                errores.append(f"La cantidad del repuesto #{i} debe ser un número entero.")

    return errores


def obtener_repuestos_de_session():
    """Obtiene la lista de repuestos almacenados en la sesión."""
    return session.get('repuestos', [])


def guardar_repuestos_en_session(repuestos):
    """Guarda la lista de repuestos en la sesión."""
    session['repuestos'] = repuestos


def calcular_total(repuestos):
    """Calcula el total de todos los repuestos."""
    total = 0
    for repuesto in repuestos:
        try:
            valor = int(repuesto.get('valor_unitario', 0))
            cantidad = int(repuesto.get('cantidad', 0))
            total += valor * cantidad
        except (ValueError, TypeError):
            pass
    return total


def extraer_datos_formulario(form_data):
    """
    Extrae datos del vehículo y repuestos del formulario.
    Maneja tanto los inputs desktop (repuesto_desc_0) como mobile (repuesto_desc_m_0).
    En mobile CSS oculta los desktop, pero ambos se envían. Priorizamos desktop,
    y si están vacíos intentamos mobile.
    """
    vehiculo = {
        'tipo_vehiculo': form_data.get('tipo_vehiculo', '').strip(),
        'marca': form_data.get('marca', '').strip(),
        'modelo': form_data.get('modelo', '').strip(),
        'color': form_data.get('color', '').strip(),
        'anio': form_data.get('anio', '').strip()
    }

    repuestos = []
    indice = 0

    while True:
        desc_key = f'repuesto_desc_{indice}'
        valor_key = f'repuesto_valor_{indice}'
        cant_key = f'repuesto_cant_{indice}'

        desc_key_m = f'repuesto_desc_m_{indice}'
        valor_key_m = f'repuesto_valor_m_{indice}'
        cant_key_m = f'repuesto_cant_m_{indice}'

        # Verificar si existe este índice en alguna de las dos vistas
        if desc_key not in form_data and desc_key_m not in form_data:
            break

        # Obtener valores de desktop
        desc = form_data.get(desc_key, '').strip()
        valor = form_data.get(valor_key, '').strip()
        cant = form_data.get(cant_key, '').strip()

        # Si desktop está vacío, intentar mobile
        desc_m = form_data.get(desc_key_m, '').strip()
        valor_m = form_data.get(valor_key_m, '').strip()
        cant_m = form_data.get(cant_key_m, '').strip()

        # Usar el que tenga contenido (priorizar el que esté lleno)
        final_desc = desc if desc else desc_m
        final_valor = valor if valor else valor_m
        final_cant = cant if cant else cant_m

        repuestos.append({
            'descripcion': final_desc,
            'valor_unitario': final_valor,
            'cantidad': final_cant if final_cant else '1'
        })
        indice += 1

    return vehiculo, repuestos


@app.route('/', methods=['GET'])
def index():
    """Página principal con el formulario de presupuesto."""
    repuestos = obtener_repuestos_de_session()
    errores = session.pop('errores', [])
    exito = session.pop('exito', None)

    # Datos del vehículo guardados en sesión
    vehiculo = session.get('vehiculo', {})

    # Calcular subtotales y total
    for repuesto in repuestos:
        try:
            valor = int(repuesto.get('valor_unitario', 0) or 0)
            cantidad = int(repuesto.get('cantidad', 0) or 0)
            repuesto['subtotal'] = valor * cantidad
            repuesto['subtotal_fmt'] = formatear_guaranies(valor * cantidad)
            repuesto['valor_fmt'] = formatear_guaranies(valor)
        except (ValueError, TypeError):
            repuesto['subtotal'] = 0
            repuesto['subtotal_fmt'] = "Gs. 0"
            repuesto['valor_fmt'] = "Gs. 0"

    total = calcular_total(repuestos)
    total_fmt = formatear_guaranies(total)

    return render_template(
        'index.html',
        repuestos=repuestos,
        vehiculo=vehiculo,
        total=total,
        total_fmt=total_fmt,
        errores=errores,
        exito=exito
    )


@app.route('/agregar-repuesto', methods=['POST'])
def agregar_repuesto():
    """Agrega un repuesto con los datos ingresados en los campos dedicados."""
    # Guardar datos del vehículo
    vehiculo = {
        'tipo_vehiculo': request.form.get('tipo_vehiculo', '').strip(),
        'marca': request.form.get('marca', '').strip(),
        'modelo': request.form.get('modelo', '').strip(),
        'color': request.form.get('color', '').strip(),
        'anio': request.form.get('anio', '').strip()
    }
    session['vehiculo'] = vehiculo

    # Recuperar repuestos existentes desde hidden inputs
    repuestos = []
    indice = 0
    while True:
        desc_key = f'repuesto_desc_{indice}'
        if desc_key not in request.form:
            break
        repuestos.append({
            'descripcion': request.form.get(desc_key, '').strip(),
            'valor_unitario': request.form.get(f'repuesto_valor_{indice}', '').strip(),
            'cantidad': request.form.get(f'repuesto_cant_{indice}', '').strip()
        })
        indice += 1

    # Obtener datos del nuevo repuesto
    nuevo_desc = request.form.get('nuevo_desc', '').strip()
    nuevo_valor = request.form.get('nuevo_valor', '').strip()
    nuevo_cant = request.form.get('nuevo_cant', '').strip()

    # Validar nuevo repuesto
    errores = []
    if not nuevo_desc:
        errores.append("La descripción del repuesto es obligatoria.")
    if not nuevo_valor:
        errores.append("El valor del repuesto es obligatorio.")
    else:
        try:
            val = int(nuevo_valor)
            if val <= 0:
                errores.append("El valor del repuesto debe ser mayor a 0.")
        except ValueError:
            errores.append("El valor del repuesto debe ser un número válido.")
    if not nuevo_cant:
        nuevo_cant = '1'
    else:
        try:
            cant = int(nuevo_cant)
            if cant <= 0:
                errores.append("La cantidad debe ser mayor a 0.")
        except ValueError:
            errores.append("La cantidad debe ser un número entero.")

    if errores:
        session['errores'] = errores
        guardar_repuestos_en_session(repuestos)
        return redirect(url_for('index'))

    # Agregar el nuevo repuesto
    repuestos.append({
        'descripcion': nuevo_desc,
        'valor_unitario': nuevo_valor,
        'cantidad': nuevo_cant
    })
    guardar_repuestos_en_session(repuestos)

    return redirect(url_for('index'))


@app.route('/eliminar-repuesto', methods=['POST'])
def eliminar_repuesto_accion():
    """Elimina un repuesto por su índice (recibido como valor del botón)."""
    # Guardar datos del vehículo
    vehiculo = {
        'tipo_vehiculo': request.form.get('tipo_vehiculo', '').strip(),
        'marca': request.form.get('marca', '').strip(),
        'modelo': request.form.get('modelo', '').strip(),
        'color': request.form.get('color', '').strip(),
        'anio': request.form.get('anio', '').strip()
    }
    session['vehiculo'] = vehiculo

    # Recuperar repuestos existentes desde hidden inputs
    repuestos = []
    indice = 0
    while True:
        desc_key = f'repuesto_desc_{indice}'
        if desc_key not in request.form:
            break
        repuestos.append({
            'descripcion': request.form.get(desc_key, '').strip(),
            'valor_unitario': request.form.get(f'repuesto_valor_{indice}', '').strip(),
            'cantidad': request.form.get(f'repuesto_cant_{indice}', '').strip()
        })
        indice += 1

    # Eliminar el repuesto indicado
    indice_str = request.form.get('eliminar', '')
    try:
        indice_eliminar = int(indice_str)
        if 0 <= indice_eliminar < len(repuestos):
            repuestos.pop(indice_eliminar)
    except (ValueError, TypeError):
        pass

    guardar_repuestos_en_session(repuestos)

    return redirect(url_for('index'))


@app.route('/generar-pdf', methods=['POST'])
def generar_presupuesto_pdf():
    """Valida los datos y genera el PDF del presupuesto.

    Soporta dos modos:
      - Descarga directa (por defecto): responde el archivo PDF como adjunto.
      - Modo compartir (?modo=compartir): igual, pero pensado para consumirse
        vía fetch desde el navegador para usar la API nativa de compartir.

    El nombre de archivo del presupuesto se envía en la cabecera
    'X-Numero-Presupuesto' para que el frontend pueda nombrar el archivo.
    """
    # Guardar datos del vehículo
    vehiculo = {
        'tipo_vehiculo': request.form.get('tipo_vehiculo', '').strip(),
        'marca': request.form.get('marca', '').strip(),
        'modelo': request.form.get('modelo', '').strip(),
        'color': request.form.get('color', '').strip(),
        'anio': request.form.get('anio', '').strip()
    }
    session['vehiculo'] = vehiculo

    # Recuperar repuestos desde hidden inputs
    repuestos = []
    indice = 0
    while True:
        desc_key = f'repuesto_desc_{indice}'
        if desc_key not in request.form:
            break
        repuestos.append({
            'descripcion': request.form.get(desc_key, '').strip(),
            'valor_unitario': request.form.get(f'repuesto_valor_{indice}', '').strip(),
            'cantidad': request.form.get(f'repuesto_cant_{indice}', '').strip()
        })
        indice += 1

    guardar_repuestos_en_session(repuestos)

    # Validar
    errores = []
    errores.extend(validar_vehiculo(vehiculo))
    errores.extend(validar_repuestos(repuestos))

    # Si la petición viene por fetch (modo compartir/descarga JS), devolvemos
    # los errores como JSON con código 422 para mostrarlos sin recargar.
    es_fetch = request.args.get('ajax') == '1'

    if errores:
        if es_fetch:
            return jsonify({'ok': False, 'errores': errores}), 422
        session['errores'] = errores
        return redirect(url_for('index'))

    # Calcular subtotales
    for repuesto in repuestos:
        valor = int(repuesto['valor_unitario'])
        cantidad = int(repuesto['cantidad'])
        repuesto['subtotal'] = valor * cantidad

    total = calcular_total(repuestos)

    # Generar número y fecha
    numero = obtener_siguiente_numero()
    fecha = datetime.now().strftime('%d/%m/%Y')

    # Datos para el PDF
    datos_pdf = {
        'numero': numero,
        'fecha': fecha,
        'tipo_vehiculo': vehiculo.get('tipo_vehiculo', ''),
        'marca': vehiculo.get('marca', ''),
        'modelo': vehiculo.get('modelo', ''),
        'color': vehiculo.get('color', ''),
        'anio': vehiculo.get('anio', ''),
        'repuestos': repuestos,
        'total': total
    }

    # Generar PDF
    pdf_buffer = generar_pdf(datos_pdf)

    nombre_archivo = f'presupuesto_{numero}.pdf'

    # Crear respuesta con el PDF como descarga
    response = make_response(pdf_buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={nombre_archivo}'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    # Exponer el número para que el frontend pueda armar el nombre/mensaje
    response.headers['X-Numero-Presupuesto'] = numero
    response.headers['Access-Control-Expose-Headers'] = 'X-Numero-Presupuesto'

    return response


@app.route('/limpiar', methods=['POST'])
def limpiar():
    """Limpia el formulario completo."""
    session.pop('repuestos', None)
    session.pop('vehiculo', None)
    session.pop('errores', None)
    session.pop('exito', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Intentar arrancar en HTTPS (necesario para compartir archivos por
    # WhatsApp desde los celulares vía navigator.share). Si no se puede
    # generar el certificado, se cae con seguridad a HTTP.
    contexto_ssl = None
    puerto = 443

    try:
        from certificado import generar_certificado, obtener_ip_local

        cert_path, key_path = generar_certificado()
        contexto_ssl = (cert_path, key_path)
        ip_local = obtener_ip_local()

        print('=' * 50)
        print('  VIELMA MOTO-REPUESTOS - Sistema de Presupuestos')
        print('=' * 50)
        print('  Modo seguro HTTPS activado.')
        print('  Acceder desde esta PC:')
        print('    https://localhost')
        print('    https://vielma-presupuestos.com')
        print('  Acceder desde celular/tablet (misma red WiFi):')
        print(f'    https://{ip_local}')
        print('  La primera vez el navegador mostrará una advertencia de')
        print('  seguridad: elegí "Avanzado" y "Continuar al sitio".')
        print('=' * 50)
    except Exception as e:
        # Fallback a HTTP si falta 'cryptography' o falla la generación.
        contexto_ssl = None
        puerto = 80
        print('=' * 50)
        print('  AVISO: No se pudo activar HTTPS.')
        print(f'  Motivo: {e}')
        print('  El sistema arrancará en HTTP (puerto 80).')
        print('  Para habilitar el compartir directo por WhatsApp desde')
        print('  los celulares, instalá la dependencia con:')
        print('    pip install cryptography')
        print('=' * 50)

    app.run(debug=False, host='0.0.0.0', port=puerto, ssl_context=contexto_ssl)
