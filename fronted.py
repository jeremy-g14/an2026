import reflex as rx
import httpx
from typing import List

# ─────────────────────────────────────────────
#  Colores
# ─────────────────────────────────────────────
BG_DEEP   = "#060e04"
BG_DARK   = "#0a1208"
BG_MID    = "#0d1a0a"
BG_PANEL  = "#0f2a08"
BORDER    = "#1e3810"
BORDER2   = "#2a4a1a"
GREEN_LT  = "#97C459"
GREEN_MID = "#639922"
GREEN_DK  = "#3B6D11"
TEXT_PRI  = "#eaf3de"
TEXT_SEC  = "#9FE1CB"
TEXT_MUT  = "#5a8a3a"
MONO      = "monospace"

# ─────────────────────────────────────────────
#  Estado
# ─────────────────────────────────────────────
class State(rx.State):
    # Bisección
    funcion: str       = "x**2 - 5"
    a: str             = "2.0"
    b: str             = "3.0"
    tolerancia: str    = "0.001"
    max_iteraciones: str = "50"
    filas: List[List[str]] = []
    raiz: str          = ""
    error_final: str   = ""
    iter_total: str    = ""
    mensaje: str       = ""
    cargando: bool     = False
    error_ui: str      = ""
    mostrar: bool      = False

    # Secante
    funcion_sec: str   = "x**3 - x - 2"
    x0: str            = "1.0"
    x1: str            = "2.0"
    tol_sec: str       = "0.0001"
    max_sec: str       = "50"
    filas_sec: List[List[str]] = []
    raiz_sec: str      = ""
    error_sec: str     = ""
    iter_sec: str      = ""
    mensaje_sec: str   = ""
    cargando_sec: bool = False
    error_sec_ui: str  = ""
    mostrar_sec: bool  = False

    # Tab activo
    tab: str = "biseccion"

    # Estado del backend
    backend_activo: bool = False

    async def verificar_backend(self):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get("http://127.0.0.1:8000/", timeout=2)
            self.backend_activo = r.status_code == 200
        except:
            self.backend_activo = False

    # Setters bisección
    def set_funcion(self, v): self.funcion = v
    def set_a(self, v): self.a = v
    def set_b(self, v): self.b = v
    def set_tolerancia(self, v): self.tolerancia = v
    def set_max_iteraciones(self, v): self.max_iteraciones = v

    # Setters secante
    def set_funcion_sec(self, v): self.funcion_sec = v
    def set_x0(self, v): self.x0 = v
    def set_x1(self, v): self.x1 = v
    def set_tol_sec(self, v): self.tol_sec = v
    def set_max_sec(self, v): self.max_sec = v

    # Tabs
    def ir_biseccion(self): self.tab = "biseccion"
    def ir_secante(self):   self.tab = "secante"

    async def calcular_biseccion(self):
        self.cargando = True
        self.error_ui = ""
        self.filas = []
        self.mostrar = False
        try:
            payload = {
                "funcion": self.funcion,
                "a": float(self.a),
                "b": float(self.b),
                "tolerancia": float(self.tolerancia),
                "max_iteraciones": int(self.max_iteraciones),
            }
            async with httpx.AsyncClient() as client:
                r = await client.post("http://127.0.0.1:8000/biseccion", json=payload, timeout=10)
            d = r.json()
            self.filas = [
                [str(it.get("iteracion","")), str(it.get("a","")), str(it.get("b","")),
                 str(it.get("c","")), str(it.get("f_c","")), str(it.get("error","—"))]
                for it in d.get("iteraciones", [])
            ]
            self.raiz        = str(d.get("raiz_aproximada",""))
            self.error_final = str(d.get("error_final",""))
            self.iter_total  = str(d.get("iteraciones_totales",""))
            self.mensaje     = d.get("mensaje","")
            self.mostrar     = True
        except Exception as e:
            self.error_ui = f"Error al conectar con el backend: {str(e)}"
        self.cargando = False

    async def calcular_secante(self):
        self.cargando_sec = True
        self.error_sec_ui = ""
        self.filas_sec = []
        self.mostrar_sec = False
        try:
            payload = {
                "funcion": self.funcion_sec,
                "x0": float(self.x0),
                "x1": float(self.x1),
                "tolerancia": float(self.tol_sec),
                "max_iteraciones": int(self.max_sec),
            }
            async with httpx.AsyncClient() as client:
                r = await client.post("http://127.0.0.1:8000/secante", json=payload, timeout=10)
            d = r.json()
            self.filas_sec = [
                [str(it.get("iteracion","")), str(it.get("x_n1","")), str(it.get("x_n","")),
                 str(it.get("x_nuevo","")), str(it.get("f_x_n","")), str(it.get("error","—"))]
                for it in d.get("iteraciones", [])
            ]
            self.raiz_sec  = str(d.get("raiz_aproximada",""))
            self.error_sec = str(d.get("error_final",""))
            self.iter_sec  = str(d.get("iteraciones_totales",""))
            self.mensaje_sec = d.get("mensaje","")
            self.mostrar_sec = True
        except Exception as e:
            self.error_sec_ui = f"Error al conectar con el backend: {str(e)}"
        self.cargando_sec = False


