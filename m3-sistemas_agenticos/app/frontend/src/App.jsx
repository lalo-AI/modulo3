import { useState } from 'react'
import FormularioEmpleado from './FormularioEmpleado.jsx'
import DirectorioEmpleados from './DirectorioEmpleados.jsx'
import EditarEmpleado from './EditarEmpleado.jsx'
import BajaEmpleado from './BajaEmpleado.jsx'

function App() {
  const [version, setVersion] = useState(0)
  const [empleadoEnEdicion, setEmpleadoEnEdicion] = useState(null)
  const [empleadoEnBaja, setEmpleadoEnBaja] = useState(null)

  const refrescar = () => setVersion((v) => v + 1)

  return (
    <div className="contenedor">
      <h1>Registrar empleado</h1>
      <FormularioEmpleado onEmpleadoCreado={refrescar} />

      {empleadoEnEdicion && (
        <EditarEmpleado
          empleado={empleadoEnEdicion}
          onCancelar={() => setEmpleadoEnEdicion(null)}
          onGuardado={refrescar}
        />
      )}

      {empleadoEnBaja && (
        <BajaEmpleado
          empleado={empleadoEnBaja}
          onCancelar={() => setEmpleadoEnBaja(null)}
          onConfirmado={refrescar}
        />
      )}

      <h1>Directorio de empleados</h1>
      <DirectorioEmpleados
        version={version}
        onEditar={setEmpleadoEnEdicion}
        onBaja={setEmpleadoEnBaja}
      />
    </div>
  )
}

export default App
