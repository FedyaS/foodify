import { useState, useEffect } from 'react'
import './App.css'

const FOOD_OPTIONS = [
  { name: 'Italian', image: '/italianfood.jpg' },
  { name: 'Mexican', image: '/mexicanfood.jpg' },
  { name: 'Chinese', image: '/chinesefood.jpg' },
  { name: 'Japanese', image: '/japanesefood.jpg' },
  { name: 'Indian', image: '/indianfood.jpg' },
  { name: 'American', image: '/americanfood.jpg' },
  { name: 'Vietnamese', image: '/vietnamesefood.jpg' },
  { name: 'Thai', image: '/thaifood.jpg' },
  { name: 'French', image: '/frenchfood.jpg' },
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

  function toggleFood(name) {
    setFoodPicks((prev) =>
      prev.includes(name)
        ? prev.filter((f) => f !== name)
        : prev.length < 4
          ? [...prev, name]
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
        <section className="w-full max-w-3xl mx-auto px-4 py-6">
          <div className="mb-8">
            <h2 className="text-3xl font-semibold mb-2">Pick Your Cravings</h2>
            <p className="subtitle">Tap foods that look good to you</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 md:gap-4">
            {FOOD_OPTIONS.map(({ name, image }) => {
              const selected = foodPicks.includes(name)
              return (
                <button
                  key={name}
                  type="button"
                  onClick={() => toggleFood(name)}
                  className={`relative w-full max-w-[180px] mx-auto text-left rounded-2xl overflow-hidden border-2 transition-all ${
                    selected ? 'border-primary shadow-lg' : 'border-transparent hover:border-primary-container'
                  }`}
                >
                  <div className="h-28 md:h-32 overflow-hidden">
                    <img src={image} alt={name} className="w-full h-full object-cover" />
                  </div>

                  {selected && (
                    <span className="absolute top-2 right-2 bg-primary text-white rounded-full w-7 h-7 grid place-items-center text-sm">
                      ✓
                    </span>
                  )}

                  <div className="px-3 py-2 text-center bg-white/90">
                    <span className={`font-medium ${selected ? 'text-primary' : ''}`}>{name}</span>
                  </div>
                </button>
              )
            })}
          </div>

          <div className="mt-6">
            <p className="pick-count mb-4">
              <span>{foodPicks.length}</span> of 4 picked
            </p>
            <button
              className="btn-next"
              disabled={foodPicks.length === 0}
              onClick={() => setStep(1)}
            >
              Next
            </button>
          </div>
        </section>
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
          <h2>Your Matches</h2>
          {error ? (
            <div className="error-box">{error}</div>
          ) : (
            <div className="card-list">
              {result?.restaurants?.map((r, i) => (
                <div className="restaurant-card" key={i}>
                  <div className="card-header">
                    <div className="card-title-area">
                      <h3 className="card-name">{r.name}</h3>
                      <div className="cuisine-tags">
                        {r.cuisine_tags?.map((tag) => (
                          <span className="cuisine-tag" key={tag}>{tag}</span>
                        ))}
                      </div>
                    </div>
                    <div className="match-badge">
                      <span className="match-number">{r.match_score}</span>
                      <span className="match-label">match</span>
                    </div>
                  </div>

                  <div className="card-info-row">
                    <span className="info-item">
                      <span className="info-icon">&#x1F4CD;</span> {r.distance}
                    </span>
                    <span className="info-item">
                      <span className="info-icon">&#x1F4B0;</span> {r.price_range}
                    </span>
                    <span className="info-item">
                      <span className="info-icon">&#x1F553;</span> {r.hours}
                    </span>
                  </div>

                  {r.vibe_tags?.length > 0 && (
                    <div className="vibe-row">
                      {r.vibe_tags.map((v) => (
                        <span className="vibe-chip" key={v}>{v}</span>
                      ))}
                    </div>
                  )}

                  {r.dietary_note && (
                    <p className="dietary-note">{r.dietary_note}</p>
                  )}

                  <p className="love-it">{r.why_youll_love_it}</p>

                  {r.menu_url && (
                    <a
                      className="menu-link"
                      href={r.menu_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      View Menu &rarr;
                    </a>
                  )}
                </div>
              ))}
            </div>
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