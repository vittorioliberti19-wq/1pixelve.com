#!/usr/bin/env python3
"""Genera las paginas interiores de 1pixelve.com.

La home (index.html) NO se toca: ya funciona y ya rankea. Lo unico que se
lee de ella es el bloque <style>, que se vuelca a assets/site.css para que
las paginas interiores se vean identicas sin duplicar el CSS a mano. Si
alguien edita los estilos del index, basta con volver a correr el script.

    python3 build-paginas.py

Cada pagina se define en PAGINAS: slug, metadatos y cuerpo en HTML. El
contenido vive aca, no en los archivos generados, asi que los .html de
salida no se editan directamente.
"""

import html
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
DOMINIO = "https://1pixelve.com"
HOY = "2026-08-12"

WA = "https://wa.me/584222174935?text=Hola%2C%20quiero%20informacion%20sobre%20publicidad%20en%201PIXEL"


# --------------------------------------------------------------------------
# CSS: se extrae del index y se le agregan los estilos propios de estas
# paginas (columna de lectura, tablas, cajas de datos).
# --------------------------------------------------------------------------

CSS_PAGINAS = """
/* === PAGINAS INTERIORES === */
.pagina-hero {
  padding: 160px 0 60px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background:
    radial-gradient(
      ellipse at 20% 0%,
      rgba(139, 0, 255, 0.16),
      transparent 60%
    ),
    var(--bg);
}
.pagina-hero h1 {
  font-family: var(--font-display);
  font-size: clamp(2rem, 4.6vw, 3.4rem);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -1.5px;
  max-width: 18ch;
}
.pagina-hero .bajada {
  margin-top: 22px;
  font-size: 1.12rem;
  color: rgba(255, 255, 255, 0.62);
  max-width: 62ch;
}
.breadcrumb {
  font-size: 0.85rem;
  color: var(--gray);
  margin-bottom: 26px;
}
.breadcrumb a:hover {
  color: var(--white);
}
.breadcrumb span {
  margin: 0 8px;
  opacity: 0.5;
}
.prosa {
  padding: 70px 0 90px;
}
.prosa .container {
  max-width: 780px;
}
.prosa h2 {
  font-family: var(--font-display);
  font-size: clamp(1.5rem, 3vw, 2.1rem);
  font-weight: 600;
  letter-spacing: -0.8px;
  line-height: 1.2;
  margin: 54px 0 18px;
}
.prosa h3 {
  font-size: 1.18rem;
  font-weight: 600;
  margin: 34px 0 12px;
  color: var(--white);
}
.prosa p {
  color: rgba(255, 255, 255, 0.72);
  margin-bottom: 18px;
  font-size: 1.02rem;
}
.prosa ul,
.prosa ol {
  color: rgba(255, 255, 255, 0.72);
  margin: 0 0 22px 22px;
}
.prosa li {
  margin-bottom: 10px;
}
.prosa strong {
  color: var(--white);
  font-weight: 600;
}
.prosa a:not(.shiny-cta) {
  color: #c58bff;
  text-decoration: underline;
  text-underline-offset: 3px;
}
.prosa a:not(.shiny-cta):hover {
  color: var(--white);
}
.dato-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  overflow: hidden;
  margin: 30px 0;
}
.dato-item {
  background: var(--bg-card);
  padding: 22px 18px;
  text-align: center;
}
.dato-item .n {
  font-family: var(--font-display);
  font-size: 1.9rem;
  font-weight: 700;
  color: var(--white);
  letter-spacing: -1px;
}
.dato-item .l {
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 1.4px;
  color: var(--gray);
  margin-top: 6px;
}
.tabla-wrap {
  overflow-x: auto;
  margin: 26px 0;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
}
.prosa table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.94rem;
  min-width: 460px;
}
.prosa th,
.prosa td {
  padding: 13px 16px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}
.prosa th {
  background: var(--bg-light);
  color: var(--white);
  font-weight: 600;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.prosa td {
  color: rgba(255, 255, 255, 0.72);
}
.prosa tr:last-child td {
  border-bottom: 0;
}
.nota {
  border-left: 2px solid var(--purple);
  background: rgba(139, 0, 255, 0.07);
  padding: 18px 22px;
  border-radius: 0 10px 10px 0;
  margin: 28px 0;
}
.nota p:last-child {
  margin-bottom: 0;
}
.cierre {
  margin-top: 56px;
  padding: 34px;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 16px;
  background: var(--bg-card);
  text-align: center;
}
.cierre h2 {
  margin-top: 0;
  font-size: 1.45rem;
}
.cierre p {
  max-width: 46ch;
  margin: 0 auto 24px;
}
.enlaces-relacionados {
  margin-top: 44px;
  padding-top: 26px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}
.enlaces-relacionados h2 {
  font-size: 1.1rem;
  margin: 0 0 14px;
}
.enlaces-relacionados ul {
  margin-left: 20px;
}
.pagina-video {
  width: 100%;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  margin: 28px 0;
  display: block;
}
@media (max-width: 768px) {
  .pagina-hero {
    padding: 130px 0 44px;
  }
  .prosa {
    padding: 46px 0 64px;
  }
  .cierre {
    padding: 26px 20px;
  }
}
"""


# --------------------------------------------------------------------------
# Plantilla
# --------------------------------------------------------------------------

PLANTILLA = """<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
    <link rel="icon" type="image/png" href="/favicon.png" />
    <link rel="canonical" href="{url}" />
    <meta name="description" content="{description}" />
    <meta property="og:type" content="{og_type}" />
    <meta property="og:site_name" content="1PIXEL" />
    <meta property="og:url" content="{url}" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:image" content="{DOMINIO}/og-image.png" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:locale" content="es_VE" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{description}" />
    <meta name="twitter:image" content="{DOMINIO}/og-image.png" />
    <link
      rel="preload"
      href="/fonts/inter-var-latin.woff2"
      as="font"
      type="font/woff2"
      crossorigin
    />
    <link rel="stylesheet" href="/fonts/inter.css" />
    <link rel="stylesheet" href="/icons.css" />
    <link rel="stylesheet" href="/assets/site.css" />
    <script type="application/ld+json">
{jsonld}
    </script>
  </head>
  <body>
    <nav id="navbar" class="navbar-solido">
      <div class="container">
        <a href="/" class="logo" aria-label="1PIXEL — inicio"
          ><img
            src="/logo.webp"
            width="286"
            height="96"
            alt="1PIXEL"
            fetchpriority="high"
        /></a>
        <ul class="nav-links" id="navLinks">
          <li><a href="/pantallas-led-maracaibo/">Pantallas LED</a></li>
          <li><a href="/#galerias">Galerías</a></li>
          <li><a href="/publicidad-dooh-venezuela/">DOOH</a></li>
          <li><a href="/nosotros/">Nosotros</a></li>
          <li>
            <a href="/#contacto" class="nav-cta shiny-cta shiny-sm"
              ><span>Contacto</span></a
            >
          </li>
        </ul>
        <button
          class="hamburger"
          id="hamburger"
          aria-label="Menú"
          aria-expanded="false"
          aria-controls="navLinks"
        >
          <span></span><span></span><span></span>
        </button>
      </div>
    </nav>

    <header class="pagina-hero">
      <div class="container">
        <nav class="breadcrumb" aria-label="Ruta de navegación">
          <a href="/">Inicio</a><span>/</span>{breadcrumb_final}
        </nav>
        <h1>{h1}</h1>
        <p class="bajada">{bajada}</p>
      </div>
    </header>

    <main class="prosa">
      <div class="container">
{cuerpo}
        <div class="cierre">
          <h2>{cta_titulo}</h2>
          <p>{cta_texto}</p>
          <a
            href="{WA}"
            class="shiny-cta"
            target="_blank"
            rel="noopener"
            ><span>Escríbenos por WhatsApp</span></a
          >
        </div>
{relacionados}
      </div>
    </main>

    <footer>
      <div class="container">
        <div class="footer-grid">
          <div class="footer-brand">
            <a href="/" class="logo" aria-label="1PIXEL — inicio"
              ><img
                src="/logo.webp"
                width="286"
                height="96"
                alt="1PIXEL"
                loading="lazy"
            /></a>
            <p>
              Iluminando marcas en Maracaibo. La red de pantallas LED
              publicitarias más innovadora de la región.
            </p>
            <div class="footer-social">
              <a
                href="https://wa.me/584222174935"
                target="_blank"
                rel="noopener"
                aria-label="WhatsApp"
                ><i class="fab fa-whatsapp"></i
              ></a>
              <a href="mailto:ventas@1pixelve.com" aria-label="Email"
                ><i class="fas fa-envelope"></i
              ></a>
              <a
                href="https://www.instagram.com/1pixelve"
                target="_blank"
                rel="noopener"
                aria-label="Instagram"
                ><i class="fab fa-instagram"></i
              ></a>
            </div>
          </div>
          <div class="footer-col">
            <h3>Publicidad LED</h3>
            <ul>
              <li>
                <a href="/pantallas-led-maracaibo/">Pantallas LED Maracaibo</a>
              </li>
              <li>
                <a href="/alquiler-pantallas-led-maracaibo/"
                  >Alquiler de pantallas LED</a
                >
              </li>
              <li>
                <a href="/vallas-digitales-maracaibo/">Vallas digitales</a>
              </li>
              <li>
                <a href="/publicidad-dooh-venezuela/">Publicidad DOOH</a>
              </li>
            </ul>
          </div>
          <div class="footer-col">
            <h3>Galerías</h3>
            <ul>
              <li>
                <a href="/galerias/calle-77-bella-vista/"
                  >Calle 77 con Bella Vista</a
                >
              </li>
              <li>
                <a href="/galerias/cecilio-acosta/">Cecilio Acosta</a>
              </li>
              <li>
                <a href="/galerias/corredor-gastronomico-3h/"
                  >Corredor Gastronómico 3H</a
                >
              </li>
              <li><a href="/nosotros/">Sobre 1PIXEL</a></li>
              <li><a href="/blog/">Blog</a></li>
            </ul>
          </div>
          <div class="footer-col">
            <h3>Contacto</h3>
            <ul>
              <li>
                <a
                  href="https://wa.me/584222174935"
                  target="_blank"
                  rel="noopener"
                  ><i class="fab fa-whatsapp"></i> +58 422-217-4935</a
                >
              </li>
              <li>
                <a href="mailto:ventas@1pixelve.com"
                  ><i class="fas fa-envelope"></i> ventas@1pixelve.com</a
                >
              </li>
              <li>
                <a href="mailto:administracion@1pixelve.com"
                  ><i class="fas fa-envelope"></i>
                  administracion@1pixelve.com</a
                >
              </li>
            </ul>
          </div>
        </div>
        <div class="footer-bottom">
          <span>&copy; 2026 1PIXEL. Todos los derechos reservados.</span>
          <span class="developed-by"
            >Web developed by
            <a href="https://1bite.studio/" target="_blank" rel="noopener"
              ><img
                src="/1bite-logo.webp"
                alt="1bite Studio"
                style="
                  height: 18px;
                  width: auto;
                  filter: invert(1);
                  vertical-align: middle;
                " /></a
          ></span>
          <span>Maracaibo, Venezuela</span>
          <span>Actualizado: agosto 2026</span>
        </div>
      </div>
    </footer>

    <script>
      /* Menu movil: mismo comportamiento que la home. */
      (function () {
        var burger = document.getElementById("hamburger");
        var links = document.getElementById("navLinks");
        if (!burger || !links) return;
        burger.addEventListener("click", function () {
          // La clase del panel es "open" (asi la define el CSS de la home);
          // el boton si usa "active" para animarse a X.
          var abierto = links.classList.toggle("open");
          burger.classList.toggle("active", abierto);
          burger.setAttribute("aria-expanded", abierto ? "true" : "false");
        });
      })();
    </script>
    <!-- Cloudflare Web Analytics -->
    <script
      defer
      src="https://static.cloudflareinsights.com/beacon.min.js"
      data-cf-beacon='{{"token": "31633f1ed984497bbf33ffc1f82ffad2"}}'
    ></script>
    <!-- End Cloudflare Web Analytics -->
  </body>
</html>
"""


