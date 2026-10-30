/* Mejoras progresivas: la web funciona sin JavaScript. */
(function () {
  'use strict';

  // Sombra en la cabecera al hacer scroll
  var header = document.querySelector('.site-header');
  if (header) {
    var onScroll = function () {
      header.setAttribute('data-scrolled', window.scrollY > 20 ? '1' : '0');
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // Formulario: envío por AJAX a FormSubmit; sin JS se envía como formulario normal.
  var form = document.querySelector('form[data-contact]');
  if (!form) return;
  var lang = document.documentElement.lang === 'en' ? 'en' : 'es';
  var to = form.getAttribute('data-to');
  var sending = false;
  var btn = form.querySelector('button[type="submit"]');
  var btnLabel = btn ? btn.textContent : '';
  var thanks = document.querySelector('[data-thanks]');
  var errBox = form.querySelector('[data-error]');

  function val(name) {
    var el = form.elements[name];
    return ((el && el.value) || '').trim();
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (sending) return;
    if (val('_honey')) return; // anti-spam: campo señuelo relleno

    var nombre = val('nombre'), empresa = val('empresa'), email = val('email'),
        linea = val('linea'), mensaje = val('mensaje');
    var subject = (lang === 'es' ? 'Consulta web — ' : 'Website enquiry — ') + (nombre || 'Zirotti');

    sending = true;
    if (btn) { btn.disabled = true; btn.textContent = lang === 'es' ? 'Enviando…' : 'Sending…'; }
    if (errBox) errBox.hidden = true;

    function done() {
      form.hidden = true;
      if (thanks) { thanks.hidden = false; thanks.focus(); }
    }

    function mailtoFallback() {
      var L = lang === 'es'
        ? { n: 'Nombre', c: 'Empresa', e: 'Email', l: 'Línea', m: 'Proyecto' }
        : { n: 'Name', c: 'Company', e: 'Email', l: 'Line', m: 'Project' };
      var body = [L.n + ': ' + nombre, L.c + ': ' + empresa, L.e + ': ' + email,
                  L.l + ': ' + linea, '', L.m + ':', mensaje].join('\n');
      window.location.href = 'mailto:' + to + '?subject=' + encodeURIComponent(subject) +
        '&body=' + encodeURIComponent(body);
      done();
    }

    fetch('https://formsubmit.co/ajax/' + to, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({
        _subject: subject, _template: 'table', _captcha: 'false',
        Nombre: nombre, Empresa: empresa, Email: email,
        'Línea de interés': linea, Proyecto: mensaje
      })
    }).then(function (r) {
      if (!r.ok) throw new Error('bad status');
      return r.json();
    }).then(done).catch(function () {
      sending = false;
      if (btn) { btn.disabled = false; btn.textContent = btnLabel; }
      mailtoFallback();
    });
  });
})();