# ─────────────────────────────────────────────
#  CSS global + partículas + animaciones
# ─────────────────────────────────────────────

GLOBAL_CSS = """body { background: #060e04 !important; margin: 0; }
@keyframes pulse {
  0%,100% { opacity:1; box-shadow: 0 0 0 0 rgba(99,153,34,0.4); }
  50%      { opacity:0.7; box-shadow: 0 0 0 6px rgba(99,153,34,0); }
}
@keyframes fadeSlideIn {
  from { opacity:0; transform: translateY(10px); }
  to   { opacity:1; transform: translateY(0); }
}
@keyframes rowIn {
  from { opacity:0; transform: translateX(-8px); }
  to   { opacity:1; transform: translateX(0); }
}
@keyframes blink {
  0%,100% { opacity:1; }
  50%      { opacity:0; }
}
.sdot { animation: pulse 2s infinite; }
.result-appear { animation: fadeSlideIn 0.5s ease both; }
.tbl-row-anim { animation: rowIn 0.35s ease both; }
.cursor-blink {
  display: inline-block; width: 2px; height: 13px;
  background: #97C459; margin-left: 2px;
  vertical-align: middle;
  animation: blink 0.8s infinite;
}
#particles-canvas {
  position: fixed; top: 0; left: 0;
  width: 100vw; height: 100vh;
  pointer-events: none; z-index: 0;
}
.app-layer { position: relative; z-index: 1; }
"""

