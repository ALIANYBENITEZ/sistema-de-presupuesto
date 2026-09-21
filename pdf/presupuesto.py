"""
Módulo de generación de PDF para presupuestos.
Utiliza ReportLab para crear documentos PDF profesionales tamaño A4.
"""

from io import BytesIO
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
)
from reportlab.lib import colors


# Datos del negocio
NOMBRE_NEGOCIO = "VIELMA MOTO-REPUESTOS"
DIRECCION_LINEA1 = "Oceanía, casi Sapirangy"
DIRECCION_LINEA2 = "Barrio 8 de Diciembre, Villa Elisa"
PROPIETARIO = "Propietario: Christian Vielma"

# Colores del tema
COLOR_PRIMARIO = HexColor("#1a237e")
COLOR_SECUNDARIO = HexColor("#283593")
COLOR_ACENTO = HexColor("#0d47a1")
COLOR_GRIS_CLARO = HexColor("#f5f5f5")
COLOR_GRIS = HexColor("#e0e0e0")
COLOR_TEXTO = HexColor("#212121")


def formatear_guaranies(valor):
    """Formatea un número como guaraníes paraguayos."""
    valor_int = int(valor)
    texto = f"{valor_int:,}".replace(",", ".")
    return f"Gs. {texto}"


def generar_pdf(datos):
    """
    Genera un PDF de presupuesto profesional.
    
    Args:
        datos: diccionario con claves:
            - numero: str (ej: "PRES-000001")
            - fecha: str (ej: "17/08/2026")
            - tipo_vehiculo: str
            - marca: str
            - modelo: str
            - color: str
            - anio: str
            - repuestos: lista de dicts con {descripcion, valor_unitario, cantidad, subtotal}
            - total: int
    
    Returns:
        BytesIO con el contenido del PDF
    """
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=2 * cm
    )
    
    elements = []
    width_disponible = A4[0] - 4 * cm
    
    # --- Estilos ---
    styles = getSampleStyleSheet()
    
    estilo_titulo = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=COLOR_PRIMARIO,
        alignment=TA_CENTER,
        spaceAfter=2 * mm
    )
    
    estilo_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=COLOR_SECUNDARIO,
        alignment=TA_CENTER,
        spaceAfter=1 * mm
    )
    
    estilo_seccion = ParagraphStyle(
        'Seccion',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=COLOR_PRIMARIO,
        spaceBefore=6 * mm,
        spaceAfter=3 * mm
    )
    
    estilo_normal = ParagraphStyle(
        'NormalCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=COLOR_TEXTO
    )
    
    estilo_pie = ParagraphStyle(
        'Pie',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        textColor=COLOR_SECUNDARIO,
        alignment=TA_CENTER,
        spaceBefore=10 * mm
    )
    
    estilo_pie_dir = ParagraphStyle(
        'PieDir',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=HexColor("#757575"),
        alignment=TA_CENTER,
        spaceBefore=2 * mm
    )
    
    # --- Encabezado con logo ---
    # Intentar cargar el logo
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'img', 'logo.png')
    
    if os.path.exists(logo_path):
        # Encabezado con logo a la derecha
        logo_img = Image(logo_path, width=22 * mm, height=22 * mm)
        logo_img.hAlign = 'RIGHT'
        
        header_texto = [
            [
                Paragraph(NOMBRE_NEGOCIO, estilo_titulo),
                logo_img
            ],
        ]
        header_table = Table(header_texto, colWidths=[width_disponible - 26 * mm, 26 * mm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        elements.append(header_table)
    else:
        elements.append(Paragraph(NOMBRE_NEGOCIO, estilo_titulo))
    
    elements.append(Paragraph(DIRECCION_LINEA1, estilo_subtitulo))
    elements.append(Paragraph(DIRECCION_LINEA2, estilo_subtitulo))
    elements.append(Paragraph(PROPIETARIO, estilo_subtitulo))
    elements.append(Spacer(1, 4 * mm))
    
    # Línea separadora
    linea_data = [['', '']]
    linea_table = Table(linea_data, colWidths=[width_disponible])
    linea_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 2, COLOR_PRIMARIO),
    ]))
    elements.append(linea_table)
    elements.append(Spacer(1, 4 * mm))
    
    # --- Datos del presupuesto ---
    estilo_pres_titulo = ParagraphStyle(
        'PresTitulo',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=COLOR_ACENTO,
        alignment=TA_CENTER,
        spaceAfter=3 * mm
    )
    elements.append(Paragraph("PRESUPUESTO", estilo_pres_titulo))
    
    # Número y fecha en tabla
    info_data = [
        [
            Paragraph(f"<b>Número:</b> {datos['numero']}", estilo_normal),
            Paragraph(f"<b>Fecha:</b> {datos['fecha']}", estilo_normal)
        ]
    ]
    info_table = Table(info_data, colWidths=[width_disponible / 2, width_disponible / 2])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2 * mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2 * mm),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 4 * mm))
    
    # --- Datos del vehículo ---
    elements.append(Paragraph("DATOS DEL VEHÍCULO", estilo_seccion))
    
    vehiculo_data = [
        [Paragraph("<b>Tipo:</b>", estilo_normal), Paragraph(datos['tipo_vehiculo'], estilo_normal),
         Paragraph("<b>Marca:</b>", estilo_normal), Paragraph(datos['marca'], estilo_normal)],
        [Paragraph("<b>Modelo:</b>", estilo_normal), Paragraph(datos['modelo'], estilo_normal),
         Paragraph("<b>Color:</b>", estilo_normal), Paragraph(datos['color'], estilo_normal)],
        [Paragraph("<b>Año:</b>", estilo_normal), Paragraph(datos['anio'], estilo_normal),
         '', ''],
    ]
    
    col_w = width_disponible / 4
    vehiculo_table = Table(vehiculo_data, colWidths=[col_w * 0.6, col_w * 1.4, col_w * 0.6, col_w * 1.4])
    vehiculo_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2 * mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2 * mm),
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_GRIS_CLARO),
        ('BOX', (0, 0), (-1, -1), 0.5, COLOR_GRIS),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, COLOR_GRIS),
    ]))
    elements.append(vehiculo_table)
    elements.append(Spacer(1, 6 * mm))
    
    # --- Tabla de repuestos ---
    elements.append(Paragraph("REPUESTOS", estilo_seccion))
    
    # Encabezados de la tabla
    estilo_header = ParagraphStyle(
        'HeaderTabla',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=white,
        alignment=TA_CENTER
    )
    
    estilo_celda = ParagraphStyle(
        'CeldaTabla',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=COLOR_TEXTO,
        alignment=TA_CENTER
    )
    
    estilo_celda_izq = ParagraphStyle(
        'CeldaTablaIzq',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=COLOR_TEXTO,
        alignment=TA_LEFT
    )
    
    estilo_celda_der = ParagraphStyle(
        'CeldaTableDer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=COLOR_TEXTO,
        alignment=TA_RIGHT
    )
    
    tabla_data = [
        [
            Paragraph("Cant.", estilo_header),
            Paragraph("Descripción", estilo_header),
            Paragraph("Valor Unitario", estilo_header),
            Paragraph("Subtotal", estilo_header)
        ]
    ]
    
    for repuesto in datos['repuestos']:
        fila = [
            Paragraph(str(repuesto['cantidad']), estilo_celda),
            Paragraph(repuesto['descripcion'], estilo_celda_izq),
            Paragraph(formatear_guaranies(repuesto['valor_unitario']), estilo_celda_der),
            Paragraph(formatear_guaranies(repuesto['subtotal']), estilo_celda_der)
        ]
        tabla_data.append(fila)
    
    col_widths = [
        width_disponible * 0.10,
        width_disponible * 0.40,
        width_disponible * 0.25,
        width_disponible * 0.25
    ]
    
    tabla_repuestos = Table(tabla_data, colWidths=col_widths)
    
    estilo_tabla = [
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARIO),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3 * mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3 * mm),
        ('LEFTPADDING', (0, 0), (-1, -1), 2 * mm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2 * mm),
        # Bordes
        ('BOX', (0, 0), (-1, -1), 1, COLOR_PRIMARIO),
        ('LINEBELOW', (0, 0), (-1, 0), 1, COLOR_PRIMARIO),
        ('INNERGRID', (0, 1), (-1, -1), 0.5, COLOR_GRIS),
    ]
    
    # Filas alternadas
    for i in range(1, len(tabla_data)):
        if i % 2 == 0:
            estilo_tabla.append(('BACKGROUND', (0, i), (-1, i), COLOR_GRIS_CLARO))
    
    tabla_repuestos.setStyle(TableStyle(estilo_tabla))
    elements.append(tabla_repuestos)
    elements.append(Spacer(1, 4 * mm))
    
    # --- Total ---
    estilo_total = ParagraphStyle(
        'Total',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=COLOR_PRIMARIO,
        alignment=TA_RIGHT
    )
    
    total_data = [
        ['', Paragraph(f"<b>TOTAL: {formatear_guaranies(datos['total'])}</b>", estilo_total)]
    ]
    total_table = Table(total_data, colWidths=[width_disponible * 0.5, width_disponible * 0.5])
    total_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3 * mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3 * mm),
        ('LINEABOVE', (0, 0), (-1, 0), 1.5, COLOR_PRIMARIO),
    ]))
    elements.append(total_table)
    
    # --- Pie ---
    elements.append(Spacer(1, 15 * mm))
    
    # Línea separadora del pie
    linea_pie = Table([['', '']], colWidths=[width_disponible])
    linea_pie.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, COLOR_GRIS),
    ]))
    elements.append(linea_pie)
    
    elements.append(Paragraph(
        "Gracias por confiar en Vielma Moto-Repuestos.",
        estilo_pie
    ))
    elements.append(Paragraph(
        f"{DIRECCION_LINEA1} - {DIRECCION_LINEA2}",
        estilo_pie_dir
    ))
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
