import { useState } from 'react'

import { EyeIcon, EyeOffIcon } from './icons'
import { TextField, type TextFieldProps } from './TextField'

// Campo de contraseña con botón para mostrarla. El botón mantiene siempre el mismo nombre
// ("Mostrar contraseña") y su estado lo indica aria-pressed: si cambiara también el texto,
// el lector de pantalla lo anunciaría dos veces.
export function PasswordField(props: Omit<TextFieldProps, 'type' | 'trailing'>) {
  const [visible, setVisible] = useState(false)

  return (
    <TextField
      {...props}
      type={visible ? 'text' : 'password'}
      autoCapitalize="none"
      spellCheck={false}
      trailing={
        <button
          type="button"
          aria-pressed={visible}
          aria-label="Mostrar contraseña"
          onClick={() => setVisible((current) => !current)}
          className="inline-flex size-11 cursor-pointer items-center justify-center rounded-control text-muted transition-colors duration-150 hover:text-ink"
        >
          {visible ? <EyeOffIcon /> : <EyeIcon />}
        </button>
      }
    />
  )
}
