"""
Generación de certificado HTTPS autofirmado para uso en red local.

El certificado permite que el navegador de los celulares/tablets del taller
habilite la API nativa de compartir (navigator.share con archivos), que solo
funciona en contextos seguros (HTTPS o localhost).

El certificado se genera UNA sola vez y dura 10 años. Incluye en el campo SAN
(Subject Alternative Name):
  - localhost y 127.0.0.1
  - vielma-presupuestos.com
  - la IP local detectada de la PC

Como es autofirmado, la primera vez cada dispositivo mostrará una advertencia
de seguridad. Hay que aceptarla una sola vez (en Chrome/Edge: "Avanzado" ->
"Continuar al sitio").
"""

import os
import socket
import datetime
import ipaddress

CARPETA_BASE = os.path.dirname(os.path.abspath(__file__))
CERT_PATH = os.path.join(CARPETA_BASE, 'cert.pem')
KEY_PATH = os.path.join(CARPETA_BASE, 'key.pem')


def obtener_ip_local():
    """Detecta la IP local de la PC en la red WiFi/LAN."""
    try:
        # Truco: abrir un socket UDP hacia una IP externa no envía datos,
        # pero deja ver qué interfaz/IP usaría el sistema operativo.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def certificado_existe():
    """Indica si ya hay un certificado y clave generados."""
    return os.path.exists(CERT_PATH) and os.path.exists(KEY_PATH)


def generar_certificado(forzar=False):
    """
    Genera cert.pem y key.pem autofirmados si no existen.

    Args:
        forzar: si es True, regenera el certificado aunque ya exista
                (útil si cambió la IP de la PC).

    Returns:
        (cert_path, key_path)
    """
    if certificado_existe() and not forzar:
        return CERT_PATH, KEY_PATH

    # Import diferido para que la app pueda arrancar en HTTP aunque falte
    # la librería 'cryptography'.
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    ip_local = obtener_ip_local()

    # Clave privada RSA 2048
    clave = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    nombre = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, 'PY'),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Vielma Moto-Repuestos'),
        x509.NameAttribute(NameOID.COMMON_NAME, 'vielma-presupuestos.com'),
    ])

    # Nombres alternativos: dominios e IPs por los que se accede al sistema
    sans = [
        x509.DNSName('localhost'),
        x509.DNSName('vielma-presupuestos.com'),
        x509.IPAddress(ipaddress.ip_address('127.0.0.1')),
    ]
    try:
        sans.append(x509.IPAddress(ipaddress.ip_address(ip_local)))
    except ValueError:
        pass

    try:
        ahora = datetime.datetime.now(datetime.UTC)
    except AttributeError:
        # Python < 3.11 no tiene datetime.UTC
        ahora = datetime.datetime.now(datetime.timezone.utc)

    certificado = (
        x509.CertificateBuilder()
        .subject_name(nombre)
        .issuer_name(nombre)
        .public_key(clave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(ahora - datetime.timedelta(days=1))
        .not_valid_after(ahora + datetime.timedelta(days=3650))  # 10 años
        .add_extension(x509.SubjectAlternativeName(sans), critical=False)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(clave, hashes.SHA256())
    )

    # Guardar clave privada
    with open(KEY_PATH, 'wb') as f:
        f.write(clave.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    # Guardar certificado
    with open(CERT_PATH, 'wb') as f:
        f.write(certificado.public_bytes(serialization.Encoding.PEM))

    return CERT_PATH, KEY_PATH


if __name__ == '__main__':
    print('Detectando IP local...')
    ip = obtener_ip_local()
    print(f'IP local: {ip}')
    print('Generando certificado autofirmado (10 años)...')
    cert, key = generar_certificado(forzar=True)
    print('Certificado generado:')
    print(f'  {cert}')
    print(f'  {key}')
    print('Listo. Ahora el sistema puede arrancar en HTTPS.')
