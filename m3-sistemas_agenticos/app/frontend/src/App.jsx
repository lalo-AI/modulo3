import { useState } from 'react'
import FormularioEmpleado from './FormularioEmpleado.jsx'
import DirectorioEmpleados from './DirectorioEmpleados.jsx'

function App() {
  const [version, setVersion] = useState(0)

  return (
    <div className="contenedor">
      <h1>Registrar empleado</h1>
      <FormularioEmpleado onEmpleadoCreado={() => setVersion((v) => v + 1)} />
      <h1>Directorio de empleados</h1>
      <DirectorioEmpleados version={version} />
    </div>
  )
}

export default App
