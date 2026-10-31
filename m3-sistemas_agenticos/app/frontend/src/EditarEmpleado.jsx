import { useEffect, useState } from 'react'

function EditarEmpleado({ empleado, onCancelar, onGuardado }) {
  const [puesto, setPuesto] = useState(empleado.puesto)
  const [departamento, setDepartamento] = useState(empleado.departamento)
  const [departamentos, setDepartamentos] = useState([])
  const [mensajeExito, setMensajeExito] = useState('')
  const [mensajeError, setMensajeError] = useState('')

  useEffect(() => {
    fetch('/api/departamentos')
      .then((respuesta) => respuesta.json())
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]))
  }, [])

  const guardar = async (evento) => {
    evento.preventDefault()
    setMensajeExito('')
    setMensajeError('')

    try {
      const respuesta = await fetch(`/api/empleados/${empleado.numero_empleado}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ puesto, departamento }),
      })
      const datos = await respuesta.json()

      if (!respuesta.ok) {
        setMensajeError(datos.detail || 'Ocurrió un error al editar al empleado')
        return
      }

      setMensajeExito('Empleado actualizado correctamente')
      onGuardado?.()
    } catch (error) {
      setMensajeError('No se pudo conectar con el servidor')
    }
  }

  return (
    <form onSubmit={guardar}>
      <h2>Editar empleado {empleado.numero_empleado}</h2>
      <label>
        Puesto
        <input
          data-testid="empleado-puesto"
          value={puesto}
          onChange={(evento) => setPuesto(evento.target.value)}
          required
        />
      </label>
      <label>
        Departamento
        <select
          data-testid="empleado-departamento"
          value={departamento}
          onChange={(evento) => setDepartamento(evento.target.value)}
          required
        >
          <option value="">Selecciona un departamento</option>
          {departamentos.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
      </label>
      <button type="submit" data-testid="empleado-guardar">
        Guardar
      </button>
      <button type="button" onClick={onCancelar}>
        Cancelar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  )
}

export default EditarEmpleado
