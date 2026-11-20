/* Menú móvil y refresco del calendario. */
(function () {
    'use strict';

    /* --- menú ------------------------------------------------------------ */

    var toggle = document.querySelector('[data-menu-toggle]');
    var sheet = document.querySelector('[data-menu]');
    var closeButton = document.querySelector('[data-menu-close]');

    function setMenu(open) {
        if (!sheet || !toggle) return;

        sheet.hidden = !open;
        document.body.classList.toggle('menu-open', open);
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');

        if (open) {
            sheet.focus();
        } else {
            toggle.focus();
        }
    }

    if (toggle && sheet) {
        toggle.addEventListener('click', function () {
            setMenu(sheet.hidden);
        });

        if (closeButton) {
            closeButton.addEventListener('click', function () {
                setMenu(false);
            });
        }

        sheet.addEventListener('click', function (evento) {
            if (evento.target.closest('a')) setMenu(false);
        });

        document.addEventListener('keydown', function (evento) {
            if (evento.key === 'Escape' && !sheet.hidden) setMenu(false);
        });

        window.addEventListener('resize', function () {
            if (window.innerWidth > 900 && !sheet.hidden) setMenu(false);
        });
    }

    /* --- calendario ------------------------------------------------------ */

    var resultado = document.getElementById('resultado');
    if (resultado && new URLSearchParams(window.location.search).has('cancha_id')) {
        resultado.scrollIntoView({ block: 'start' });
    }

    var raiz = document.querySelector('[data-calendario]');
    if (!raiz) return;

    var api = raiz.dataset.api;
    var cancha = raiz.dataset.cancha;
    var semana = raiz.dataset.semana;
    var reservarUrl = raiz.dataset.reserva || '/reservar/';
    var aviso = document.querySelector('[data-actualizado]');

    if (!api || !cancha || !semana) return;

    function urlReserva(dia, inicio, fin) {
        var params = new URLSearchParams({
            cancha_id: cancha,
            fecha: dia,
            hora_inicio: inicio,
            hora_fin: fin
        });
        return reservarUrl + '?' + params.toString();
    }

    function pintar(celda, franja, dia) {
        celda.dataset.estado = franja.estado;
        celda.textContent = '';

        if (franja.estado === 'libre') {
            var enlace = document.createElement('a');
            enlace.className = 'cell cell--libre';
            enlace.href = urlReserva(dia, franja.inicio, franja.fin);
            enlace.setAttribute(
                'aria-label',
                'Reservar el ' + dia + ' a las ' + franja.inicio
            );
            enlace.innerHTML = '<span class="cell-text">Libre</span>'
                + '<span class="cell-plus" aria-hidden="true">+</span>';
            celda.appendChild(enlace);
            return;
        }

        var etiqueta = document.createElement('span');
        etiqueta.className = 'cell cell--' + franja.estado;

        if (franja.estado === 'ocupado') {
            etiqueta.innerHTML = '<span class="cell-text">Ocupado</span>';
        } else {
            etiqueta.innerHTML = '<span class="sr-only">Hora pasada</span>';
        }

        celda.appendChild(etiqueta);
    }

    function refrescar() {
        var url = api
            + '?cancha_id=' + encodeURIComponent(cancha)
            + '&semana=' + encodeURIComponent(semana);

        fetch(url, { headers: { 'Accept': 'application/json' } })
            .then(function (respuesta) {
                if (!respuesta.ok) throw new Error('Sin respuesta');
                return respuesta.json();
            })
            .then(function (datos) {
                (datos.dias || []).forEach(function (dia) {
                    (dia.franjas || []).forEach(function (franja) {
                        var celda = raiz.querySelector(
                            'td[data-dia="' + dia.fecha + '"][data-hora="' + franja.inicio + '"]'
                        );
                        if (celda) pintar(celda, franja, dia.fecha);
                    });
                });

                if (aviso) {
                    var hora = new Date().toLocaleTimeString('es-CO', {
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                    aviso.textContent = 'Actualizado a las ' + hora;
                }
            })
            .catch(function () {
                /* Sin conexión: se queda lo que ya está en pantalla. */
            });
    }

    window.setInterval(function () {
        if (!document.hidden) refrescar();
    }, 30000);
})();
