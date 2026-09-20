window.siteMeasurementConfig = {"name": "1PIXEL", "gaId": "G-SGJXXCCZFN", "adsId": "AW-18462681015", "whatsappConversion": "AW-18462681015/g5p_CLfohv4cELfP2ONE"};
/* Optional measurement. No Google request is made before an explicit choice. */
(function () {
  'use strict';
  if (window.siteMeasurement) return;
  var config = window.siteMeasurementConfig || {};
  var key = 'site-consent-v1';
  var consent = { analytics: false, advertising: false };
  var stored = null, loaded = false, configured = {}, lastPage = '';
  try {
    var saved = JSON.parse(localStorage.getItem(key));
    if (saved && saved.version === 1 && saved.expires > Date.now() && typeof saved.analytics === 'boolean' && typeof saved.advertising === 'boolean') stored = saved;
  } catch (_) { /* Storage blocked: default to denied. */ }
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  function tag() { window.gtag.apply(window, arguments); }
  function permissions(value) {
    return { analytics_storage: value.analytics ? 'granted' : 'denied', ad_storage: value.advertising ? 'granted' : 'denied', ad_user_data: value.advertising ? 'granted' : 'denied', ad_personalization: 'denied' };
  }
  tag('consent', 'default', permissions(consent));
  tag('set', 'ads_data_redaction', true);
  tag('set', 'url_passthrough', false);
  function cleanUrl(value) { try { var url = new URL(value); return url.origin + url.pathname; } catch (_) { return ''; } }
  function page() {
    var path = location.pathname;
    if (!consent.analytics || !config.gaId || path === lastPage) return;
    lastPage = path;
    tag('event', 'page_view', { send_to: config.gaId, page_location: cleanUrl(location.href), page_referrer: cleanUrl(document.referrer), page_title: config.name });
  }
  function start() {
    var id = consent.analytics && config.gaId || consent.advertising && config.adsId;
    if (!id) return;
    if (!loaded) { loaded = true; tag('js', new Date()); }
    if (consent.analytics && config.gaId && !configured[config.gaId]) {
      configured[config.gaId] = true;
      tag('config', config.gaId, { send_page_view: false, allow_google_signals: false, allow_ad_personalization_signals: false, page_location: cleanUrl(location.href), page_referrer: cleanUrl(document.referrer), page_title: config.name, cookie_expires: 15552000 });
    }
    if (consent.advertising && config.adsId && !configured[config.adsId]) {
      configured[config.adsId] = true;
      tag('config', config.adsId, { allow_enhanced_conversions: false, allow_ad_personalization_signals: false });
    }
    if (!document.getElementById('site-google-tag')) {
      var script = document.createElement('script'); script.id = 'site-google-tag'; script.async = true;
      script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
      document.head.appendChild(script);
    }
    page();
  }
  function event(name, method) {
    if (consent.analytics && config.gaId) tag('event', name, { send_to: config.gaId, contact_method: method, page_location: cleanUrl(location.href), page_referrer: cleanUrl(document.referrer) });
    if (name === 'contact_click' && method === 'whatsapp' && consent.advertising && config.whatsappConversion) tag('event', 'conversion', { send_to: config.whatsappConversion, transport_type: 'beacon' });
  }
  function clearCookies(next) {
    document.cookie.split(';').forEach(function (item) {
      var name = item.split('=')[0].trim();
      if (!( !next.analytics && /^_ga(?:_|$)|^_gid$|^_gat/.test(name)) && !(!next.advertising && /^_gcl_|^_gac_/.test(name))) return;
      var parts = location.hostname.split('.');
      var domains = [''];
      for (var i = 0; i < parts.length - 1; i++) domains.push(parts.slice(i).join('.'), '.' + parts.slice(i).join('.'));
      var paths = ['/']; var segments = location.pathname.split('/');
      for (var j = 1; j < segments.length; j++) paths.push(segments.slice(0, j + 1).join('/'));
      domains.forEach(function (domain) { paths.forEach(function (path) { document.cookie = name + '=; Max-Age=0; path=' + path + (domain ? '; domain=' + domain : '') + '; SameSite=Lax'; }); });
    });
  }
  function choose(next) {
    var withdrawn = loaded && ((consent.analytics && !next.analytics) || (consent.advertising && !next.advertising));
    consent = next;
    try { localStorage.setItem(key, JSON.stringify({ version: 1, analytics: next.analytics, advertising: next.advertising, expires: Date.now() + 15552000000 })); } catch (_) { /* Consent only lasts for this page when storage is unavailable. */ }
    tag('consent', 'update', permissions(consent));
    clearCookies(consent);
    close();
    document.getElementById('measurement-banner').hidden = true;
    if (withdrawn) { location.reload(); return; }
    start();
    window.dispatchEvent(new CustomEvent('site-consent-change', { detail: { analytics: consent.analytics } }));
  }
  var dialog, previousFocus;
  function close() { if (dialog && dialog.open) dialog.close(); if (previousFocus && previousFocus.isConnected) previousFocus.focus(); }
  function open() {
    previousFocus = document.activeElement;
    dialog.querySelector('[name=analytics]').checked = consent.analytics;
    dialog.querySelector('[name=advertising]').checked = consent.advertising;
    dialog.showModal();
  }
  function ui() {
    var style = document.createElement('style');
    style.textContent = '#measurement-banner,#measurement-dialog,#measurement-reopen{font:14px/1.5 system-ui,sans-serif;color:#f7f7f7;background:#16181c;box-sizing:border-box}#measurement-banner{position:fixed;left:16px;bottom:16px;z-index:2147483000;width:min(440px,calc(100vw - 32px));padding:20px;border:1px solid #777;border-radius:14px;box-shadow:0 8px 40px #0006}#measurement-banner[hidden]{display:none}#measurement-banner p,#measurement-dialog p{margin:8px 0 16px}#measurement-banner strong,#measurement-dialog h2{font-size:18px;color:#fff}#measurement-banner .choices{display:flex;gap:8px;flex-wrap:wrap}#measurement-banner button,#measurement-dialog button,#measurement-reopen{border:1px solid #999;border-radius:7px;padding:10px 14px;background:#24272c;color:white;cursor:pointer;font:inherit;min-height:44px}#measurement-banner button:focus-visible,#measurement-dialog button:focus-visible,#measurement-reopen:focus-visible{outline:3px solid #70d6ff;outline-offset:3px}#measurement-dialog{position:fixed;inset:0;margin:auto;border:1px solid #888;border-radius:16px;padding:24px;width:min(520px,calc(100vw - 32px));max-height:85vh;overflow:auto}#measurement-dialog::backdrop{background:#0009}#measurement-dialog label{display:block;padding:12px 0}#measurement-dialog input{margin-right:10px;accent-color:#70d6ff}#measurement-dialog a{color:#9cddff;text-decoration:underline}#measurement-reopen{position:fixed;left:12px;bottom:12px;z-index:2147482999;font-size:12px;padding:6px 12px}';
    document.head.appendChild(style);
    var root = document.createElement('div');
    root.innerHTML = '<button id="measurement-reopen" type="button">Cookies</button><section id="measurement-banner" aria-label="Preferencias de cookies"><strong>Tú eliges las cookies</strong><p>Con tu permiso usamos Google Analytics para conocer visitas y contactos, y Google Ads para medir resultados de anuncios. Puedes rechazar las opcionales y seguir usando la web.</p><div class="choices"><button type="button" data-choice="accept">Aceptar todas</button><button type="button" data-choice="reject">Rechazar</button><button type="button" data-choice="preferences">Preferencias</button></div></section><dialog id="measurement-dialog" aria-labelledby="measurement-title"><h2 id="measurement-title">Cookies y medición</h2><p>Las funciones necesarias del sitio siguen disponibles con cualquier elección. Guardamos tu elección en este navegador durante 180 días.</p><label><input type="checkbox" name="analytics">Analytics: visitas y contactos</label><label><input type="checkbox" name="advertising">Publicidad: atribución de Google Ads</label><p>Analytics registra páginas vistas, datos del navegador, ubicación aproximada y clics de contacto. Los formularios se cuentan únicamente cuando confirman el envío. No enviamos nombres, teléfonos, correos ni el contenido de los mensajes a Analytics. Un clic no equivale a una venta.</p><p>Google puede guardar identificadores en cookies (_ga, _gcl). Limitamos las cookies de Analytics a 180 días. No activamos personalización de anuncios ni grabaciones de sesiones. Puedes retirar tu permiso aquí; al hacerlo se recarga la página para detener las etiquetas.</p><p><a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener noreferrer">Cómo usa Google los datos</a>. Los servicios necesarios de formularios, seguridad y alojamiento procesan los datos requeridos para funcionar, independientemente de estas cookies.</p><button type="button" data-choice="save">Guardar preferencias</button> <button type="button" data-choice="close">Cerrar</button></dialog>';
    var privacy = document.createElement('a');
    privacy.href = config.privacyUrl || '/privacidad-medicion.html';
    privacy.textContent = 'Privacidad de la web';
    var privacyParagraph = document.createElement('p');
    privacyParagraph.appendChild(privacy);
    root.querySelector('#measurement-dialog').appendChild(privacyParagraph);
    document.body.appendChild(root);
    dialog = document.getElementById('measurement-dialog');
    document.getElementById('measurement-banner').hidden = !!stored;
    root.addEventListener('click', function (e) {
      var button = e.target.closest('button'); if (!button) return;
      var action = button.dataset.choice;
      if (button.id === 'measurement-reopen' || action === 'preferences') open();
      if (action === 'close') close();
      if (action === 'accept') choose({ analytics: true, advertising: true });
      if (action === 'reject') choose({ analytics: false, advertising: false });
      if (action === 'save') choose({ analytics: dialog.querySelector('[name=analytics]').checked, advertising: dialog.querySelector('[name=advertising]').checked });
    });
  }
  function contact(e) {
    if ((e.type === 'click' && e.button !== 0) || (e.type === 'auxclick' && e.button !== 1)) return;
    var element = e.target instanceof Element && e.target.closest('a[href],button[data-whatsapp-click]');
    if (!element || element.disabled || element.getAttribute('aria-disabled') === 'true') return;
    var method = element.hasAttribute('data-whatsapp-click') ? 'whatsapp' : '';
    if (!method) { try { var url = new URL(element.href); if (url.protocol === 'https:' && ['wa.me','api.whatsapp.com','web.whatsapp.com'].includes(url.hostname)) method = 'whatsapp'; else if (url.protocol === 'tel:') method = 'phone'; else if (url.protocol === 'mailto:') method = 'email'; } catch (_) { return; } }
    if (method) event('contact_click', method);
  }
  window.siteMeasurement = { page: page, analyticsAllowed: function () { return consent.analytics; } };
  document.addEventListener('click', contact, true);
  document.addEventListener('auxclick', contact, true);
  window.addEventListener('site-lead-success', function () { event('generate_lead', 'form'); });
  window.addEventListener('site-whatsapp-form', function () { event('contact_click', 'whatsapp'); });
  window.addEventListener('site-page-view', page);
  if (stored) { consent = { analytics: stored.analytics, advertising: stored.advertising }; tag('consent', 'update', permissions(consent)); start(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ui, { once: true }); else ui();
}());
