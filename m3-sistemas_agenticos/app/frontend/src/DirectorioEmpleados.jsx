import { useEffect, useState } from 'react'

function DirectorioEmpleados({ version, onEditar, onBaja }) {
  const [empleados, setEmpleados] = useState([])
  const [departamentos, setDepartamentos] = useState([])
  const [busqueda, setBusqueda] = useState('')
  const [departamentoFiltro, setDepartamentoFiltro] = useState('')

  useEffect(() => {
    fetch('/api/departamentos')
      .then((respuesta) => respuesta.json())
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]))
  }, [])

  useEffect(() => {
    const parametros = new URLSearchParams()
    if (busqueda) parametros.set('buscar', busqueda)
    if (departamentoFiltro) parametros.set('departamento', departamentoFiltro)

    fetch(`/api/empleados?${parametros.toString()}`)
      .then((respuesta) => respuesta.json())
      .then(setEmpleados)
      .catch(() => setEmpleados([]))
  }, [busqueda, departamentoFiltro, version])

  return (
    <div>
      <input
        data-testid="buscar-empleados"
        type="text"
        placeholder="Buscar por nombre o correo"
        value={busqueda}
        onChange={(evento) => setBusqueda(evento.target.value)}
      />
      <select
        data-testid="filtro-departamento"
        value={departamentoFiltro}
        onChange={(evento) => setDepartamentoFiltro(evento.target.value)}
      >
        <option value="">Todos los departamentos</option>
        {departamentos.map((departamento) => (
          <option key={departamento} value={departamento}>
            {departamento}
          </option>
        ))}
      </select>

      {empleados.length === 0 ? (
        <p data-testid="sin-resultados">No se encontraron empleados</p>
      ) : (
        <table data-testid="tabla-empleados">
          <thead>
            <tr>
              <th>Número</th>
              <th>Nombre</th>
              <th>Puesto</th>
              <th>Departamento</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {empleados.map((empleado) => (
              <tr data-testid={`fila-empleado-${empleado.numero_empleado}`} key={empleado.id}>
                <td data-testid={`numero-empleado-${empleado.numero_empleado}`}>
                  {empleado.numero_empleado}
                </td>
                <td>{empleado.nombre}</td>
                <td>{empleado.puesto}</td>
                <td>{empleado.departamento}</td>
                <td data-testid={`estado-empleado-${empleado.numero_empleado}`}>
                  {empleado.estado === 'baja' ? 'Baja' : 'Activo'}
                </td>
                <td>
                  <button
                    data-testid={`editar-empleado-${empleado.numero_empleado}`}
                    onClick={() => onEditar?.(empleado)}
                    disabled={empleado.estado === 'baja'}
                  >
                    Editar
                  </button>
                  <button
                    data-testid={`baja-empleado-${empleado.numero_empleado}`}
                    onClick={() => onBaja?.(empleado)}
                    disabled={empleado.estado === 'baja'}
                  >
                    Dar de baja
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default DirectorioEmpleados