PARTICLES_JS = """
(function() {
  var canvas = document.createElement('canvas');
  canvas.id = 'particles-canvas';
  document.body.appendChild(canvas);
  var ctx = canvas.getContext('2d');
  var W, H;

  function resize() {
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = W; canvas.height = H;
  }
  resize();
  window.addEventListener('resize', resize);

  // Iconos de agronomia y metodos numericos
  var ICONS = [
    // Planta / brote
    function(ctx, x, y, s, a) {
      ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = '#639922'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(x, y+s); ctx.lineTo(x, y-s*0.3); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x, y);
      ctx.bezierCurveTo(x, y-s*0.5, x+s*0.8, y-s*0.8, x+s*0.6, y-s*1.2); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x, y+s*0.2);
      ctx.bezierCurveTo(x, y-s*0.3, x-s*0.7, y-s*0.6, x-s*0.5, y-s); ctx.stroke();
      ctx.restore();
    },
    // Espiga de trigo
    function(ctx, x, y, s, a) {
      ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = '#97C459'; ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.moveTo(x, y+s); ctx.lineTo(x, y-s); ctx.stroke();
      for(var i=-3;i<=3;i++) {
        var py = y + i*(s*0.28);
        ctx.beginPath(); ctx.moveTo(x, py);
        ctx.bezierCurveTo(x+s*0.4, py-s*0.15, x+s*0.5, py-s*0.3, x+s*0.2, py-s*0.4); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(x, py);
        ctx.bezierCurveTo(x-s*0.4, py-s*0.15, x-s*0.5, py-s*0.3, x-s*0.2, py-s*0.4); ctx.stroke();
      }
      ctx.restore();
    },
    // Gota de agua
    function(ctx, x, y, s, a) {
      ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = '#9FE1CB'; ctx.lineWidth = 1.3;
      ctx.beginPath(); ctx.moveTo(x, y-s);
      ctx.bezierCurveTo(x+s*0.6, y-s*0.2, x+s*0.6, y+s*0.6, x, y+s*0.7);
      ctx.bezierCurveTo(x-s*0.6, y+s*0.6, x-s*0.6, y-s*0.2, x, y-s);
      ctx.stroke(); ctx.restore();
    },
    // Hoja
    function(ctx, x, y, s, a) {
      ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = '#3B6D11'; ctx.lineWidth = 1.3;
      ctx.beginPath(); ctx.moveTo(x, y+s*0.8);
      ctx.bezierCurveTo(x-s*0.8, y+s*0.2, x-s*0.9, y-s*0.6, x, y-s*0.8);
      ctx.bezierCurveTo(x+s*0.9, y-s*0.6, x+s*0.8, y+s*0.2, x, y+s*0.8);
      ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x, y+s*0.8); ctx.lineTo(x, y-s*0.8); ctx.stroke();
      ctx.restore();
    },
    // f(x)
    function(ctx, x, y, s, a) {
      ctx.save(); ctx.globalAlpha = a;
      ctx.font = 'bold ' + Math.round(s*1.3) + 'px monospace';
      ctx.fillStyle = '#639922'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText('f(x)', x, y); ctx.restore();
    },
    // Sigma
    function(ctx, x, y, s, a) {
      ctx.save(); ctx.globalAlpha = a;
      ctx.font = 'bold ' + Math.round(s*1.6) + 'px serif';
      ctx.fillStyle = '#2a4a1a'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText('Σ', x, y); ctx.restore();
    },
    // Raiz cuadrada
    function(ctx, x, y, s, a) {
      ctx.save(); ctx.globalAlpha = a;
      ctx.font = 'bold ' + Math.round(s*1.4) + 'px monospace';
      ctx.fillStyle = '#3B6D11'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText('√x', x, y); ctx.restore();
    },
    // Mazorca de maiz
    function(ctx, x, y, s, a) {
      ctx.save(); ctx.globalAlpha = a;
      var sc = s * 0.13;
      ctx.strokeStyle = '#3B6D11'; ctx.lineWidth = sc * 0.8;
      ctx.beginPath(); ctx.moveTo(x, y+s*0.95); ctx.lineTo(x, y+s*0.55); ctx.stroke();
      ctx.strokeStyle = '#639922'; ctx.lineWidth = sc * 0.7;
      ctx.beginPath(); ctx.moveTo(x, y+s*0.7);
      ctx.bezierCurveTo(x+s*0.5, y+s*0.5, x+s*0.7, y+s*0.2, x+s*0.4, y); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(x, y+s*0.5);
      ctx.bezierCurveTo(x-s*0.5, y+s*0.3, x-s*0.6, y, x-s*0.3, y-s*0.2); ctx.stroke();
      ctx.strokeStyle = '#97C459'; ctx.lineWidth = sc;
      ctx.beginPath();
      ctx.ellipse(x, y-s*0.1, s*0.22, s*0.55, 0, 0, Math.PI*2); ctx.stroke();
      ctx.fillStyle = '#C0DD97';
      for(var r=0;r<6;r++) {
        for(var c=0;c<3;c++) {
          var gx = x + (c-1)*s*0.13;
          var gy = y - s*0.52 + r*s*0.17;
          var offset = (c%2===0) ? 0 : s*0.085;
          ctx.globalAlpha = a*0.7;
          ctx.beginPath(); ctx.arc(gx, gy+offset, sc*0.5, 0, Math.PI*2); ctx.fill();
        }
      }
      ctx.globalAlpha = a; ctx.strokeStyle = '#C0DD97'; ctx.lineWidth = 0.5;
      for(var h=-2;h<=2;h++) {
        ctx.beginPath();
        ctx.moveTo(x+h*s*0.06, y-s*0.62);
        ctx.lineTo(x+h*s*0.1,  y-s*0.95); ctx.stroke();
      }
      ctx.restore();
    },
  ];

  // Crear particulas
  var particles = [];
  // Distribuir uniformemente en grilla para evitar aglomeracion
  var cols = 4, rows = 4;
  var cellW = W / cols, cellH = H / rows;
  var count = 0;
  for(var row=0;row<rows;row++) {
    for(var col=0;col<cols;col++) {
      particles.push({
        x: col*cellW + Math.random()*cellW*0.7 + cellW*0.15,
        y: row*cellH + Math.random()*cellH*0.7 + cellH*0.15,
        vx: (Math.random()-0.5)*0.28,
        vy: (Math.random()-0.5)*0.28,
        s: Math.random()*10+14,
        a: Math.random()*0.2+0.12,
        type: count % ICONS.length,
        angle: Math.random()*Math.PI*2,
        va: (Math.random()-0.5)*0.006,
      });
      count++;
    }
  }

  function draw() {
    ctx.clearRect(0,0,W,H);

    // Lineas de conexion
    for(var i=0;i<particles.length;i++) {
      for(var j=i+1;j<particles.length;j++) {
        var dx=particles[i].x-particles[j].x, dy=particles[i].y-particles[j].y;
        var dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<130) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x,particles[i].y);
          ctx.lineTo(particles[j].x,particles[j].y);
          ctx.strokeStyle='rgba(99,153,34,'+(0.07*(1-dist/130))+')';
          ctx.lineWidth=0.5; ctx.stroke();
        }
      }
    }

    // Dibujar iconos
    for(var i=0;i<particles.length;i++) {
      var p = particles[i];
      ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.angle);
      ICONS[p.type](ctx, 0, 0, p.s, p.a);
      ctx.restore();
      p.x += p.vx; p.y += p.vy; p.angle += p.va;
      if(p.x<-30||p.x>W+30) p.vx*=-1;
      if(p.y<-30||p.y>H+30) p.vy*=-1;
    }

    requestAnimationFrame(draw);
  }
  draw();
})();
"""

