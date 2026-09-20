/* 1PIXEL advertising measurement: public marketing pages only. */
(function () {
  'use strict';
  if (window.__onePixelAdsLoaded) return;
  window.__onePixelAdsLoaded = true;
  var tagId = 'AW-18462681015';
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', tagId, { allow_enhanced_conversions: false });
  var script = document.createElement('script');
  script.async = true;
  script.src = 'https://www.googletagmanager.com/gtag/js?id=' + tagId;
  document.head.appendChild(script);
  document.addEventListener('click', function (event) {
    var element = event.target instanceof Element ? event.target : null;
    var link = element && element.closest('a[href]');
    if (!link) return;
    var url;
    try { url = new URL(link.href); } catch (_) { return; }
    if (url.protocol !== 'https:' || !['wa.me', 'api.whatsapp.com', 'web.whatsapp.com'].includes(url.hostname)) return;
    window.gtag('event', 'conversion', {
      send_to: tagId + '/g5p_CLfohv4cELfP2ONE',
      transport_type: 'beacon'
    });
  });
}());