# --------------------------------------------------------------------------
# Bloques reutilizables de contenido
# --------------------------------------------------------------------------

GALERIAS = {
    "calle-77-bella-vista": {
        "nombre": "Calle 77 con Bella Vista",
        "pantallas": 24,
        "video": "galeria-calle77.mp4",
        "poster": "galeria-calle77-poster.webp",
    },
    "cecilio-acosta": {
        "nombre": "Cecilio Acosta",
        "pantallas": 12,
        "video": "galeria-cecilio.mp4",
        "poster": "galeria-cecilio-poster.webp",
    },
    "corredor-gastronomico-3h": {
        "nombre": "Corredor Gastronómico 3H",
        "pantallas": 8,
        "video": "galeria-corredor.mp4",
        "poster": "galeria-corredor-poster.webp",
    },
    "calle-77-delicias": {
        "nombre": "Calle 77 con Delicias",
        "pantallas": 24,
        "video": "galeria-5dejulio.mp4",
        "poster": "galeria-5dejulio-poster.webp",
    },
    "bella-vista-calle-72": {
        "nombre": "Bella Vista con Calle 72",
        "pantallas": 12,
        "video": "galeria-bellavista.mp4",
        "poster": "galeria-bellavista-poster.webp",
    },
    "vereda-del-lago": {
        "nombre": "Vereda del Lago",
        "pantallas": 12,
        "video": "galeria-vereda.mp4",
        "poster": "galeria-vereda-poster.webp",
    },
}

MARCAS = (
    "Cervecería Polar, Pepsi, Mavesa, Harina P.A.N., Alkosto, Atún Margarita, "
    "Maraplus, Yukery, Canel, Disprocar, Farruggio, OZ, Salvaje, San Simón, "
    "Javitour, Sangría Carorena, BNC y Palmira"
)


def datos(*pares):
    items = "".join(
        '\n          <div class="dato-item">'
        '<div class="n">%s</div><div class="l">%s</div></div>' % (n, l)
        for n, l in pares
    )
    return '        <div class="dato-grid">%s\n        </div>' % items


def video(slug):
    g = GALERIAS[slug]
    return (
        "        <video\n"
        '          class="pagina-video"\n'
        '          src="/%s"\n'
        '          poster="/%s"\n'
        '          preload="none"\n'
        "          controls\n"
        "          muted\n"
        "          playsinline\n"
        '          aria-label="Pantallas LED de 1PIXEL en %s, Maracaibo"\n'
        "        ></video>" % (g["video"], g["poster"], g["nombre"])
    )


# --------------------------------------------------------------------------
# Contenido de cada pagina
# --------------------------------------------------------------------------