TYPEWRITER_JS = """
window._typewriterActive = false;
window.startTypewriter = function(msg, elId, cursorId) {
  if(window._typewriterActive) return;
  window._typewriterActive = true;
  var el = document.getElementById(elId);
  var cur = document.getElementById(cursorId);
  if(!el) return;
  el.textContent = '';
  if(cur) cur.style.display = 'inline-block';
  var i = 0;
  function type() {
    if(i < msg.length) {
      el.textContent += msg[i++];
      setTimeout(type, 16);
    } else {
      if(cur) cur.style.display = 'none';
      window._typewriterActive = false;
    }
  }
  type();
};
window.copyToClipboard = function(text, btnId) {
  navigator.clipboard.writeText(text).catch(function(){
    var ta = document.createElement('textarea');
    ta.value = text; document.body.appendChild(ta);
    ta.select(); document.execCommand('copy');
    document.body.removeChild(ta);
  });
  var btn = document.getElementById(btnId);
  if(btn) {
    var orig = btn.textContent;
    btn.textContent = '✓ Copiado';
    btn.style.color = '#97C459';
    btn.style.borderColor = '#639922';
    setTimeout(function(){ btn.textContent=orig; btn.style.color=''; btn.style.borderColor=''; }, 2000);
  }
};
"""


# ─────────────────────────────────────────────
#  Componentes reutilizables
# ─────────────────────────────────────────────
def field(label: str, val, on_change, placeholder: str = "") -> rx.Component:
    return rx.box(
        rx.text(label, font_size="10px", color=TEXT_MUT,
                text_transform="uppercase", letter_spacing="0.08em", margin_bottom="3px"),
        rx.input(
            value=val, on_change=on_change, placeholder=placeholder,
            background=BG_MID, border=f"0.5px solid {BORDER2}",
            border_radius="8px", padding="8px 12px",
            font_size="13px", color=GREEN_LT, font_family=MONO, width="100%",
            _focus={"outline": "none", "border": f"0.5px solid {GREEN_MID}"},
        ),
    )


def metric(label: str, val, sub: str) -> rx.Component:
    return rx.box(
        rx.text(label, font_size="10px", color=GREEN_DK,
                text_transform="uppercase", letter_spacing="0.08em", margin_bottom="4px"),
        rx.text(val, font_size="22px", font_weight="500", color=GREEN_LT, font_family=MONO),
        rx.text(sub, font_size="10px", color=TEXT_MUT, margin_top="2px"),
        background=BG_DARK, border=f"0.5px solid {BORDER2}",
        border_radius="10px", padding="12px 14px",
        class_name="result-appear",
    )


