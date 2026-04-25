import { useState } from 'react'

function App() {
  const [message, setMessage] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleClick = async () => {
    setLoading(true)
    try {
      const res = await fetch('http://localhost:5000/api/test')
      const data = await res.json()
      setMessage(data.message)
    } catch (err) {
      setMessage('Error: Could not reach backend')
    }
    setLoading(false)
  }

  return (
    <div className="container text-center mt-5">
      <h1>Foodify</h1>
      <button className="btn btn-primary mt-3" onClick={handleClick} disabled={loading}>
        {loading ? 'Loading...' : 'Test API'}
      </button>
      {message && (
        <div className="alert alert-success mt-4">{message}</div>
      )}
    </div>
  )
}

export default App