PAGINAS = [
    {
        "slug": "pantallas-led-maracaibo",
        "title": "Pantallas LED Publicitarias en Maracaibo: 92 Pantallas en 6 Galerías | 1PIXEL",
        "description": "Red de 92 pantallas LED publicitarias en 6 galerías comerciales de Maracaibo. Alta resolución, transmisión 24/7 y exclusividad por subrubro. Conoce las ubicaciones.",
        "h1": "Pantallas LED publicitarias en Maracaibo",
        "breadcrumb": "Pantallas LED en Maracaibo",
        "bajada": "92 pantallas de alta resolución repartidas en seis galerías comerciales de alto tráfico. Tu marca visible las 24 horas, en las zonas donde de verdad camina la gente.",
        "cta_titulo": "¿Quieres tu marca en estas pantallas?",
        "cta_texto": "Cuéntanos qué vendes y en qué zona de Maracaibo está tu cliente. Te decimos cuál galería te conviene y si tu subrubro sigue libre.",
        "cuerpo": """
        <p>
          <strong>1PIXEL</strong> es la red de pantallas LED publicitarias más
          grande de Maracaibo. Operamos 92 pantallas de alta resolución
          instaladas en las entradas y pasillos principales de seis galerías
          comerciales del municipio, donde el tráfico peatonal se concentra
          durante todo el día. Tu anuncio se transmite las 24 horas, los 7 días
          de la semana, sin costos de impresión ni de instalación.
        </p>
"""
        + datos(
            ("92", "Pantallas activas"),
            ("6", "Galerías"),
            ("24/7", "Transmisión"),
            ("48 h", "Activación"),
        )
        + """
        <h2>¿Dónde están las pantallas LED de 1PIXEL en Maracaibo?</h2>
        <p>
          La red está distribuida en seis puntos con perfiles de público
          distintos. No es la misma persona la que entra a una galería de
          Bella Vista a mediodía que la que camina el Corredor Gastronómico un
          viernes en la noche, y esa diferencia es la que usamos para ubicar
          cada marca donde le rinde.
        </p>
        <div class="tabla-wrap">
          <table>
            <thead>
              <tr>
                <th>Galería</th>
                <th>Pantallas</th>
                <th>Perfil de público</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <a href="/galerias/calle-77-bella-vista/"
                    >Calle 77 con Bella Vista</a
                  >
                </td>
                <td>24</td>
                <td>Tráfico peatonal y vehicular alto, comercio general</td>
              </tr>
              <tr>
                <td>
                  <a href="/galerias/calle-77-delicias/">Calle 77 con Delicias</a>
                </td>
                <td>24</td>
                <td>Uno de los cruces de mayor flujo vehicular de la ciudad</td>
              </tr>
              <tr>
                <td>
                  <a href="/galerias/cecilio-acosta/">Cecilio Acosta (Calle 67)</a>
                </td>
                <td>12</td>
                <td>Comercio diurno y zona gastronómica nocturna</td>
              </tr>
              <tr>
                <td>
                  <a href="/galerias/bella-vista-calle-72/"
                    >Av. Bella Vista con Calle 72</a
                  >
                </td>
                <td>12</td>
                <td>Corredor comercial y bancario de tránsito constante</td>
              </tr>
              <tr>
                <td>
                  <a href="/galerias/vereda-del-lago/">Vereda del Lago</a>
                </td>
                <td>12</td>
                <td>Recreación, deporte y familias; picos de tarde y fin de semana</td>
              </tr>
              <tr>
                <td>
                  <a href="/galerias/corredor-gastronomico-3h/"
                    >Corredor Gastronómico AV 3H</a
                  >
                </td>
                <td>8</td>
                <td>Punto de encuentro, entretenimiento, pico nocturno</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2>¿Qué hace distinta a una pantalla LED de una valla impresa?</h2>
        <p>
          Una valla tradicional muestra un solo arte durante todo el contrato.
          Si quieres cambiar el mensaje —porque se acabó la promoción, porque
          entró temporada, porque cambió el precio— hay que reimprimir la lona
          y volver a instalarla. Una pantalla LED muestra contenido digital:
          puedes rotar artes, usar video en movimiento y actualizar cuando
          quieras.
        </p>
        <p>
          En 1PIXEL incluimos <strong>dos cambios de contenido al mes</strong>
          sin costo adicional. Aceptamos imágenes estáticas y videos cortos en
          alta resolución, y la actualización es remota: no hace falta que
          nadie suba a una estructura.
        </p>

        <h2>¿Cuántas marcas comparten una pantalla?</h2>
        <p>
          Limitamos cada galería a <strong>15 marcas</strong>. No es una cifra
          de marketing: es el máximo que permite que cada anuncio vuelva a
          aparecer con suficiente frecuencia como para que la gente lo registre.
          Si metiéramos treinta marcas, tu turno llegaría cuando el visitante ya
          se fue.
        </p>
        <p>
          Además aplicamos <strong>exclusividad por subrubro</strong>: si tu
          farmacia está en una galería, otra farmacia no entra a esa misma
          galería. Tu competencia directa no aparece al lado tuyo.
        </p>

        <h2>¿Por qué dentro de galerías y no en la calle?</h2>
        <p>
          Es una decisión deliberada y vale la pena explicarla, porque cambia
          para quién sirve la red. Una valla de avenida le habla a alguien que
          va manejando: la ve dos segundos, a distancia, mientras atiende el
          tráfico. Una pantalla dentro de una galería le habla a alguien que
          camina despacio, que ya salió de su casa con intención de comprar y
          que pasa por el mismo pasillo varias veces en la misma visita.
        </p>
        <p>
          Eso produce tres diferencias concretas:
        </p>
        <ul>
          <li>
            <strong>Repetición dentro de la misma visita.</strong> El peatón
            pasa por las pantallas al entrar, al recorrer y al salir. En una
            avenida, el mismo carro pasa una vez.
          </li>
          <li>
            <strong>Contexto de compra.</strong> No estás interrumpiendo a
            alguien que va a trabajar: estás frente a quien está resolviendo una
            compra en ese momento.
          </li>
          <li>
            <strong>Operación más confiable.</strong> Espacio techado, energía
            estable y acceso directo al equipo. En la práctica venezolana, eso
            se traduce en más horas encendida.
          </li>
        </ul>

        <h2>Cómo se decide en cuál galería anunciarse</h2>
        <p>
          La pregunta que hacemos antes de cotizar no es cuánto quieres
          invertir, sino <strong>a quién le vendes y dónde está</strong>. Con
          eso la decisión suele resolverse sola:
        </p>
        <ul>
          <li>
            Si buscas <strong>volumen general de ciudad</strong> y recordación
            de marca, Calle 77 con Bella Vista o Calle 77 con Delicias, que
            concentran 24 pantallas cada una.
          </li>
          <li>
            Si tu cliente es <strong>del sector</strong> y quieres presencia
            sostenida ante un público recurrente, Cecilio Acosta, que además te
            da dos públicos distintos en el mismo día.
          </li>
          <li>
            Si vendes algo de <strong>consumo nocturno</strong> —bebidas,
            comida, entretenimiento— el Corredor Gastronómico de AV 3H, donde el
            público está detenido y con tiempo de mirar.
          </li>
        </ul>
        <p>
          Si tu público no está en ninguna de ellas, te lo decimos. Vender
          tres meses de pauta que no van a rendir nos cuesta más caro que no
          venderlos.
        </p>

        <h2>Mantenimiento y disponibilidad</h2>
        <p>
          Una red de pantallas vale lo que vale su tiempo encendida. Las
          pantallas son nuestras, no de un tercero, así que el mantenimiento
          también: tenemos servicio técnico local y stock para reposición
          inmediata. Si un equipo falla, se reemplaza; no se espera a que llegue
          un repuesto importado.
        </p>

        <h2>¿Qué tipo de negocios se anuncian?</h2>
        <p>
          Se anuncian marcas de consumo masivo, restaurantes, tiendas de ropa,
          clínicas, concesionarios, inmobiliarias, bancos y comercios de barrio.
          Entre las marcas que han pautado con nosotros están """
        + MARCAS
        + """.
        </p>

        <h2>¿Cuánto tarda en salir mi anuncio?</h2>
        <p>
          Menos de <strong>48 horas</strong> desde que se firma el contrato y
          nos llega el arte. Si no tienes pieza lista, te orientamos sobre el
          formato y los tiempos que funcionan en pantalla —lo que se ve bien en
          Instagram no siempre se lee bien en una pantalla que la gente mira de
          paso.
        </p>

        <h2>Preguntas frecuentes</h2>
        <h3>¿Las pantallas se ven de día?</h3>
        <p>
          Sí. Las pantallas tienen brillo ajustable y se leen nítidas bajo el
          sol del mediodía y de noche. En zonas como el Corredor Gastronómico
          de AV 3H, de hecho, el horario nocturno es el de mayor tráfico.
        </p>
        <h3>¿Tengo que contratar las seis galerías?</h3>
        <p>
          No. Puedes contratar una, varias o todas según tu objetivo y tu
          presupuesto. Lo más común en marcas que arrancan es empezar por la
          galería donde está su cliente y ampliar después.
        </p>
        <h3>¿Cuál es la duración mínima?</h3>
        <p>
          Los contratos arrancan en <strong>3 meses</strong>. Menos tiempo que
          eso no alcanza para que la repetición haga efecto: la publicidad
          exterior funciona por acumulación de impactos, no por un golpe único.
        </p>
""",
        "relacionados": [
            (
                "/alquiler-pantallas-led-maracaibo/",
                "Cómo funciona el alquiler de pantallas LED en Maracaibo",
            ),
            (
                "/vallas-digitales-maracaibo/",
                "Vallas digitales en Maracaibo: qué son y dónde están",
            ),
            (
                "/publicidad-dooh-venezuela/",
                "Publicidad DOOH en Venezuela: guía completa",
            ),
        ],
    },
    {
        "slug": "alquiler-pantallas-led-maracaibo",
        "title": "Alquiler de Pantallas LED en Maracaibo: Cómo Contratar | 1PIXEL",
        "description": "Cómo alquilar una pantalla LED publicitaria en Maracaibo: qué incluye el contrato, duración mínima, formatos aceptados y el paso a paso para salir al aire en 48 horas.",
        "h1": "Alquiler de pantallas LED en Maracaibo",
        "breadcrumb": "Alquiler de pantallas LED",
        "bajada": "Qué incluye el contrato, cuánto dura, qué formato mandar y cómo es el proceso completo hasta que tu marca aparece en pantalla.",
        "cta_titulo": "Pide tu cotización",
        "cta_texto": "El costo depende de la galería, la cantidad de pantallas y la duración. Escríbenos con tu rubro y armamos la propuesta.",
        "cuerpo": """
        <p>
          Alquilar una pantalla LED con 1PIXEL significa comprar un espacio
          rotativo dentro de nuestra red de 92 pantallas en Maracaibo. No
          compras la pantalla ni pagas instalación: pagas por aparecer, y
          nosotros nos encargamos del resto —el equipo, la electricidad, el
          mantenimiento y la reposición si algo falla.
        </p>

        <h2>¿Qué incluye el alquiler?</h2>
        <ul>
          <li>
            Transmisión continua las 24 horas, los 7 días de la semana, en la
            galería o galerías que contrates.
          </li>
          <li>
            <strong>Dos actualizaciones de contenido al mes</strong> sin costo
            adicional: cambias el arte cuando cambia tu promoción.
          </li>
          <li>
            <strong>Exclusividad por subrubro</strong>: tu competencia directa
            no entra a la misma galería mientras tú estés.
          </li>
          <li>
            Un máximo de 15 marcas por galería, para que tu anuncio vuelva a
            salir con frecuencia útil.
          </li>
          <li>
            Soporte técnico local y stock para reposición inmediata: si una
            pantalla falla, se cambia, no se espera.
          </li>
        </ul>

        <h2>¿Cuánto cuesta alquilar una pantalla LED en Maracaibo?</h2>
        <p>
          El costo depende de tres variables: <strong>en cuál galería</strong>
          quieres aparecer, <strong>en cuántas pantallas</strong> y por
          <strong>cuánto tiempo</strong>. No manejamos una tarifa única porque
          las galerías no son equivalentes: la de Calle 77 con Bella Vista
          tiene 24 pantallas y un flujo distinto al del Corredor Gastronómico,
          que tiene 8 y concentra su pico de noche.
        </p>
        <div class="nota">
          <p>
            Escríbenos por WhatsApp con tu rubro y la zona donde está tu
            cliente. Te decimos en el momento si tu subrubro está libre en esa
            galería y te pasamos la propuesta con el número exacto.
          </p>
        </div>

        <h2>¿Cuál es la duración mínima del contrato?</h2>
        <p>
          <strong>Tres meses.</strong> La publicidad exterior no funciona por
          impacto único sino por repetición: la misma persona pasa por la misma
          galería varias veces por semana, y es esa acumulación la que hace que
          tu marca se quede. Un mes suelto se gasta en que la gente empiece a
          reconocerte.
        </p>
        <p>
          Ofrecemos pago mensual o prepago del período completo. El prepago
          tiene condiciones distintas; lo conversamos al cotizar.
        </p>

        <h2>¿Qué formato de contenido puedo mandar?</h2>
        <p>
          Aceptamos <strong>imágenes estáticas</strong> y
          <strong>videos cortos</strong> en alta resolución. Recomendaciones
          que salen de ver qué funciona y qué no en nuestras pantallas:
        </p>
        <ul>
          <li>
            <strong>Poco texto.</strong> La gente pasa caminando. Un titular
            corto, tu marca y un dato de contacto. Si hay que detenerse a leer,
            no se lee.
          </li>
          <li>
            <strong>Contraste alto.</strong> Los grises medios se pierden a
            plena luz. Colores plenos y tipografía gruesa.
          </li>
          <li>
            <strong>Video sin audio.</strong> Las pantallas no reproducen
            sonido: el mensaje tiene que entenderse solo con imagen.
          </li>
          <li>
            <strong>Logo visible desde el inicio.</strong> Si tu marca aparece
            solo al final del video, medio público ya se fue.
          </li>
        </ul>
        <p>
          Si no tienes pieza, te pasamos las medidas exactas y las
          recomendaciones para que tu diseñador la arme. También revisamos el
          arte antes de publicarlo y te avisamos si algo no se va a leer bien.
        </p>

        <h2>¿Qué NO incluye el alquiler?</h2>
        <p>
          Conviene decirlo con la misma claridad que lo que sí incluye, para
          que nadie se lleve sorpresas:
        </p>
        <ul>
          <li>
            <strong>El diseño de la pieza no está incluido.</strong> Revisamos
            tu arte y te decimos si va a funcionar en pantalla, pero no lo
            diseñamos nosotros. Si no tienes quién lo haga, te damos las
            especificaciones para que tu diseñador lo arme.
          </li>
          <li>
            <strong>No es una pantalla exclusiva.</strong> Compartes con hasta
            14 marcas más en esa galería. Si necesitas exclusividad total del
            espacio, este formato no es el tuyo.
          </li>
          <li>
            <strong>No hay medición individual de personas.</strong> Nadie en
            DOOH puede decirte cuántas personas exactas vieron tu anuncio. Lo
            que sí te damos es en qué punto estás, cuánto tiempo estuviste al
            aire y qué disponibilidad tuvo la red.
          </li>
        </ul>

        <h2>Preguntas que conviene hacernos antes de firmar</h2>
        <h3>¿Mi subrubro está libre?</h3>
        <p>
          Es la primera que verificamos. La exclusividad por subrubro funciona
          por orden de llegada: si tu competidor directo ya está en esa galería,
          no podemos meterte ahí. Sí podemos ofrecerte otra de las tres.
        </p>
        <h3>¿Cuántas marcas hay ahora mismo en esa galería?</h3>
        <p>
          Te decimos el número real. El tope son 15, pero si en ese momento hay
          nueve, tu anuncio sale con más frecuencia que si hay catorce, y eso es
          información que te corresponde tener antes de decidir.
        </p>
        <h3>¿Qué pasa si una pantalla se daña durante mi contrato?</h3>
        <p>
          Se repone. Mantenemos stock local justamente para eso: el compromiso
          es que la red esté operativa, no que te avisemos que se dañó.
        </p>
        <h3>¿Puedo cambiar de galería a mitad de contrato?</h3>
        <p>
          Se conversa. Si a los dos meses ves que tu público está en otra
          ubicación, preferimos moverte antes que dejarte donde no rinde y
          perderte como cliente al final del período.
        </p>

        <h2>Paso a paso para salir al aire</h2>
        <ol>
          <li>
            <strong>Nos escribes</strong> con tu rubro, tu presupuesto
            aproximado y la zona donde está tu cliente.
          </li>
          <li>
            <strong>Verificamos exclusividad.</strong> Revisamos si tu subrubro
            está libre en la galería que te interesa.
          </li>
          <li>
            <strong>Te pasamos la propuesta</strong> con galería, cantidad de
            pantallas, duración y monto.
          </li>
          <li>
            <strong>Firmas y envías el arte.</strong> Si no lo tienes, te damos
            las especificaciones.
          </li>
          <li>
            <strong>Sales al aire en menos de 48 horas</strong> desde que
            recibimos el material.
          </li>
        </ol>

        <h2>¿En cuál galería me conviene anunciarme?</h2>
        <p>
          Depende de a quién le vendes. Cada galería tiene su propia página con
          el detalle de la zona, el perfil de visitante y los rubros que mejor
          le funcionan:
        </p>
        <ul>
          <li>
            <a href="/galerias/calle-77-bella-vista/"
              >Calle 77 con Bella Vista</a
            >
            — 24 pantallas, el punto de mayor volumen de la red.
          </li>
          <li>
            <a href="/galerias/cecilio-acosta/">Cecilio Acosta</a> — 12
            pantallas, doble turno comercial y gastronómico.
          </li>
          <li>
            <a href="/galerias/corredor-gastronomico-3h/"
              >Corredor Gastronómico AV 3H</a
            >
            — 8 pantallas, público de salida nocturna.
          </li>
        </ul>
""",
        "relacionados": [
            (
                "/pantallas-led-maracaibo/",
                "La red de pantallas LED de 1PIXEL en Maracaibo",
            ),
            ("/vallas-digitales-maracaibo/", "Vallas digitales vs. vallas impresas"),
            ("/nosotros/", "Quiénes somos"),
        ],
    },
    {
        "slug": "vallas-digitales-maracaibo",
        "title": "Vallas Digitales en Maracaibo: Ubicaciones y Alcance | 1PIXEL",
        "description": "Vallas digitales LED en Maracaibo: en qué se diferencian de las vallas impresas, dónde están ubicadas las de 1PIXEL y qué tipo de marca le saca provecho.",
        "h1": "Vallas digitales en Maracaibo",
        "breadcrumb": "Vallas digitales",
        "bajada": "La versión digital de la valla de toda la vida: mismo principio, pero con contenido que cambias cuando quieras y sin costo de impresión.",
        "cta_titulo": "Reserva tu espacio",
        "cta_texto": "Quedan pocos cupos por galería: solo 15 marcas entran en cada una y aplicamos exclusividad por subrubro.",
        "cuerpo": """
        <p>
          Una <strong>valla digital</strong> es una pantalla LED que cumple la
          misma función que una valla publicitaria tradicional —estar donde
          pasa la gente— pero mostrando contenido digital en vez de una lona
          impresa. En Maracaibo, 1PIXEL opera 92 vallas digitales distribuidas
          en seis galerías comerciales.
        </p>

        <h2>Valla digital vs. valla tradicional</h2>
        <div class="tabla-wrap">
          <table>
            <thead>
              <tr>
                <th></th>
                <th>Valla impresa</th>
                <th>Valla digital LED</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Cambiar el arte</td>
                <td>Reimprimir e instalar</td>
                <td>Envío remoto, sin costo de producción</td>
              </tr>
              <tr>
                <td>Contenido</td>
                <td>Una imagen fija</td>
                <td>Imágenes y video en movimiento</td>
              </tr>
              <tr>
                <td>Costo de entrada</td>
                <td>Alto: el espacio es tuyo solo</td>
                <td>Menor: se comparte con hasta 15 marcas</td>
              </tr>
              <tr>
                <td>Visibilidad de noche</td>
                <td>Depende de la iluminación externa</td>
                <td>Luz propia, brillo ajustable</td>
              </tr>
              <tr>
                <td>Tiempo de salida</td>
                <td>Semanas (producción e instalación)</td>
                <td>Menos de 48 horas</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p>
          La contrapartida honesta: en una valla impresa el espacio es tuyo el
          100% del tiempo, mientras que en una digital rotas con otras marcas.
          Por eso limitamos a 15 marcas por galería —para que la rotación siga
          teniendo sentido— y por eso el costo de entrada es mucho menor.
        </p>

        <h2>¿Dónde están las vallas digitales de 1PIXEL?</h2>
        <p>
          A diferencia de las vallas de carretera, las nuestras están
          <strong>dentro de galerías comerciales</strong>: en las entradas y
          los pasillos por donde la gente camina, no maneja. Eso cambia la
          lógica del mensaje —el peatón sí tiene tiempo de leer un poco más que
          el conductor— y cambia el público: quien está en una galería ya salió
          a comprar.
        </p>
        <ul>
          <li>
            <a href="/galerias/calle-77-bella-vista/"
              >Calle 77 con Bella Vista</a
            >: 24 pantallas.
          </li>
          <li>
            <a href="/galerias/cecilio-acosta/">Cecilio Acosta, Calle 67</a>:
            12 pantallas.
          </li>
          <li>
            <a href="/galerias/corredor-gastronomico-3h/"
              >Corredor Gastronómico, AV 3H</a
            >: 8 pantallas.
          </li>
        </ul>
        <p>
          A esas se suman tres galerías más, todas operativas:
          <a href="/galerias/calle-77-delicias/">Calle 77 con Delicias</a>
          (24 pantallas),
          <a href="/galerias/bella-vista-calle-72/"
            >Av. Bella Vista con Calle 72</a
          >
          (12 pantallas) y
          <a href="/galerias/vereda-del-lago/">Vereda del Lago</a>
          (12 pantallas).
        </p>

        <h2>Valla de calle vs. valla digital en galería</h2>
        <p>
          Dentro del mundo de las vallas digitales hay una distinción que casi
          nunca se explica y que cambia por completo el resultado: no es lo
          mismo una pantalla frente a una avenida que una pantalla dentro de un
          espacio comercial.
        </p>
        <p>
          La de avenida le habla a un conductor: dos segundos de atención, a
          distancia, compitiendo con el tráfico. Sirve para grabar un nombre en
          la memoria, poco más. La de galería le habla a un peatón que camina
          despacio, que ya salió a comprar y que pasa por el mismo punto varias
          veces en una sola visita. Ahí sí cabe un mensaje con algo más de
          sustancia, y ahí la repetición trabaja dentro de la misma visita.
        </p>
        <p>
          Las 92 vallas digitales de 1PIXEL son del segundo tipo. Por eso
          insistimos tanto en preguntar dónde está tu cliente antes de cotizar:
          si tu público no camina estas galerías, el formato no te va a rendir
          por barato que salga el impacto.
        </p>

        <h2>¿Cuántas veces se ve tu anuncio?</h2>
        <p>
          Depende de cuántas marcas compartan la galería. Con el tope de 15 que
          manejamos, tu pieza vuelve a aparecer con la frecuencia suficiente
          para que alguien que recorre la galería te vea más de una vez en la
          misma visita. Ese es todo el sentido de poner un tope: si el número
          fuera cuarenta, tu turno llegaría cuando el visitante ya se fue.
        </p>
        <p>
          Es la pregunta que conviene hacerle a cualquier proveedor de vallas
          digitales antes de firmar, y la que menos aparece en las propuestas.
        </p>

        <h2>¿A qué marcas les rinde una valla digital?</h2>
        <p>
          Le rinde especialmente a quien necesita <strong>recordación</strong>
          más que explicación: consumo masivo, restaurantes, tiendas, clínicas,
          concesionarios, bancos. Es decir, negocios donde el objetivo es que tu
          nombre esté en la cabeza del cliente en el momento en que decide.
        </p>
        <p>
          Le rinde menos a quien vende algo que requiere una explicación larga o
          un público muy específico y pequeño: ahí una pantalla en un pasillo
          de galería no es el canal, por más barato que salga el impacto.
        </p>
        <p>
          Entre las marcas que han pautado en nuestras vallas digitales están
          """
        + MARCAS
        + """.
        </p>

        <h2>¿Cómo se contrata?</h2>
        <p>
          El proceso completo, con lo que incluye el contrato y los formatos que
          aceptamos, está en
          <a href="/alquiler-pantallas-led-maracaibo/"
            >la página de alquiler de pantallas LED</a
          >. En resumen: nos escribes, verificamos que tu subrubro esté libre,
          te pasamos la propuesta y sales al aire en menos de 48 horas.
        </p>
""",
        "relacionados": [
            ("/pantallas-led-maracaibo/", "Las 92 pantallas LED de la red"),
            ("/publicidad-dooh-venezuela/", "Qué es la publicidad DOOH"),
            ("/alquiler-pantallas-led-maracaibo/", "Cómo contratar"),
        ],
    },
    {
        "slug": "publicidad-dooh-venezuela",
        "title": "Publicidad DOOH en Venezuela: Qué Es y Cómo Funciona | 1PIXEL",
        "description": "Guía de publicidad DOOH (digital out of home) en Venezuela: qué es, en qué se diferencia del OOH tradicional, cómo se mide y qué hace falta para que funcione.",
        "h1": "Publicidad DOOH en Venezuela: qué es y cómo funciona",
        "breadcrumb": "Publicidad DOOH",
        "bajada": "Digital out of home: la publicidad exterior que dejó de imprimirse. Qué significa en la práctica, qué cambia frente a una valla de toda la vida y cómo se está aplicando en Maracaibo.",
        "cta_titulo": "¿Quieres probar DOOH en Maracaibo?",
        "cta_texto": "Operamos la red DOOH más grande de la ciudad. Te explicamos sin compromiso si tu marca encaja o si te conviene otro canal.",
        "cuerpo": """
        <p>
          <strong>DOOH</strong> son las siglas de <em>digital out of home</em>:
          publicidad exterior digital. Es toda la publicidad que ocurre fuera de
          la casa —vallas, pantallas en centros comerciales, en aeropuertos, en
          transporte— pero mostrada en pantallas en vez de en material impreso.
        </p>
        <p>
          El término suena técnico, pero el cambio de fondo es simple: cuando el
          soporte deja de ser una lona y pasa a ser una pantalla, el contenido
          deja de ser fijo. Y cuando el contenido deja de ser fijo, cambian el
          costo, la flexibilidad y hasta el tipo de anunciante que puede entrar.
        </p>

        <h2>OOH vs. DOOH: qué cambia de verdad</h2>
        <h3>1. El costo de cambiar de mensaje se vuelve casi cero</h3>
        <p>
          En OOH tradicional, cambiar el arte significa reimprimir e instalar.
          Ese costo hace que las campañas se piensen en bloques largos y con un
          solo mensaje. En DOOH el cambio es un archivo enviado de forma remota,
          así que la misma marca puede rotar promociones, adaptar el mensaje por
          temporada o corregir un precio el mismo día.
        </p>
        <h3>2. El espacio se comparte, y eso baja la barrera de entrada</h3>
        <p>
          Una valla impresa es tuya al 100%: pagas por ocuparla completa. Una
          pantalla digital rota entre varias marcas, así que el costo por
          anunciante baja mucho. Es la razón por la que negocios que jamás
          habrían pagado una valla —una clínica de barrio, una tienda de ropa,
          un restaurante— hoy pueden hacer publicidad exterior.
        </p>
        <p>
          La contrapartida es real y hay que decirla: no estás solo en la
          pantalla. Por eso importa cuántas marcas comparten el espacio. En
          nuestra red el tope son
          <strong>15 marcas por galería</strong>, con exclusividad por subrubro.
        </p>
        <h3>3. El movimiento entra en juego</h3>
        <p>
          El video capta la mirada de una forma que una imagen fija no logra. La
          trampa es asumir que un comercial de televisión sirve tal cual: en la
          calle nadie oye audio ni se queda treinta segundos. El contenido DOOH
          que funciona es corto, sin sonido, con poco texto y con la marca
          visible desde el primer segundo.
        </p>

        <h3>4. Se puede programar por horario</h3>
        <p>
          Una lona muestra lo mismo a las 8 de la mañana que a las 10 de la
          noche. Una pantalla no tiene por qué. Un restaurante puede anunciar
          almuerzo ejecutivo al mediodía y otra cosa en la noche; una tienda
          puede empujar una promoción solo los fines de semana. No todos los
          operadores ofrecen esta granularidad —conviene preguntarla antes de
          firmar, porque cambia bastante lo que puedes hacer con el espacio.
        </p>

        <h2>Los formatos de DOOH que existen</h2>
        <p>
          "DOOH" abarca cosas bastante distintas entre sí, y meterlas en la
          misma bolsa lleva a comparar peras con manzanas cuando se evalúan
          presupuestos:
        </p>
        <ul>
          <li>
            <strong>Gran formato urbano.</strong> Pantallas grandes en avenidas
            y autopistas, pensadas para el conductor. Mensajes de tres o cuatro
            palabras, alcance masivo, costo alto.
          </li>
          <li>
            <strong>Retail y galerías.</strong> Pantallas dentro de espacios
            comerciales, para peatones. Público en modo compra, más tiempo de
            lectura, costo de entrada mucho menor. Es el segmento donde opera
            1PIXEL.
          </li>
          <li>
            <strong>Transit.</strong> Pantallas en terminales, estaciones y
            unidades de transporte. Audiencia cautiva y tiempos de exposición
            largos.
          </li>
          <li>
            <strong>Point of sale.</strong> Pantallas dentro del local, junto al
            producto. Muy cerca del momento de decisión, pero alcance limitado a
            quien ya entró.
          </li>
        </ul>
        <p>
          Cada uno resuelve un problema distinto. El gran formato construye
          notoriedad de marca; el de retail acompaña la decisión de compra. Si
          alguien te ofrece "publicidad DOOH" sin especificar de cuál habla,
          esa es la primera pregunta.
        </p>

        <h2>El contexto venezolano</h2>
        <p>
          En Venezuela el DOOH creció por una vía distinta a la de otros
          mercados. Donde en otros países la expansión vino por vallas digitales
          de carretera y grandes pantallas urbanas, acá buena parte del
          crecimiento ocurrió <strong>dentro de galerías y centros
          comerciales</strong>: espacios cerrados, con flujo peatonal constante,
          donde la instalación y el mantenimiento son más manejables.
        </p>
        <p>
          Eso tiene una consecuencia práctica para el anunciante: el público de
          una galería no es el mismo que el de una autopista. Ya salió de la
          casa con intención de comprar, camina despacio y pasa varias veces por
          el mismo punto. Es un contexto donde la repetición trabaja a favor.
        </p>
        <p>
          El otro factor local es la <strong>continuidad eléctrica</strong>.
          Una red de pantallas solo vale si está encendida; por eso monitoreamos
          la disponibilidad de cada galería y mantenemos stock para reposición
          inmediata cuando un equipo falla.
        </p>

        <h2>¿Cómo se mide el DOOH?</h2>
        <p>
          Es la pregunta honesta que hay que hacerle a cualquier proveedor. A
          diferencia de la publicidad digital en redes, el DOOH no entrega un
          clic: no hay manera de saber cuántas personas exactas miraron tu
          anuncio. Lo que sí puede medirse:
        </p>
        <ul>
          <li>
            <strong>Flujo de la ubicación</strong>: cuánta gente pasa por el
            punto donde está la pantalla.
          </li>
          <li>
            <strong>Tiempo en pantalla</strong>: cuántas veces por hora sale tu
            anuncio y cuántos segundos dura.
          </li>
          <li>
            <strong>Disponibilidad</strong>: qué porcentaje del tiempo
            contratado la pantalla estuvo efectivamente encendida.
          </li>
          <li>
            <strong>Respuesta atribuida</strong>: códigos, cupones o un número
            de WhatsApp distinto al de tus otros canales.
          </li>
        </ul>
        <div class="nota">
          <p>
            Si un proveedor te promete cifras exactas de "personas alcanzadas"
            sin explicarte de dónde salen, pregúntale la metodología. En DOOH
            las estimaciones son estimaciones, y está bien que lo sean —lo que
            no está bien es venderlas como medición.
          </p>
        </div>

        <h2>Cómo se hace una pieza DOOH que funcione</h2>
        <p>
          El error más común es reciclar material de otro canal. Un post de
          Instagram tiene a alguien mirando una pantalla a treinta centímetros
          de la cara, con tiempo y con la posibilidad de detenerse. Una pantalla
          en un pasillo tiene a alguien caminando, a varios metros, mirando de
          reojo. No es el mismo formato aunque la imagen sea la misma.
        </p>
        <h3>Reglas que se sostienen en la práctica</h3>
        <ul>
          <li>
            <strong>Una sola idea por pieza.</strong> Si el anuncio comunica
            tres cosas, no comunica ninguna. Elige qué es lo único que quieres
            que la persona recuerde.
          </li>
          <li>
            <strong>Seis palabras o menos en el titular.</strong> Es una regla
            gruesa, pero funciona como filtro: si no cabe en seis palabras,
            probablemente todavía no está claro qué quieres decir.
          </li>
          <li>
            <strong>Marca visible desde el primer segundo.</strong> En video, si
            el logo aparece al final, buena parte del público se fue antes de
            llegar ahí.
          </li>
          <li>
            <strong>Contraste alto y tipografía gruesa.</strong> Los grises
            medios y las tipografías finas se desvanecen a plena luz.
          </li>
          <li>
            <strong>Sin audio.</strong> Las pantallas de exterior no reproducen
            sonido. Si tu mensaje depende de lo que se dice, no se entiende.
          </li>
          <li>
            <strong>Una acción concreta.</strong> Un número de WhatsApp, un
            nombre de local, una dirección. Un código QR funciona solo si la
            gente está detenida —en un punto de circulación rápida, no lo
            escanea nadie.
          </li>
        </ul>

        <h2>Errores frecuentes al contratar DOOH</h2>
        <h3>Comprar por cantidad de pantallas</h3>
        <p>
          Cincuenta pantallas en sitios donde no está tu cliente valen menos que
          ocho donde sí está. La pregunta correcta no es cuántas pantallas, sino
          quién pasa por ellas y con qué frecuencia.
        </p>
        <h3>No preguntar cuántas marcas comparten el espacio</h3>
        <p>
          Es el dato que más cambia el valor real de lo que compras y el que
          menos se menciona en las propuestas. Si el operador no lo dice,
          pregúntalo: entre rotar con quince marcas y rotar con cuarenta hay una
          diferencia enorme en cuántas veces te ve la misma persona.
        </p>
        <h3>Contratar un mes "para probar"</h3>
        <p>
          Es la forma más segura de concluir que el canal no sirve. La
          publicidad exterior necesita repetición sobre la misma persona, y eso
          toma semanas. Un mes suelto solo alcanza para que la gente empiece a
          registrarte, justo cuando sales del aire.
        </p>
        <h3>No preguntar por la disponibilidad real</h3>
        <p>
          En Venezuela esto es determinante: una pantalla apagada no anuncia
          nada. Pregunta qué porcentaje del tiempo la red estuvo operativa el
          mes pasado y qué pasa si un equipo falla a mitad de tu contrato.
        </p>

        <h2>¿Le conviene DOOH a tu marca?</h2>
        <p><strong>Suele funcionar cuando:</strong></p>
        <ul>
          <li>
            Vendes algo de decisión rápida o compra frecuente y necesitas
            recordación.
          </li>
          <li>
            Tu cliente está geográficamente concentrado en una zona de la
            ciudad.
          </li>
          <li>
            Ya tienes presencia digital y te falta el componente de calle que
            le dé peso físico a la marca.
          </li>
        </ul>
        <p><strong>Suele quedarse corto cuando:</strong></p>
        <ul>
          <li>
            Tu producto necesita explicación larga antes de que alguien lo
            entienda.
          </li>
          <li>
            Tu público es muy pequeño y específico: ahí la segmentación digital
            rinde más por cada dólar.
          </li>
          <li>
            Esperas resultados en dos semanas. El DOOH trabaja por acumulación;
            por eso nuestros contratos arrancan en tres meses.
          </li>
        </ul>

        <h2>DOOH en Maracaibo con 1PIXEL</h2>
        <p>
          1PIXEL opera la red DOOH más grande de Maracaibo:
          <strong>92 pantallas LED</strong> en seis galerías comerciales, con
          transmisión 24/7, dos cambios de contenido al mes incluidos y
          exclusividad por subrubro. Puedes ver
          <a href="/pantallas-led-maracaibo/">el detalle de la red</a> o
          <a href="/alquiler-pantallas-led-maracaibo/"
            >cómo funciona la contratación</a
          >.
        </p>
""",
        "relacionados": [
            ("/pantallas-led-maracaibo/", "La red de pantallas LED en Maracaibo"),
            (
                "/vallas-digitales-maracaibo/",
                "Vallas digitales: comparativa con la valla impresa",
            ),
            ("/nosotros/", "Quiénes somos"),
        ],
    },
    {
        "slug": "galerias/calle-77-bella-vista",
        "title": "Pantallas LED en Calle 77 con Bella Vista, Maracaibo | 1PIXEL",
        "description": "24 pantallas LED publicitarias en la galería de Calle 77 con Av. Bella Vista, Maracaibo. El punto de mayor volumen de la red 1PIXEL. Conoce el perfil de público.",
        "h1": "Pantallas LED en Calle 77 con Bella Vista",
        "breadcrumb": '<a href="/pantallas-led-maracaibo/">Pantallas LED</a><span>/</span>Calle 77 con Bella Vista',
        "bajada": "24 pantallas, el punto de mayor volumen de la red 1PIXEL. Cruce de tráfico peatonal y vehicular en una de las zonas comerciales más transitadas de Maracaibo.",
        "cta_titulo": "¿Tu subrubro sigue libre en esta galería?",
        "cta_texto": "Solo entran 15 marcas y aplicamos exclusividad por categoría. Escríbenos y lo verificamos en el momento.",
        "cuerpo": """
        <p>
          La galería de <strong>Calle 77 con Av. Bella Vista</strong> es la
          ubicación más grande de la red 1PIXEL:
          <strong>24 de nuestras 92 pantallas</strong> están aquí. Es el punto
          con más pantallas de toda la red, y la razón es simple: es donde pasa
          más gente.
        </p>
"""
        + datos(
            ("24", "Pantallas LED"), ("24/7", "Transmisión"), ("15", "Marcas máximo")
        )
        + video("calle-77-bella-vista")
        + """

        <h2>La zona</h2>
        <p>
          Bella Vista es uno de los ejes comerciales históricos de Maracaibo, y
          su cruce con la Calle 77 concentra a la vez tráfico vehicular de paso
          y tráfico peatonal de compra. Esa combinación es poco común: la
          mayoría de los puntos de la ciudad tiene uno u otro.
        </p>
        <p>
          Para una marca eso significa dos tipos de exposición en la misma
          ubicación. El que va manejando registra la marca de reojo; el que
          entra a la galería la ve varias veces mientras camina, en las
          pantallas de entrada y de pasillo.
        </p>

        <h2>Perfil de visitante</h2>
        <p>
          El visitante típico es comercio general: gente que entra a resolver
          una compra concreta y aprovecha para ver otras cosas. El flujo se
          mantiene a lo largo del día, sin el pico marcado que sí tienen otras
          galerías de la red.
        </p>

        <h2>Por qué concentramos 24 pantallas acá</h2>
        <p>
          Poner más de la mitad de la red en un solo punto no fue por
          disponibilidad, fue por criterio. En publicidad exterior el factor que
          más pesa no es cuántas pantallas tienes repartidas, sino cuántas veces
          la misma persona ve tu anuncio. Con 24 pantallas cubriendo entrada,
          pasillos y zonas de circulación, un visitante se cruza con tu marca
          varias veces en una sola visita, sin que el anuncio se vuelva
          invasivo.
        </p>
        <p>
          Esa densidad es la que convierte una visita casual en recordación
          real. Es también la razón por la que esta galería es la primera
          recomendación para marcas que están arrancando su presencia en
          Maracaibo y necesitan volumen antes que segmentación fina.
        </p>

        <h2>Ritmo de la galería durante el día</h2>
        <p>
          A diferencia de las otras dos ubicaciones de la red, acá el flujo no
          tiene un pico único: se sostiene durante toda la jornada comercial.
          Para el anunciante eso significa que no hace falta pensar el mensaje
          en función de un horario —lo que sí conviene hacer en el
          <a href="/galerias/corredor-gastronomico-3h/">Corredor Gastronómico</a>,
          donde el grueso del público llega de noche.
        </p>

        <h2>¿Qué rubros funcionan mejor aquí?</h2>
        <p>
          Por volumen y por perfil, esta galería rinde bien para marcas de
          <strong>consumo masivo</strong> —las que necesitan estar en la cabeza
          de mucha gente— y para comercios que quieren captar clientes de toda
          la ciudad, no solo del sector. Entre las marcas que han pautado en la
          red están """
        + MARCAS
        + """.
        </p>
        <p>
          Si tu negocio depende de un público de una zona específica y no de
          volumen general, puede convenirte más
          <a href="/galerias/cecilio-acosta/">Cecilio Acosta</a> o el
          <a href="/galerias/corredor-gastronomico-3h/"
            >Corredor Gastronómico 3H</a
          >, que tienen públicos más definidos.
        </p>

        <h2>Cómo contratar en esta galería</h2>
        <p>
          Puedes contratar solo esta galería o combinarla con las otras dos. El
          contrato mínimo es de tres meses, incluye dos cambios de contenido al
          mes y tu anuncio sale al aire en menos de 48 horas desde que nos
          mandas el arte. El detalle completo está en
          <a href="/alquiler-pantallas-led-maracaibo/"
            >la página de alquiler</a
          >.
        </p>
""",
        "relacionados": [
            ("/galerias/cecilio-acosta/", "Galería de Cecilio Acosta (12 pantallas)"),
            (
                "/galerias/corredor-gastronomico-3h/",
                "Corredor Gastronómico 3H (8 pantallas)",
            ),
            ("/alquiler-pantallas-led-maracaibo/", "Cómo contratar"),
        ],
    },
    {
        "slug": "galerias/cecilio-acosta",
        "title": "Pantallas LED en Cecilio Acosta, Calle 67, Maracaibo | 1PIXEL",
        "description": "12 pantallas LED publicitarias en la galería de Cecilio Acosta, Calle 67, Maracaibo. Doble turno: comercio de día y zona gastronómica de noche.",
        "h1": "Pantallas LED en Cecilio Acosta",
        "breadcrumb": '<a href="/pantallas-led-maracaibo/">Pantallas LED</a><span>/</span>Cecilio Acosta',
        "bajada": "12 pantallas en la Calle 67. La galería de doble turno de la red: vida comercial durante el día y movimiento gastronómico en la noche.",
        "cta_titulo": "Reserva tu espacio en Cecilio Acosta",
        "cta_texto": "12 pantallas, máximo 15 marcas y exclusividad por subrubro. Escríbenos y verificamos disponibilidad para tu categoría.",
        "cuerpo": """
        <p>
          La galería de <strong>Cecilio Acosta, en la Calle 67</strong>, tiene
          <strong>12 pantallas LED</strong> de la red 1PIXEL. Lo que la
          distingue no es el tamaño sino el ritmo: es la única ubicación de la
          red con dos picos de tráfico claramente distintos en el mismo día.
        </p>
"""
        + datos(
            ("12", "Pantallas LED"), ("2", "Picos diarios"), ("15", "Marcas máximo")
        )
        + video("cecilio-acosta")
        + """

        <h2>La zona</h2>
        <p>
          Cecilio Acosta es una avenida con identidad doble. De día funciona
          como corredor comercial: comercios, servicios, gente resolviendo
          diligencias. Al caer la tarde el perfil cambia y toma fuerza la
          actividad gastronómica, con un público que sale a comer y a pasar el
          rato.
        </p>

        <h2>Dos públicos, una misma pantalla</h2>
        <p>
          Esto tiene una implicación práctica que conviene aprovechar: el mismo
          espacio te expone a dos audiencias distintas sin pagar dos veces. Una
          marca que vende de día y de noche puede alternar el mensaje —usando
          los dos cambios de contenido mensuales incluidos— para hablarle a cada
          público en su momento.
        </p>
        <p>
          Y una marca que solo le vende a uno de los dos sigue estando presente
          para el otro, que es exactamente cómo se construye recordación en
          publicidad exterior.
        </p>

        <h2>Cómo aprovechar los dos turnos</h2>
        <p>
          El contrato incluye dos cambios de contenido al mes, y esta es la
          galería donde esa flexibilidad más se nota. Algunas formas concretas
          de usarla:
        </p>
        <ul>
          <li>
            <strong>Alternar mensaje por temporada del mes.</strong> Una
            quincena empujando el producto de día, la otra el de noche.
          </li>
          <li>
            <strong>Probar dos propuestas.</strong> Cambia el arte a mitad de
            mes y compara la respuesta que llega por WhatsApp. No es medición
            exacta, pero es más de lo que da una lona impresa.
          </li>
          <li>
            <strong>Acompañar la agenda del local.</strong> Si tienes promoción
            de fin de semana o un evento puntual, el arte puede reflejarlo en
            vez de quedarse genérico todo el trimestre.
          </li>
        </ul>

        <h2>Una ubicación de escala media</h2>
        <p>
          Con 12 pantallas, esta galería está entre las 24 de
          <a href="/galerias/calle-77-bella-vista/">Calle 77 con Bella Vista</a>
          y las 8 del
          <a href="/galerias/corredor-gastronomico-3h/">Corredor Gastronómico</a>.
          En la práctica es un buen punto de entrada para marcas que quieren
          presencia sólida sin comprometerse con el volumen de la galería
          principal, y para negocios de la zona cuyo cliente es del sector.
        </p>

        <h2>¿Qué rubros funcionan mejor aquí?</h2>
        <p>
          Rinde bien para <strong>restaurantes y marcas de consumo nocturno</strong>,
          que encuentran a su público justo cuando está decidiendo dónde comer,
          y para <strong>comercios y servicios de la zona</strong>, que captan
          al visitante diurno. También funciona para bancos, clínicas y
          concesionarios que buscan presencia sostenida frente a un público
          local recurrente.
        </p>

        <h2>Cómo contratar en esta galería</h2>
        <p>
          Aplican las mismas condiciones que en el resto de la red: contrato
          desde tres meses, máximo 15 marcas por galería, exclusividad por
          subrubro, dos cambios de contenido al mes y salida al aire en menos de
          48 horas. Puedes ver el proceso completo en
          <a href="/alquiler-pantallas-led-maracaibo/"
            >la página de alquiler de pantallas LED</a
          >.
        </p>
""",
        "relacionados": [
            (
                "/galerias/calle-77-bella-vista/",
                "Calle 77 con Bella Vista (24 pantallas)",
            ),
            (
                "/galerias/corredor-gastronomico-3h/",
                "Corredor Gastronómico 3H (8 pantallas)",
            ),
            ("/pantallas-led-maracaibo/", "Toda la red de pantallas LED"),
        ],
    },
    {
        "slug": "galerias/corredor-gastronomico-3h",
        "title": "Pantallas LED en el Corredor Gastronómico AV 3H, Maracaibo | 1PIXEL",
        "description": "8 pantallas LED publicitarias en el Corredor Gastronómico de la AV 3H, Maracaibo. Público de salida nocturna, entretenimiento y punto de encuentro.",
        "h1": "Pantallas LED en el Corredor Gastronómico AV 3H",
        "breadcrumb": '<a href="/pantallas-led-maracaibo/">Pantallas LED</a><span>/</span>Corredor Gastronómico 3H',
        "bajada": "8 pantallas en la AV 3H. La ubicación de público nocturno de la red: gente que salió a comer, a encontrarse y a pasar el rato.",
        "cta_titulo": "Habla con el público de la noche",
        "cta_texto": "8 pantallas en el punto de encuentro de la AV 3H. Escríbenos para verificar si tu subrubro está libre.",
        "cuerpo": """
        <p>
          El <strong>Corredor Gastronómico de la AV 3H</strong> tiene
          <strong>8 pantallas LED</strong> de la red 1PIXEL. Es la ubicación más
          pequeña en número de pantallas y la más definida en cuanto a público:
          acá la gente no viene a hacer diligencias, viene a salir.
        </p>
"""
        + datos(
            ("8", "Pantallas LED"),
            ("Noche", "Pico de tráfico"),
            ("15", "Marcas máximo"),
        )
        + video("corredor-gastronomico-3h")
        + """

        <h2>La zona</h2>
        <p>
          La AV 3H se consolidó como corredor gastronómico y punto de encuentro
          de Maracaibo. Es una zona de entretenimiento: restaurantes, sitios
          para sentarse, gente que se queda. El tráfico se concentra en la
          tarde-noche y sostiene un ritmo alto hasta tarde.
        </p>

        <h2>Por qué el horario nocturno juega a favor</h2>
        <p>
          Hay dos razones concretas por las que una pantalla LED rinde
          especialmente de noche en esta zona:
        </p>
        <ul>
          <li>
            <strong>La pantalla tiene luz propia.</strong> De noche, cuando el
            entorno está oscuro, una pantalla LED es lo más brillante de la
            escena. Una valla impresa, en cambio, depende de la iluminación que
            le pongan.
          </li>
          <li>
            <strong>La gente está detenida, no de paso.</strong> Quien está
            esperando mesa o conversando afuera de un local tiene tiempo real de
            mirar. Eso permite mensajes un poco menos telegráficos que en un
            punto de circulación rápida.
          </li>
        </ul>

        <h2>Ocho pantallas: por qué el tamaño no es el punto</h2>
        <p>
          Es la ubicación más pequeña de la red y aun así la más específica. En
          publicidad exterior, ocho pantallas frente al público correcto valen
          más que veinte frente al equivocado: lo que determina el resultado es
          quién pasa y en qué estado de ánimo, no cuántos metros de LED hay
          instalados.
        </p>
        <p>
          Acá el público llegó por voluntad propia, se va a quedar un rato y
          está en modo consumo. Para una marca de bebidas o de comida, ese
          contexto es difícil de comprar en otro lado de la ciudad.
        </p>

        <h2>Qué mensaje funciona en este punto</h2>
        <p>
          Como la gente está detenida y no de paso, aguanta un mensaje un poco
          más elaborado que el que sirve en un pasillo de circulación rápida.
          Aun así, las reglas del formato se mantienen: sin audio, con la marca
          visible desde el inicio y con contraste alto —de noche la pantalla es
          lo más brillante del entorno, y eso perdona menos los grises medios.
        </p>
        <p>
          Lo que mejor rinde acá es lo que conecta con el momento: si la persona
          está por decidir qué toma o dónde come, tu anuncio compite en ese
          instante exacto, no en abstracto.
        </p>

        <h2>¿Qué rubros funcionan mejor aquí?</h2>
        <p>
          Es la ubicación natural para <strong>marcas de bebidas, alimentos y
          consumo nocturno</strong> —están frente a su público justo en el
          momento de consumo— y para
          <strong>entretenimiento, eventos y servicios dirigidos a público
          joven</strong>. También funciona para negocios de la zona que quieren
          que el visitante los tenga presentes en su próxima salida.
        </p>
        <p>
          Si lo que buscas es volumen general de ciudad más que un público
          definido, conviene mirar
          <a href="/galerias/calle-77-bella-vista/"
            >Calle 77 con Bella Vista</a
          >, que concentra 24 pantallas.
        </p>

        <h2>Cómo contratar en esta galería</h2>
        <p>
          Contrato desde tres meses, máximo 15 marcas, exclusividad por
          subrubro, dos cambios de contenido al mes incluidos y salida al aire
          en menos de 48 horas. El detalle está en
          <a href="/alquiler-pantallas-led-maracaibo/"
            >la página de alquiler</a
          >.
        </p>
""",
        "relacionados": [
            (
                "/galerias/calle-77-bella-vista/",
                "Calle 77 con Bella Vista (24 pantallas)",
            ),
            ("/galerias/cecilio-acosta/", "Cecilio Acosta (12 pantallas)"),
            ("/pantallas-led-maracaibo/", "Toda la red de pantallas LED"),
        ],
    },
    {
        "slug": "galerias/calle-77-delicias",
        "title": "Pantallas LED en Calle 77 con Delicias, Maracaibo | 1PIXEL",
        "description": "24 pantallas LED publicitarias en Calle 77 con Av. Las Delicias, Maracaibo. Uno de los cruces de mayor flujo vehicular del norte de la ciudad.",
        "h1": "Pantallas LED en Calle 77 con Delicias",
        "breadcrumb": '<a href="/pantallas-led-maracaibo/">Pantallas LED</a><span>/</span>Calle 77 con Delicias',
        "bajada": "24 pantallas en el cruce que conecta las zonas residenciales del norte con el eje comercial de la ciudad. Volumen alto de tráfico vehicular durante todo el día.",
        "cta_titulo": "Reserva tu espacio en Calle 77 con Delicias",
        "cta_texto": "24 pantallas, máximo 15 marcas y exclusividad por subrubro. Escríbenos y verificamos si tu categoría sigue libre.",
        "cuerpo": """
        <p>
          El cruce de <strong>Calle 77 con Av. Las Delicias</strong> es, junto a
          Calle 77 con Bella Vista, una de las dos ubicaciones más grandes de la
          red: <strong>24 pantallas LED</strong>. Es el punto donde el norte
          residencial de Maracaibo se conecta con el eje comercial, y por ahí
          pasa a diario buena parte de la ciudad.
        </p>
"""
        + datos(
            ("24", "Pantallas LED"), ("24/7", "Transmisión"), ("15", "Marcas máximo")
        )
        + video("calle-77-delicias")
        + """

        <h2>La zona</h2>
        <p>
          Las Delicias es una de las avenidas que estructura el movimiento del
          norte de Maracaibo. Quien vive en las urbanizaciones de esa zona la usa
          para bajar al centro comercial y de servicios, y quien trabaja en el
          eje comercial la usa para volver. El resultado es un flujo que no
          depende de una hora pico única: se sostiene durante casi todo el día.
        </p>

        <h2>Perfil del público</h2>
        <p>
          Predomina el <strong>tráfico vehicular</strong>, con un componente
          peatonal fuerte en los comercios del cruce. Es un público de poder
          adquisitivo medio y medio-alto, que se mueve por rutina: pasa por el
          mismo punto varias veces a la semana. Esa repetición es justamente lo
          que hace que la publicidad exterior funcione.
        </p>

        <h2>¿Qué rubros funcionan mejor aquí?</h2>
        <p>
          Rinde para <strong>consumo masivo, concesionarios, inmobiliarias,
          clínicas y bancos</strong>, que buscan recordación de marca a escala de
          ciudad, y para comercios de la zona que quieren capturar al vecino en
          su trayecto diario.
        </p>

        <h2>Volumen comparado con el resto de la red</h2>
        <p>
          Con 24 pantallas está a la par de
          <a href="/galerias/calle-77-bella-vista/">Calle 77 con Bella Vista</a>
          y por encima de
          <a href="/galerias/cecilio-acosta/">Cecilio Acosta</a> (12) o del
          <a href="/galerias/corredor-gastronomico-3h/">Corredor Gastronómico</a>
          (8). Si tu objetivo es volumen y no un nicho específico, esta y Bella
          Vista son las dos ubicaciones a considerar primero.
        </p>

        <h2>Cómo contratar en esta galería</h2>
        <p>
          Mismas condiciones que en el resto de la red: contrato desde tres
          meses, máximo 15 marcas por galería, exclusividad por subrubro, dos
          cambios de contenido al mes y salida al aire en menos de 48 horas.
          Puedes ver el proceso completo en
          <a href="/alquiler-pantallas-led-maracaibo/"
            >la página de alquiler de pantallas LED</a
          >.
        </p>
""",
        "relacionados": [
            (
                "/galerias/calle-77-bella-vista/",
                "Calle 77 con Bella Vista (24 pantallas)",
            ),
            ("/galerias/vereda-del-lago/", "Vereda del Lago (12 pantallas)"),
            ("/pantallas-led-maracaibo/", "Toda la red de pantallas LED"),
        ],
    },
    {
        "slug": "galerias/bella-vista-calle-72",
        "title": "Pantallas LED en Av. Bella Vista con Calle 72, Maracaibo | 1PIXEL",
        "description": "12 pantallas LED publicitarias en Av. Bella Vista con Calle 72, Maracaibo. Corredor comercial y bancario con flujo vehicular continuo.",
        "h1": "Pantallas LED en Bella Vista con Calle 72",
        "breadcrumb": '<a href="/pantallas-led-maracaibo/">Pantallas LED</a><span>/</span>Bella Vista con Calle 72',
        "bajada": "12 pantallas sobre la avenida Bella Vista, en el corredor comercial y bancario de Maracaibo. Tránsito constante, público de rutina.",
        "cta_titulo": "Reserva tu espacio en Bella Vista con Calle 72",
        "cta_texto": "12 pantallas, máximo 15 marcas y exclusividad por subrubro. Escríbenos y lo verificamos en el momento.",
        "cuerpo": """
        <p>
          La galería de <strong>Av. Bella Vista con Calle 72</strong> tiene
          <strong>12 pantallas LED</strong> sobre uno de los ejes más
          reconocidos de Maracaibo. Bella Vista es la avenida que la ciudad usa
          para casi todo: comercio, bancos, oficinas y tránsito de paso.
        </p>
"""
        + datos(
            ("12", "Pantallas LED"), ("24/7", "Transmisión"), ("15", "Marcas máximo")
        )
        + video("bella-vista-calle-72")
        + """

        <h2>La zona</h2>
        <p>
          El tramo de la Calle 72 concentra agencias bancarias, comercios y
          servicios profesionales. Es una zona de diligencias: la gente va a un
          trámite concreto, estaciona, camina un par de cuadras y vuelve. Ese
          patrón produce exposición repetida dentro de la misma visita.
        </p>

        <h2>Perfil del público</h2>
        <p>
          Público adulto, económicamente activo, en horario diurno sobre todo.
          Mezcla de residentes de la zona norte y de gente que baja a resolver
          gestiones bancarias o comerciales. Es una audiencia menos impulsiva que
          la de una zona de entretenimiento, y más receptiva a mensajes de
          servicio, salud, finanzas y hogar.
        </p>

        <h2>¿Qué rubros funcionan mejor aquí?</h2>
        <p>
          Funciona para <strong>servicios financieros, seguros, clínicas,
          farmacias, ópticas, inmobiliarias y comercios del corredor</strong>.
          También para marcas de consumo que quieren estar frente a un público
          adulto con capacidad de compra, en un entorno de baja saturación
          publicitaria digital.
        </p>

        <h2>Cuándo conviene esta galería</h2>
        <p>
          Es una ubicación de escala media, igual que
          <a href="/galerias/cecilio-acosta/">Cecilio Acosta</a> y
          <a href="/galerias/vereda-del-lago/">Vereda del Lago</a>. Conviene
          cuando tu cliente es de la zona o cuando quieres presencia sostenida
          sin el volumen —ni el costo— de las galerías de 24 pantallas. Muchas
          marcas la combinan con
          <a href="/galerias/calle-77-bella-vista/">Calle 77 con Bella Vista</a>
          para cubrir el eje completo.
        </p>

        <h2>Cómo contratar en esta galería</h2>
        <p>
          Contrato desde tres meses, máximo 15 marcas por galería, exclusividad
          por subrubro, dos cambios de contenido al mes y salida al aire en menos
          de 48 horas. El proceso completo está en
          <a href="/alquiler-pantallas-led-maracaibo/"
            >la página de alquiler de pantallas LED</a
          >.
        </p>
""",
        "relacionados": [
            (
                "/galerias/calle-77-bella-vista/",
                "Calle 77 con Bella Vista (24 pantallas)",
            ),
            ("/galerias/cecilio-acosta/", "Cecilio Acosta (12 pantallas)"),
            ("/pantallas-led-maracaibo/", "Toda la red de pantallas LED"),
        ],
    },
    {
        "slug": "galerias/vereda-del-lago",
        "title": "Pantallas LED en Vereda del Lago, Maracaibo | 1PIXEL",
        "description": "12 pantallas LED publicitarias en la avenida principal de Vereda del Lago, Maracaibo. Público familiar, deportivo y recreativo con picos de tarde y fin de semana.",
        "h1": "Pantallas LED en Vereda del Lago",
        "breadcrumb": '<a href="/pantallas-led-maracaibo/">Pantallas LED</a><span>/</span>Vereda del Lago',
        "bajada": "12 pantallas en la avenida principal del parque más visitado de Maracaibo. Público familiar y deportivo, con picos de tarde y de fin de semana.",
        "cta_titulo": "Reserva tu espacio en Vereda del Lago",
        "cta_texto": "12 pantallas, máximo 15 marcas y exclusividad por subrubro. Escríbenos y verificamos disponibilidad para tu categoría.",
        "cuerpo": """
        <p>
          La galería de <strong>Vereda del Lago</strong> tiene
          <strong>12 pantallas LED</strong> sobre la avenida principal del
          parque recreativo más visitado de Maracaibo. Es la ubicación con el
          público más distinto de toda la red: no va de paso ni a comprar, va a
          pasar el rato.
        </p>
"""
        + datos(
            ("12", "Pantallas LED"), ("24/7", "Transmisión"), ("15", "Marcas máximo")
        )
        + video("vereda-del-lago")
        + """

        <h2>La zona</h2>
        <p>
          Vereda del Lago concentra actividad deportiva en la mañana y en la
          tarde, y actividad familiar y recreativa en las tardes y los fines de
          semana. El movimiento no sigue el calendario laboral: los picos más
          altos son sábado y domingo, justo cuando otras ubicaciones bajan.
        </p>

        <h2>Perfil del público</h2>
        <p>
          Familias, corredores, ciclistas y grupos de amigos. Gente que está
          <strong>caminando o detenida</strong>, no manejando, con tiempo real
          de mirar una pantalla completa en lugar de captarla dos segundos. Es
          el tipo de atención que ninguna valla de avenida puede ofrecer.
        </p>

        <h2>¿Qué rubros funcionan mejor aquí?</h2>
        <p>
          Rinde para <strong>marcas de consumo, bebidas, comida, deporte, salud,
          educación y entretenimiento familiar</strong>, y para eventos con fecha
          —un concierto, una feria, una apertura— porque el público está en modo
          ocio y receptivo a planes.
        </p>

        <h2>La galería que completa la semana</h2>
        <p>
          Su valor real aparece al combinarla. Las galerías comerciales como
          <a href="/galerias/calle-77-bella-vista/">Calle 77 con Bella Vista</a>
          o
          <a href="/galerias/bella-vista-calle-72/">Bella Vista con Calle 72</a>
          rinden de lunes a viernes; Vereda del Lago cubre el fin de semana.
          Para una marca de consumo masivo, esa combinación cierra los siete
          días.
        </p>

        <h2>Cómo contratar en esta galería</h2>
        <p>
          Contrato desde tres meses, máximo 15 marcas por galería, exclusividad
          por subrubro, dos cambios de contenido al mes y salida al aire en menos
          de 48 horas. Puedes ver el proceso completo en
          <a href="/alquiler-pantallas-led-maracaibo/"
            >la página de alquiler de pantallas LED</a
          >.
        </p>
""",
        "relacionados": [
            ("/galerias/calle-77-delicias/", "Calle 77 con Delicias (24 pantallas)"),
            (
                "/galerias/corredor-gastronomico-3h/",
                "Corredor Gastronómico 3H (8 pantallas)",
            ),
            ("/pantallas-led-maracaibo/", "Toda la red de pantallas LED"),
        ],
    },
    {
        "slug": "nosotros",
        "title": "Quiénes Somos: la Red de Pantallas LED de Maracaibo | 1PIXEL",
        "description": "1PIXEL es la red de pantallas LED publicitarias más grande de Maracaibo, parte de Liberti Global Corporation. Conoce cómo operamos y en qué nos comprometemos.",
        "h1": "Quiénes somos",
        "breadcrumb": "Nosotros",
        "bajada": "1PIXEL es la red de pantallas LED publicitarias más grande de Maracaibo. Esto es lo que operamos, cómo lo operamos y qué le garantizamos a una marca que entra.",
        "cta_titulo": "Hablemos de tu marca",
        "cta_texto": "Escríbenos y te decimos con franqueza si nuestra red te sirve o si te conviene otro canal.",
        "cuerpo": """
        <p>
          <strong>1PIXEL</strong> opera una red de 92 pantallas LED
          publicitarias en seis galerías comerciales de Maracaibo, estado Zulia.
          Somos parte de
          <a href="https://liberticorporation.com" target="_blank" rel="noopener"
            >Liberti Global Corporation</a
          >, un holding con sede en Maracaibo.
        </p>
"""
        + datos(
            ("92", "Pantallas LED"),
            ("6", "Galerías activas"),
            ("24/7", "Transmisión"),
            ("18", "Marcas anunciantes"),
        )
        + """

        <h2>Qué operamos</h2>
        <p>
          No somos una agencia que revende espacios de terceros: la red es
          nuestra. Instalamos las pantallas, mantenemos los equipos, cargamos el
          contenido y respondemos cuando algo falla. Eso significa que cuando
          una pantalla se apaga, no hay a quién echarle la culpa —nos toca a
          nosotros arreglarla.
        </p>
        <p>
          Por eso mantenemos <strong>stock para reposición inmediata</strong> y
          servicio técnico local. En Venezuela, donde la continuidad eléctrica y
          la disponibilidad de repuestos no son un dato menor, esa es la
          diferencia entre una red que funciona y una que existe en el papel.
        </p>

        <h2>Nuestras ubicaciones</h2>
        <div class="tabla-wrap">
          <table>
            <thead>
              <tr>
                <th>Galería</th>
                <th>Pantallas</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <a href="/galerias/calle-77-bella-vista/"
                    >Calle 77 con Bella Vista</a
                  >
                </td>
                <td>24</td>
                <td>Activa</td>
              </tr>
              <tr>
                <td><a href="/galerias/cecilio-acosta/">Cecilio Acosta</a></td>
                <td>12</td>
                <td>Activa</td>
              </tr>
              <tr>
                <td>
                  <a href="/galerias/corredor-gastronomico-3h/"
                    >Corredor Gastronómico AV 3H</a
                  >
                </td>
                <td>8</td>
                <td>Activa</td>
              </tr>
              <tr>
                <td>
                  <a href="/galerias/calle-77-delicias/"
                    >Calle 77 con Delicias</a
                  >
                </td>
                <td>24</td>
                <td>Activa</td>
              </tr>
              <tr>
                <td>
                  <a href="/galerias/bella-vista-calle-72/"
                    >Av. Bella Vista con Calle 72</a
                  >
                </td>
                <td>12</td>
                <td>Activa</td>
              </tr>
              <tr>
                <td>
                  <a href="/galerias/vereda-del-lago/">Vereda del Lago</a>
                </td>
                <td>12</td>
                <td>Activa</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2>En qué nos comprometemos</h2>
        <ul>
          <li>
            <strong>Máximo 15 marcas por galería.</strong> No metemos más
            anunciantes de los que la rotación aguanta, aunque haya demanda.
          </li>
          <li>
            <strong>Exclusividad por subrubro.</strong> Si tu marca está en una
            galería, tu competencia directa no entra a esa galería.
          </li>
          <li>
            <strong>Dos cambios de contenido al mes</strong>, sin costo
            adicional.
          </li>
          <li>
            <strong>Menos de 48 horas</strong> desde que recibimos el arte hasta
            que sale al aire.
          </li>
          <li>
            <strong>Reposición inmediata.</strong> Si una pantalla falla, se
            reemplaza; no se descuenta y ya.
          </li>
        </ul>

        <h2>Las marcas que confían en la red</h2>
        <p>
          Han pautado con nosotros """
        + MARCAS
        + """. Conviven marcas nacionales de consumo masivo con comercios
          locales, que es justamente el punto del formato: el costo de entrada
          permite que ambos estén en la misma pantalla.
        </p>

        <h2>Cómo trabajamos con una marca nueva</h2>
        <p>
          Antes de cotizar preguntamos dos cosas: a quién le vendes y en qué
          zona está. Con eso te decimos cuál galería te conviene —o si ninguna
          te conviene. Si tu público no está en nuestras galerías, preferimos
          decírtelo antes que venderte tres meses de pauta que no te van a
          rendir.
        </p>
        <p>
          Si quieres ver cómo funciona el formato en detalle, empieza por
          <a href="/pantallas-led-maracaibo/">la red de pantallas LED</a> o por
          <a href="/publicidad-dooh-venezuela/"
            >la guía de publicidad DOOH en Venezuela</a
          >.
        </p>
""",
        "relacionados": [
            ("/pantallas-led-maracaibo/", "La red de 92 pantallas LED"),
            ("/alquiler-pantallas-led-maracaibo/", "Cómo se contrata"),
            ("/publicidad-dooh-venezuela/", "Guía de publicidad DOOH"),
        ],
    },
]


