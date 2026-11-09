import { useEffect, useRef, useState } from 'react'

// Decide si mostrar un skeleton mientras algo carga, sin parpadeos:
// - Espera `delay` ms antes de mostrarlo: si la carga es casi instantánea, no se ve nada.
// - Una vez visible, lo mantiene al menos `minVisible` ms para que no aparezca y desaparezca
//   de golpe.
export function useDelayedFlag(active: boolean, delay = 200, minVisible = 300): boolean {
  const [shown, setShown] = useState(false)
  const shownAt = useRef(0)

  useEffect(() => {
    if (active && !shown) {
      const timer = setTimeout(() => {
        shownAt.current = Date.now()
        setShown(true)
      }, delay)
      return () => clearTimeout(timer)
    }
    if (!active && shown) {
      const remaining = minVisible - (Date.now() - shownAt.current)
      const timer = setTimeout(() => setShown(false), Math.max(0, remaining))
      return () => clearTimeout(timer)
    }
  }, [active, shown, delay, minVisible])

  return shown
}
