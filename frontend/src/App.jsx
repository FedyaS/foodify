import { useState, useEffect } from 'react'
import './App.css'

const FOOD_OPTIONS = [
  'Pizza', 'Sushi', 'Tacos', 'Burgers', 'Pasta',
  'Ramen', 'Curry', 'Pho', 'BBQ', 'Salad',
  'Dim Sum', 'Steak', 'Seafood', 'Brunch', 'Thai',
  'Mediterranean', 'Korean', 'Ethiopian',
]

const VIBE_OPTIONS = ['Cozy', 'Lively', 'Upscale', 'Authentic', 'Hidden Gem']
const RADIUS_OPTIONS = ['1 mi', '5 mi', '10 mi', '25 mi']
const PRICE_OPTIONS = ['$10-15', '$15-25', '$25-40', '$40+']

const LOADING_MESSAGES = [
  'Analyzing your taste...',
  'Scanning nearby restaurants...',
  'Ranking your matches...',
]

const API_URL = 'http://localhost:5000'

function App() {
  const [step, setStep] = useState(0)

  const [foodPicks, setFoodPicks] = useState([])
  const [location, setLocation] = useState('Portland, OR')
  const [radius, setRadius] = useState('10 mi')
  const [vibes, setVibes] = useState([])
  const [restrictions, setRestrictions] = useState('')
  const [priceRange, setPriceRange] = useState('')
  const [specialRequests, setSpecialRequests] = useState('')

  const [loading, setLoading] = useState(false)
  const [loadingMsg, setLoadingMsg] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!loading) return
    const interval = setInterval(() => {
      setLoadingMsg((prev) => (prev + 1) % LOADING_MESSAGES.length)
    }, 2000)
    return () => clearInterval(interval)
  }, [loading])

  function toggleFood(food) {
    setFoodPicks((prev) =>
      prev.includes(food)
        ? prev.filter((f) => f !== food)
        : prev.length < 4
          ? [...prev, food]
          : prev
    )
  }

  function toggleVibe(vibe) {
    setVibes((prev) =>
      prev.includes(vibe) ? prev.filter((v) => v !== vibe) : [...prev, vibe]
    )
  }

  async function handleSubmit() {
    setStep(2)
    setLoading(true)
    setLoadingMsg(0)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(`${API_URL}/api/recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          food_picks: foodPicks,
          location,
          radius,
          vibes,
          restrictions,
          price_range: priceRange,
          special_requests: specialRequests,
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Request failed')
      setResult(data)
      setStep(3)
    } catch (err) {
      setError(err.message)
      setStep(3)
    } finally {
      setLoading(false)
    }
  }

  function handleReset() {
    setStep(0)
    setFoodPicks([])
    setVibes([])
    setRestrictions('')
    setPriceRange('')
    setSpecialRequests('')
    setResult(null)
    setError(null)
  }

  return (
    <div className="app">
      <h1>Foodify</h1>

      <div className="step-indicator">
        {[0, 1, 2, 3].map((s) => (
          <div key={s} className={`step-dot ${step >= s ? 'active' : ''}`} />
        ))}
      </div>

      {step === 0 && (
        <>
          <p className="subtitle">Tap foods that sound good to you</p>
          <div className="food-grid">
            {FOOD_OPTIONS.map((food) => (
              <div
                key={food}
                className={`food-box ${foodPicks.includes(food) ? 'selected' : ''}`}
                onClick={() => toggleFood(food)}
              >
                {food}
              </div>
            ))}
          </div>
          <p className="pick-count">
            <span>{foodPicks.length}</span> of 4 picked
          </p>
          <button
            className="btn-next"
            disabled={foodPicks.length === 0}
            onClick={() => setStep(1)}
          >
            Next
          </button>
        </>
      )}

      {step === 1 && (
        <>
          <p className="subtitle">Set your preferences</p>

          <div className="form-section">
            <label>Location</label>
            <input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Portland, OR"
            />
          </div>

          <div className="form-section">
            <label>Radius</label>
            <div className="chip-group">
              {RADIUS_OPTIONS.map((r) => (
                <div
                  key={r}
                  className={`chip ${radius === r ? 'selected' : ''}`}
                  onClick={() => setRadius(r)}
                >
                  {r}
                </div>
              ))}
            </div>
          </div>

          <div className="form-section">
            <label>Vibe</label>
            <div className="chip-group">
              {VIBE_OPTIONS.map((v) => (
                <div
                  key={v}
                  className={`chip ${vibes.includes(v) ? 'selected' : ''}`}
                  onClick={() => toggleVibe(v)}
                >
                  {v}
                </div>
              ))}
            </div>
          </div>

          <div className="form-section">
            <label>Dietary Restrictions</label>
            <input
              value={restrictions}
              onChange={(e) => setRestrictions(e.target.value)}
              placeholder="e.g. gluten-free, vegan..."
            />
          </div>

          <div className="form-section">
            <label>Price Range</label>
            <div className="chip-group">
              {PRICE_OPTIONS.map((p) => (
                <div
                  key={p}
                  className={`chip ${priceRange === p ? 'selected' : ''}`}
                  onClick={() => setPriceRange(priceRange === p ? '' : p)}
                >
                  {p}
                </div>
              ))}
            </div>
          </div>

          <div className="form-section">
            <label>Special Requests</label>
            <textarea
              value={specialRequests}
              onChange={(e) => setSpecialRequests(e.target.value)}
              placeholder="Anything else? e.g. outdoor seating, good for dates..."
            />
          </div>

          <button className="btn-next" onClick={handleSubmit}>
            Find My Food
          </button>
          <button className="btn-back" onClick={() => setStep(0)}>
            ← Back
          </button>
        </>
      )}

      {step === 2 && (
        <div className="loading-screen">
          <div className="spinner" />
          <p>{LOADING_MESSAGES[loadingMsg]}</p>
        </div>
      )}

      {step === 3 && (
        <div className="results-section">
          <h2>Results</h2>
          {error ? (
            <div className="error-box">{error}</div>
          ) : (
            <pre className="json-output">
              {JSON.stringify(result, null, 2)}
            </pre>
          )}
          <button className="btn-next" onClick={handleReset}>
            Start Over
          </button>
        </div>
      )}
    </div>
  )
}

export default App