def fila_tabla(fila: List[str]) -> rx.Component:
    return rx.table.row(
        rx.table.cell(fila[0], text_align="center", color=GREEN_MID, font_weight="500", font_family=MONO, font_size="12px"),
        rx.table.cell(fila[1], text_align="center", color=TEXT_SEC, font_family=MONO, font_size="11px"),
        rx.table.cell(fila[2], text_align="center", color=TEXT_SEC, font_family=MONO, font_size="11px"),
        rx.table.cell(fila[3], text_align="center", color=GREEN_LT, font_weight="500", font_family=MONO, font_size="11px"),
        rx.table.cell(fila[4], text_align="center", color=TEXT_SEC, font_family=MONO, font_size="11px"),
        rx.table.cell(fila[5], text_align="center", color=TEXT_MUT, font_family=MONO, font_size="11px"),
        _hover={"background": BG_PANEL},
        border_bottom=f"0.5px solid {BG_MID}",
        class_name="tbl-row-anim",
    )


def sidebar_btn(label, cargando, on_click) -> rx.Component:
    return rx.button(
        rx.cond(cargando, "Ejecutando...", label),
        on_click=on_click, loading=cargando,
        background=GREEN_MID, color=BG_DEEP,
        width="100%", margin_top="1.2rem", padding="10px",
        border_radius="8px", font_size="13px", font_weight="500",
        cursor="pointer", border="none",
        _hover={"background": GREEN_LT},
        transition="background 0.2s",
    )


def tabla_section(title, subtitulo, filas, headers) -> rx.Component:
    return rx.box(
        rx.flex(
            rx.text(title, font_size="12px", font_weight="500", color=GREEN_LT),
            rx.text(subtitulo, font_size="11px", color=TEXT_MUT),
            justify="between", align="center",
            padding="10px 14px", background=BG_DARK,
            border_bottom=f"0.5px solid {BORDER}",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(*[
                    rx.table.column_header_cell(
                        h, text_align="center", color=GREEN_MID,
                        font_size="10px", background=BG_PANEL,
                        padding="8px 10px", letter_spacing="0.06em",
                    ) for h in headers
                ]),
            ),
            rx.table.body(rx.foreach(filas, fila_tabla)),
            width="100%",
        ),
        border=f"0.5px solid {BORDER2}",
        border_radius="10px", overflow="hidden",
    )


def mensaje_box(msg, tw_id, cur_id, copy_id, on_mount_js) -> rx.Component:
    return rx.box(
        rx.html(f"""
        <div style="position:relative;">
          <span id="{tw_id}" style="font-size:12px;color:#9FE1CB;line-height:1.7;font-family:var(--font-sans);"></span>
          <span id="{cur_id}" class="cursor-blink"></span>
          <button id="{copy_id}"
            onclick="window.copyToClipboard(document.getElementById('{tw_id}').textContent, '{copy_id}')"
            style="position:absolute;top:0;right:0;background:#1e3810;border:0.5px solid #2a4a1a;
                   border-radius:6px;padding:3px 10px;font-size:10px;color:#639922;cursor:pointer;
                   font-family:var(--font-sans);transition:all 0.2s;">
            Copiar
          </button>
        </div>
        """),
        rx.script(on_mount_js),
        background=BG_DARK,
        border_left=f"2px solid {GREEN_MID}",
        border_top=f"0.5px solid {BORDER}",
        border_right=f"0.5px solid {BORDER}",
        border_bottom=f"0.5px solid {BORDER}",
        border_radius="0 8px 8px 0",
        padding="10px 14px",
        margin_bottom="1.25rem",
        class_name="result-appear",
    )