# --------------------------------------------------------------------------
# Generacion
# --------------------------------------------------------------------------


def extraer_css_del_index():
    ruta = os.path.join(RAIZ, "index.html")
    with open(ruta, encoding="utf-8") as fh:
        contenido = fh.read()
    m = re.search(r"<style>\n(.*?)\n\s*</style>", contenido, re.S)
    if not m:
        sys.exit("ERROR: no se encontro el bloque <style> en index.html")
    return m.group(1)


def jsonld_de(pagina, url):
    grafo = [
        {
            "@type": "WebPage",
            "@id": url + "#webpage",
            "url": url,
            "name": pagina["title"],
            "description": pagina["description"],
            "inLanguage": "es-VE",
            "dateModified": HOY,
            "isPartOf": {"@id": DOMINIO + "/#website"},
            "about": {"@id": DOMINIO + "/#business"},
            "publisher": {"@id": DOMINIO + "/#business"},
        },
        {
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": nombre,
                    "item": destino,
                }
                for i, (nombre, destino) in enumerate(pagina["ruta"])
            ],
        },
    ]
    if pagina.get("servicio"):
        grafo.append(pagina["servicio"])
    doc = {"@context": "https://schema.org", "@graph": grafo}
    texto = json.dumps(doc, ensure_ascii=False, indent=2)
    return "\n".join("      " + linea for linea in texto.split("\n"))


