import { useEffect, useState } from 'react'

function SolicitarVacaciones({ empleado, onCancelar }) {
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [anio, setAnio] = useState(new Date().getFullYear())
  const [disponibles, setDisponibles] = useState(null)
  const [mensaje, setMensaje] = useState('')

  const cargarSaldo = (anioConsulta) => {
    fetch(`/api/empleados/${empleado.id}/vacaciones?anio=${anioConsulta}`)
      .then((respuesta) => respuesta.json())
      .then((datos) => {
        setAnio(datos.anio)
        setDisponibles(datos.dias_disponibles)
      })
      .catch(() => setDisponibles(null))
  }

  useEffect(() => {
    cargarSaldo(new Date().getFullYear())
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [empleado.id])

  const enviar = async (evento) => {
    evento.preventDefault()
    setMensaje('')

    try {
      const respuesta = await fetch(`/api/empleados/${empleado.id}/vacaciones`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fecha_inicio: fechaInicio, fecha_fin: fechaFin }),
      })
      const datos = await respuesta.json()

      if (!respuesta.ok) {
        setMensaje(datos.detail || 'Ocurrió un error al solicitar las vacaciones')
        return
      }

      const anioSolicitud = fechaInicio.slice(0, 4)
      setMensaje(
        `Solicitud registrada: ${datos.dias_habiles} días hábiles. Te quedan ${datos.dias_restantes} días hábiles en ${anioSolicitud}.`
      )
      cargarSaldo(Number(anioSolicitud))
    } catch (error) {
      setMensaje('No se pudo conectar con el servidor')
    }
  }

  return (
    <form onSubmit={enviar}>
      <h2>Solicitar vacaciones de {empleado.nombre}</h2>
      <p>
        Días disponibles en {anio}:{' '}
        <span data-testid="vacaciones-disponibles">{disponibles ?? '—'}</span>
      </p>
      <label>
        Fecha de inicio
        <input
          data-testid="vacaciones-fecha-inicio"
          type="date"
          value={fechaInicio}
          onChange={(evento) => setFechaInicio(evento.target.value)}
          required
        />
      </label>
      <label>
        Fecha de fin
        <input
          data-testid="vacaciones-fecha-fin"
          type="date"
          value={fechaFin}
          onChange={(evento) => setFechaFin(evento.target.value)}
          required
        />
      </label>
      <button type="submit" data-testid="vacaciones-enviar">
        Enviar solicitud
      </button>
      <button type="button" onClick={onCancelar}>
        Cerrar
      </button>

      {mensaje && <p data-testid="vacaciones-mensaje">{mensaje}</p>}
    </form>
  )
}

export default SolicitarVacaciones
