// ===== Interactividad de la agenda =====
const $  = (s, c = document) => c.querySelector(s);
const $$ = (s, c = document) => [...c.querySelectorAll(s)];

// 1) Notificaciones: se ocultan solas (y celebramos si se guardó)
$$('.toast').forEach(t => {
  if (t.textContent.includes('guardado')) confeti();
  setTimeout(() => t.classList.add('out'), 3500);
  setTimeout(() => t.remove(), 4200);
});

// 2) Formulario desplegable
const panel = $('#panelForm'), btnNuevo = $('#btnNuevo');
if (panel && btnNuevo) {
  btnNuevo.onclick = () => {
    const abierto = panel.classList.toggle('abierto');
    btnNuevo.textContent = abierto ? '✖ Cerrar formulario' : '➕ Nuevo contacto';
    if (abierto) setTimeout(() => $('input', panel).focus(), 300);
  };
}

// 3) Estadísticas (contador)
const tarjetas = $$('.contacto');   // <- esta línea es la que faltaba

function contar(id, total) {
  const elemento = $(id);
  if (elemento) elemento.textContent = total;
}

contar('#nTotal', tarjetas.length);

['Familia', 'Escuela', 'Trabajo', 'Otro'].forEach(categoria => {
  const cantidad = tarjetas.filter(t => {
    const cat = t.getAttribute('data-cat');
    return cat && cat.trim().toLowerCase() === categoria.toLowerCase();
  }).length;

  contar('#n' + categoria, cantidad);
});

// 4) Búsqueda y filtros en vivo
let categoria = 'Todas';
const buscar = $('#buscar');
function filtrar() {
  const q = buscar.value.toLowerCase().trim();
  let visibles = 0;
  tarjetas.forEach(t => {
    const ok = (categoria === 'Todas' || t.dataset.cat === categoria) && t.dataset.texto.includes(q);
    t.hidden = !ok;
    if (ok) visibles++;
  });
  $('#sinResultados').hidden = visibles > 0 || tarjetas.length === 0;
}
if (buscar) {
  buscar.oninput = filtrar;
  $$('.chip').forEach(ch => ch.onclick = () => {
    $$('.chip').forEach(x => x.classList.remove('activo'));
    ch.classList.add('activo');
    categoria = ch.dataset.cat;
    filtrar();
  });
}

// 5) Ventana de confirmación para eliminar
const modal = $('#modal');
let formPendiente = null;
$$('.btn-eliminar').forEach(b => b.onclick = () => {
  formPendiente = b.closest('form');
  $('#modalNombre').textContent = b.dataset.nombre;
  modal.classList.add('visible');
});
const cerrar = () => { modal.classList.remove('visible'); formPendiente = null; };
$('#no').onclick = cerrar;
$('#si').onclick = () => formPendiente && formPendiente.submit();
modal.onclick = e => { if (e.target === modal) cerrar(); };
document.onkeydown = e => { if (e.key === 'Escape') cerrar(); };

// 6) Modo oscuro (se recuerda)
const temaBtn = $('#tema');
function aplicarTema(oscuro) {
  document.body.classList.toggle('oscuro', oscuro);
  temaBtn.textContent = oscuro ? '☀️' : '🌙';
}
try { aplicarTema(localStorage.getItem('tema') === 'oscuro'); } catch (e) {}
temaBtn.onclick = () => {
  const oscuro = !document.body.classList.contains('oscuro');
  aplicarTema(oscuro);
  try { localStorage.setItem('tema', oscuro ? 'oscuro' : 'claro'); } catch (e) {}
};

// 7) Confeti
function confeti() {
  for (let i = 0; i < 26; i++) {
    const s = document.createElement('span');
    s.className = 'conf';
    s.textContent = ['⭐', '🎉', '💖', '✨', '🌈'][i % 5];
    s.style.left = Math.random() * 100 + 'vw';
    s.style.animationDelay = Math.random() * .6 + 's';
    document.body.appendChild(s);
    setTimeout(() => s.remove(), 3200);
  }
}

// 8) Vista previa de la foto antes de guardar
const inputFoto = $('#foto'), prev = $('#preview');
if (inputFoto && prev) {
  inputFoto.onchange = () => {
    const f = inputFoto.files[0];
    if (f) { prev.src = URL.createObjectURL(f); prev.hidden = false; }
  };
}

// 9) Ampliar la foto al hacer clic en el avatar
const visor = $('#visor');
$$('.avatar.con-foto').forEach(av => av.onclick = () => {
  $('#visorImg').src = $('img', av).src;
  $('#visorNombre').textContent = av.dataset.nombre;
  visor.classList.add('visible');
});
visor.onclick = () => visor.classList.remove('visible');
document.addEventListener('keydown', e => { if (e.key === 'Escape') visor.classList.remove('visible'); });