def ruta_breadcrumb(pagina, url):
    ruta = [("Inicio", DOMINIO + "/")]
    if pagina["slug"].startswith("galerias/"):
        ruta.append(
            ("Pantallas LED en Maracaibo", DOMINIO + "/pantallas-led-maracaibo/")
        )
    ruta.append((pagina["h1"], url))
    return ruta


def bloque_relacionados(enlaces):
    if not enlaces:
        return ""
    items = "\n".join(
        '            <li><a href="%s">%s</a></li>' % (destino, html.escape(texto))
        for destino, texto in enlaces
    )
    return (
        '        <nav class="enlaces-relacionados" aria-label="Contenido relacionado">\n'
        "          <h2>Sigue leyendo</h2>\n"
        "          <ul>\n%s\n          </ul>\n        </nav>" % items
    )


def generar():
    css = extraer_css_del_index() + CSS_PAGINAS
    destino_css = os.path.join(RAIZ, "assets")
    os.makedirs(destino_css, exist_ok=True)
    with open(os.path.join(destino_css, "site.css"), "w", encoding="utf-8") as fh:
        fh.write(css)
    print("assets/site.css  (%d KB)" % (len(css) // 1024))

    urls = [DOMINIO + "/"]
    for pagina in PAGINAS:
        url = "%s/%s/" % (DOMINIO, pagina["slug"])
        pagina["ruta"] = ruta_breadcrumb(pagina, url)

        breadcrumb_final = pagina.get("breadcrumb", pagina["h1"])
        if "<a" not in breadcrumb_final:
            breadcrumb_final = html.escape(breadcrumb_final)

        # Sustitucion literal, no str.format: la plantilla lleva JavaScript
        # con llaves y format se atraganta con ellas.
        campos = {
            "title": html.escape(pagina["title"]),
            "description": html.escape(pagina["description"]),
            "url": url,
            "h1": html.escape(pagina["h1"]),
            "bajada": html.escape(pagina["bajada"]),
            "breadcrumb_final": breadcrumb_final,
            "cuerpo": pagina["cuerpo"].rstrip(),
            "cta_titulo": html.escape(pagina["cta_titulo"]),
            "cta_texto": html.escape(pagina["cta_texto"]),
            "relacionados": bloque_relacionados(pagina.get("relacionados")),
            "jsonld": jsonld_de(pagina, url),
            "og_type": (
                "article"
                if pagina["slug"] == "publicidad-dooh-venezuela"
                else "website"
            ),
            "DOMINIO": DOMINIO,
            "WA": WA,
        }
        salida = PLANTILLA
        for clave, valor in campos.items():
            salida = salida.replace("{" + clave + "}", valor)
        salida = salida.replace('{{"token"', '{"token"').replace('"}}', '"}')
        sobrantes = re.findall(
            r"\{(title|description|url|h1|bajada|cuerpo|jsonld)\}", salida
        )
        if sobrantes:
            sys.exit(
                "ERROR: placeholders sin sustituir en %s: %s"
                % (pagina["slug"], sobrantes)
            )

        carpeta = os.path.join(RAIZ, pagina["slug"])
        os.makedirs(carpeta, exist_ok=True)
        with open(os.path.join(carpeta, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(salida)

        palabras = len(re.sub(r"<[^>]+>", " ", pagina["cuerpo"]).split())
        print("%-42s %4d palabras" % (pagina["slug"] + "/index.html", palabras))
        urls.append(url)

    urls.extend(urls_del_blog())
    escribir_sitemap(urls)


def urls_del_blog():
    """El blog lo genera otro proyecto (blog-seo-holding). Se descubre por
    disco para que este script no le borre las URLs del sitemap."""
    carpeta = os.path.join(RAIZ, "blog")
    if not os.path.isdir(carpeta):
        return []
    encontradas = [DOMINIO + "/blog/"]
    for nombre in sorted(os.listdir(carpeta)):
        if nombre.endswith(".html") and nombre != "index.html":
            encontradas.append("%s/blog/%s" % (DOMINIO, nombre))
    print("blog            (%d URLs descubiertas)" % len(encontradas))
    return encontradas


def escribir_sitemap(urls):
    filas = []
    for url in urls:
        prioridad = (
            "1.0" if url == DOMINIO + "/" else ("0.7" if "/galerias/" in url else "0.8")
        )
        filas.append(
            "  <url>\n"
            "    <loc>%s</loc>\n"
            "    <lastmod>%s</lastmod>\n"
            "    <changefreq>monthly</changefreq>\n"
            "    <priority>%s</priority>\n"
            "  </url>" % (url, HOY, prioridad)
        )
    contenido = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "%s\n</urlset>\n" % "\n".join(filas)
    )
    with open(os.path.join(RAIZ, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(contenido)
    print("sitemap.xml      (%d URLs)" % len(urls))


if __name__ == "__main__":
    generar()