# ─────────────────────────────────────────────
#  Panel Bisección
# ─────────────────────────────────────────────
def panel_biseccion() -> rx.Component:
    tw_js = rx.cond(
        State.mostrar,
        "window._typewriterActive=false; window.startTypewriter(" +
        "document.getElementById('msg-bis-full')?.dataset?.msg || '', 'tw-bis', 'cur-bis');",
        ""
    )
    return rx.flex(
        # Sidebar
        rx.box(
            field("f(x)", State.funcion, State.set_funcion, "x**2 - 5"),
            rx.text("Intervalo", font_size="10px", color=TEXT_MUT,
                    text_transform="uppercase", letter_spacing="0.08em",
                    margin_top="14px", margin_bottom="6px"),
            rx.flex(
                field("a", State.a, State.set_a, "2.0"),
                field("b", State.b, State.set_b, "3.0"),
                gap="8px",
            ),
            rx.text("Precisión", font_size="10px", color=TEXT_MUT,
                    text_transform="uppercase", letter_spacing="0.08em",
                    margin_top="14px", margin_bottom="6px"),
            rx.flex(
                field("Tolerancia", State.tolerancia, State.set_tolerancia, "0.001"),
                field("Máx. iter.", State.max_iteraciones, State.set_max_iteraciones, "50"),
                gap="8px",
            ),
            sidebar_btn("Ejecutar Bisección", State.cargando, State.calcular_biseccion),
            rx.cond(
                State.error_ui != "",
                rx.box(rx.text(State.error_ui, font_size="12px", color="#f87171"),
                       background="#1a0a0a", border="0.5px solid #7f1d1d",
                       border_radius="8px", padding="10px", margin_top="10px"),
            ),
            width="280px", flex_shrink="0",
            background=BG_DARK,
            border_right=f"0.5px solid {BORDER}",
            padding="1.25rem",
            min_height="500px",
        ),

        # Main
        rx.box(
            rx.cond(
                State.mostrar,
                rx.box(
                    # Pill convergencia
                    rx.flex(
                        rx.box(width="7px", height="7px", border_radius="50%",
                               background=GREEN_MID, class_name="sdot"),
                        rx.text("Convergencia alcanzada", font_size="11px", color=GREEN_LT),
                        align="center", gap="6px",
                        background=BG_PANEL, border=f"0.5px solid {GREEN_DK}",
                        border_radius="99px", padding="4px 12px",
                        display="inline-flex", margin_bottom="1rem",
                        class_name="result-appear",
                    ),
                    # Métricas
                    rx.grid(
                        metric("Raíz", State.raiz, "valor aproximado"),
                        metric("Iteraciones", State.iter_total, "pasos realizados"),
                        metric("Error final", State.error_final, "precisión lograda"),
                        columns="3", gap="10px", margin_bottom="1.25rem",
                    ),
                    # Mensaje resultado
                    rx.box(
                        rx.flex(
                            rx.text(
                                State.mensaje,
                                font_size="12px", color=TEXT_SEC,
                                line_height="1.7", flex="1",
                            ),
                            rx.button(
                                "Copiar",
                                on_click=rx.set_clipboard(State.mensaje),
                                background="#1e3810",
                                border=f"0.5px solid {BORDER2}",
                                border_radius="6px",
                                padding="3px 10px",
                                font_size="10px",
                                color=GREEN_MID,
                                cursor="pointer",
                                flex_shrink="0",
                                align_self="start",
                                _hover={"background": BORDER2, "color": GREEN_LT},
                            ),
                            gap="10px",
                            align="start",
                        ),
                        background=BG_DARK,
                        border_left=f"2px solid {GREEN_MID}",
                        border_top=f"0.5px solid {BORDER}",
                        border_right=f"0.5px solid {BORDER}",
                        border_bottom=f"0.5px solid {BORDER}",
                        border_radius="0 8px 8px 0",
                        padding="10px 14px",
                        margin_bottom="1.25rem",
                        class_name="result-appear",
                    ),
                    # Tabla
                    tabla_section(
                        "Tabla de iteraciones",
                        State.iter_total + " pasos",
                        State.filas,
                        ["It.", "a", "b", "c=(a+b)/2", "f(c)", "Error"],
                    ),
                    class_name="result-appear",
                ),
                rx.flex(
                    rx.text("Ingresa los parámetros y ejecuta el método",
                            font_size="13px", color=TEXT_MUT),
                    align="center", justify="center", height="200px",
                    background=BG_MID,
                ),
            ),
            flex="1", padding="1.25rem 1.5rem", overflow_y="auto", background=BG_MID,
        ),
        align="stretch", width="100%",
        background=BG_MID,
    )


