import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>כותרת של אתר בעברית</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          הספירה היא {count}
        </button>
        <p>
          ערכו את <code>src/App.tsx</code> ושמרו כדי לבדוק את HMR
        </p>
      </div>
      <p className="read-the-docs">
      לחצו על הלוגואים של Vite ו-React כדי ללמוד עוד
      </p>
    </>
  )
}

export default App
