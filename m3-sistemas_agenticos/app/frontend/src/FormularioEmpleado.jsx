import { useEffect, useState } from 'react'

const ESTADO_INICIAL = {
  nombre: '',
  correo: '',
  puesto: '',
  departamento: '',
  fecha_ingreso: '',
}

function FormularioEmpleado({ onEmpleadoCreado }) {
  const [valores, setValores] = useState(ESTADO_INICIAL)
  const [departamentos, setDepartamentos] = useState([])
  const [mensajeExito, setMensajeExito] = useState('')
  const [mensajeError, setMensajeError] = useState('')

  useEffect(() => {
    fetch('/api/departamentos')
      .then((respuesta) => respuesta.json())
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]))
  }, [])

  const actualizarCampo = (campo) => (evento) => {
    setValores({ ...valores, [campo]: evento.target.value })
  }

  const enviarFormulario = async (evento) => {
    evento.preventDefault()
    setMensajeExito('')
    setMensajeError('')

    try {
      const respuesta = await fetch('/api/empleados', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(valores),
      })
      const datos = await respuesta.json()

      if (!respuesta.ok) {
        setMensajeError(datos.detail || 'Ocurrió un error al registrar al empleado')
        return
      }

      setMensajeExito(`Empleado registrado con número ${datos.numero_empleado}`)
      setValores(ESTADO_INICIAL)
      onEmpleadoCreado?.()
    } catch (error) {
      setMensajeError('No se pudo conectar con el servidor')
    }
  }

  return (
    <form onSubmit={enviarFormulario}>
      <label>
        Nombre
        <input
          data-testid="empleado-nombre"
          value={valores.nombre}
          onChange={actualizarCampo('nombre')}
          required
        />
      </label>
      <label>
        Correo
        <input
          data-testid="empleado-correo"
          type="email"
          value={valores.correo}
          onChange={actualizarCampo('correo')}
          required
        />
      </label>
      <label>
        Puesto
        <input
          data-testid="empleado-puesto"
          value={valores.puesto}
          onChange={actualizarCampo('puesto')}
          required
        />
      </label>
      <label>
        Departamento
        <select
          data-testid="empleado-departamento"
          value={valores.departamento}
          onChange={actualizarCampo('departamento')}
          required
        >
          <option value="">Selecciona un departamento</option>
          {departamentos.map((departamento) => (
            <option key={departamento} value={departamento}>
              {departamento}
            </option>
          ))}
        </select>
      </label>
      <label>
        Fecha de ingreso
        <input
          data-testid="empleado-fecha-ingreso"
          type="date"
          value={valores.fecha_ingreso}
          onChange={actualizarCampo('fecha_ingreso')}
          required
        />
      </label>
      <button type="submit" data-testid="empleado-guardar">
        Guardar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  )
}

export default FormularioEmpleado
