# Diseño: "Tinta y resaltador"

La interfaz toma su identidad de la agenda de papel de un negocio pequeño: **tinta azul** para
las acciones y **resaltador amarillo** para marcar lo importante. Debe verse limpia, cómoda a la
vista y nada genérica. Los tokens viven en `frontend/src/index.css` (`@theme` de Tailwind v4).

## Colores

| Token | Hex | Uso |
| --- | --- | --- |
| `paper` | `#F4F5F8` | Fondo de la página |
| `surface` | `#FFFFFF` | Cabecera, paneles, campos |
| `ink` | `#151A33` | Texto principal |
| `muted` | `#555C78` | Texto secundario (6:1 sobre `paper`) |
| `line` | `#E2E4EC` | Separadores decorativos |
| `field` | `#7C829A` | Borde de campos y controles (3.8:1, cumple el 3:1 de WCAG) |
| `tinta` | `#2A35A8` | Botón principal, enlaces y anillo de foco (texto blanco: 9.7:1) |
| `danger` / `danger-soft` | `#B42318` / `#FEF3F2` | Errores |
| `highlight` | `#FFE15A` | Resaltador (texto `ink` encima) |
| `taken` | `#6B7189` | Horas ocupadas: siempre tachadas y con borde discontinuo |
| `skeleton` | `#E4E6EE` | Bloques de carga |

## Tipografía

- **Bricolage Grotesque** (títulos y marca), con eje óptico al máximo (`opsz 96`) y tracking ajustado.
- **Figtree** (todo lo demás). Las horas usan `tabular-nums` para que no "bailen".
- Se alojan con la propia app (`@fontsource-variable/bricolage-grotesque` y
  `@fontsource-variable/figtree`, importadas en `main.tsx`), no desde Google Fonts: así no se
  envía la IP de los visitantes a terceros y se puede usar una CSP estricta.

## Reglas

- **Resaltador con moderación:** como mucho una palabra del título y un elemento por pantalla
  (utilidad `marker`). Si todo está resaltado, nada lo está.
- **Nada de looks genéricos:** sin degradados morados, sin emojis como iconos, sin sombra y
  `rounded-lg` en todo. Las tarjetas solo donde un elemento necesita separarse.
- **Skeletons en toda carga**, con la forma real del contenido. Aparecen tras ~200 ms
  (`useDelayedFlag`) y duran al menos 300 ms para no parpadear. La zona que carga lleva
  `aria-busy` y un único texto para lectores de pantalla (`LoadingRegion`).
- **Accesibilidad:** foco visible en `tinta`, objetivos táctiles de 44 px como mínimo, etiquetas
  visibles en todos los campos, errores junto al campo y nunca solo con color.
- **Responsive, móvil primero:** sin scroll horizontal a 320 px; los paneles decorativos
  (como la agenda del login) solo aparecen en pantallas grandes.
