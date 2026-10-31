import { useState } from 'react'

function BajaEmpleado({ empleado, onCancelar, onConfirmado }) {
  const [fechaBaja, setFechaBaja] = useState('')
  const [mensajeExito, setMensajeExito] = useState('')
  const [mensajeError, setMensajeError] = useState('')

  const confirmar = async (evento) => {
    evento.preventDefault()
    setMensajeExito('')
    setMensajeError('')

    try {
      const respuesta = await fetch(`/api/empleados/${empleado.numero_empleado}/baja`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fecha_baja: fechaBaja }),
      })
      const datos = await respuesta.json()

      if (!respuesta.ok) {
        setMensajeError(datos.detail || 'Ocurrió un error al dar de baja al empleado')
        return
      }

      setMensajeExito('Empleado dado de baja correctamente')
      onConfirmado?.()
    } catch (error) {
      setMensajeError('No se pudo conectar con el servidor')
    }
  }

  return (
    <form onSubmit={confirmar}>
      <h2>Dar de baja a {empleado.numero_empleado}</h2>
      <label>
        Fecha de baja
        <input
          data-testid="empleado-fecha-baja"
          type="date"
          value={fechaBaja}
          onChange={(evento) => setFechaBaja(evento.target.value)}
          required
        />
      </label>
      <button type="submit" data-testid="confirmar-baja">
        Confirmar baja
      </button>
      <button type="button" onClick={onCancelar}>
        Cancelar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  )
}

export default BajaEmpleado