# ─────────────────────────────────────────────
#  Panel Secante
# ─────────────────────────────────────────────
def panel_secante() -> rx.Component:
    return rx.flex(
        rx.box(
            field("f(x)", State.funcion_sec, State.set_funcion_sec, "x**3 - x - 2"),
            rx.text("Puntos iniciales", font_size="10px", color=TEXT_MUT,
                    text_transform="uppercase", letter_spacing="0.08em",
                    margin_top="14px", margin_bottom="6px"),
            rx.flex(
                field("x₀", State.x0, State.set_x0, "1.0"),
                field("x₁", State.x1, State.set_x1, "2.0"),
                gap="8px",
            ),
            rx.text("Precisión", font_size="10px", color=TEXT_MUT,
                    text_transform="uppercase", letter_spacing="0.08em",
                    margin_top="14px", margin_bottom="6px"),
            rx.flex(
                field("Tolerancia", State.tol_sec, State.set_tol_sec, "0.0001"),
                field("Máx. iter.", State.max_sec, State.set_max_sec, "50"),
                gap="8px",
            ),
            sidebar_btn("Ejecutar Secante", State.cargando_sec, State.calcular_secante),
            rx.cond(
                State.error_sec_ui != "",
                rx.box(rx.text(State.error_sec_ui, font_size="12px", color="#f87171"),
                       background="#1a0a0a", border="0.5px solid #7f1d1d",
                       border_radius="8px", padding="10px", margin_top="10px"),
            ),
            width="280px", flex_shrink="0",
            background=BG_DARK,
            border_right=f"0.5px solid {BORDER}",
            padding="1.25rem",
            min_height="500px",
        ),
        rx.box(
            rx.cond(
                State.mostrar_sec,
                rx.box(
                    rx.flex(
                        rx.box(width="7px", height="7px", border_radius="50%",
                               background=GREEN_MID, class_name="sdot"),
                        rx.text("Convergencia alcanzada", font_size="11px", color=GREEN_LT),
                        align="center", gap="6px",
                        background=BG_PANEL, border=f"0.5px solid {GREEN_DK}",
                        border_radius="99px", padding="4px 12px",
                        display="inline-flex", margin_bottom="1rem",
                        class_name="result-appear",
                    ),
                    rx.grid(
                        metric("Raíz", State.raiz_sec, "valor aproximado"),
                        metric("Iteraciones", State.iter_sec, "pasos realizados"),
                        metric("Error final", State.error_sec, "precisión lograda"),
                        columns="3", gap="10px", margin_bottom="1.25rem",
                    ),
                    rx.box(
                        rx.flex(
                            rx.text(
                                State.mensaje_sec,
                                font_size="12px", color=TEXT_SEC,
                                line_height="1.7", flex="1",
                            ),
                            rx.button(
                                "Copiar",
                                on_click=rx.set_clipboard(State.mensaje_sec),
                                background="#1e3810",
                                border=f"0.5px solid {BORDER2}",
                                border_radius="6px",
                                padding="3px 10px",
                                font_size="10px",
                                color=GREEN_MID,
                                cursor="pointer",
                                flex_shrink="0",
                                align_self="start",
                                _hover={"background": BORDER2, "color": GREEN_LT},
                            ),
                            gap="10px",
                            align="start",
                        ),
                        background=BG_DARK,
                        border_left=f"2px solid {GREEN_MID}",
                        border_top=f"0.5px solid {BORDER}",
                        border_right=f"0.5px solid {BORDER}",
                        border_bottom=f"0.5px solid {BORDER}",
                        border_radius="0 8px 8px 0",
                        padding="10px 14px",
                        margin_bottom="1.25rem",
                        class_name="result-appear",
                    ),
                                        tabla_section(
                        "Tabla de iteraciones",
                        State.iter_sec + " pasos",
                        State.filas_sec,
                        ["It.", "xₙ₋₁", "xₙ", "xₙ₊₁", "f(xₙ)", "Error"],
                    ),
                    class_name="result-appear",
                ),
                rx.flex(
                    rx.text("Ingresa los parámetros y ejecuta el método",
                            font_size="13px", color=TEXT_MUT),
                    align="center", justify="center", height="200px",
                    background=BG_MID,
                ),
            ),
            flex="1", padding="1.25rem 1.5rem", overflow_y="auto", background=BG_MID,
        ),
        align="stretch", width="100%",
        background=BG_MID,
    )


# ─────────────────────────────────────────────
#  Página principal
# ─────────────────────────────────────────────
def index() -> rx.Component:
    return rx.box(
        # CSS global
        rx.html(f"<style>{GLOBAL_CSS}</style>"),
        # Script partículas
        rx.script(PARTICLES_JS),
        # Script typewriter + copy
        rx.script(TYPEWRITER_JS),
        # Script para pasar mensaje al typewriter
        rx.script(
            "window.__bis_msg = " + rx.State.mensaje._var_value.__repr__() + ";"
            if hasattr(rx.State, "mensaje") else ""
        ),

        rx.box(
            rx.box(
                    # ── Topbar ──
                    rx.flex(
                        rx.flex(
                            rx.image(
                                src="/UP-logo.png",
                                height="48px",
                                object_fit="contain",
                                flex_shrink="0",
                            ),
                            rx.box(
                                rx.text("Métodos Numéricos", font_size="15px",
                                        font_weight="500", color=TEXT_PRI, letter_spacing="0.01em"),
                                rx.text("Universidad de Panamá · Ing. Informática",
                                        font_size="11px", color=GREEN_MID, margin_top="1px"),
                            ),
                            align="center", gap="14px",
                        ),
                        rx.flex(
                            rx.box(
                                width="7px", height="7px", border_radius="50%",
                                background=rx.cond(State.backend_activo, GREEN_MID, "#dc2626"),
                                class_name=rx.cond(State.backend_activo, "sdot", ""),
                            ),
                            rx.text(
                                rx.cond(State.backend_activo, "Backend activo", "Backend inactivo"),
                                font_size="11px",
                                color=rx.cond(State.backend_activo, GREEN_MID, "#dc2626"),
                            ),
                            align="center", gap="6px",
                            on_mount=State.verificar_backend,
                        ),
                        justify="between", align="center",
                        padding="0.9rem 1.75rem",
                        background="rgba(10,18,8,0.92)",
                        border_bottom=f"0.5px solid {BORDER}",
                    ),

                    # ── Tabs ──
                    rx.flex(
                        rx.button(
                            "Bisección",
                            on_click=State.ir_biseccion,
                            background="transparent", border="none", border_radius="0",
                            padding="10px 18px", font_size="12px", cursor="pointer",
                            letter_spacing="0.02em",
                            color=rx.cond(State.tab == "biseccion", GREEN_LT, TEXT_MUT),
                            border_bottom=rx.cond(State.tab == "biseccion",
                                                  f"2px solid {GREEN_MID}", "2px solid transparent"),
                            _hover={"color": GREEN_LT},
                        ),
                        rx.button(
                            "Secante",
                            on_click=State.ir_secante,
                            background="transparent", border="none", border_radius="0",
                            padding="10px 18px", font_size="12px", cursor="pointer",
                            letter_spacing="0.02em",
                            color=rx.cond(State.tab == "secante", GREEN_LT, TEXT_MUT),
                            border_bottom=rx.cond(State.tab == "secante",
                                                  f"2px solid {GREEN_MID}", "2px solid transparent"),
                            _hover={"color": GREEN_LT},
                        ),
                        background="rgba(10,18,8,0.85)",
                        border_bottom=f"0.5px solid {BORDER}",
                        padding_left="1rem",
                    ),

                    # ── Contenido ──
                    rx.cond(
                        State.tab == "biseccion",
                        panel_biseccion(),
                        panel_secante(),
                    ),

                    # ── Footer ──
                    rx.flex(
                        rx.text("Félix Samudio · José Urrunaga · Jeremy Gonzalez",
                                font_size="10px", color=BORDER2, letter_spacing="0.05em"),
                        rx.text("FastAPI + Reflex · Análisis Numérico 2026",
                                font_size="10px", color=GREEN_DK, letter_spacing="0.05em"),
                        justify="between", align="center",
                        padding="8px 1.75rem",
                        background="rgba(10,18,8,0.92)",
                        border_top=f"0.5px solid {BORDER}",
                    ),

                    background="rgba(13,26,10,0.85)",
                    border=f"0.5px solid {BORDER2}",
                    border_radius="16px",
                    overflow="hidden",
                    max_width="1100px",
                    margin="2rem auto",
                    backdrop_filter="blur(2px)",
                ),
            class_name="app-layer",
        ),

        background=BG_DEEP,
        min_height="100vh",
        padding="0 1rem",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    stylesheets=[],
)
app.add_page(index, route="/", title="Métodos Numéricos — UP", on_load=State.verificar_backend)
