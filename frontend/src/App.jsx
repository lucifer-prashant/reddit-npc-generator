import { useState, useEffect, useRef } from 'react'
import CharacterCard from './components/CharacterCard'
import CompareView from './components/CompareView'
import './App.css'

const ESTIMATED_MS = 10000

const LOADING_MESSAGES = [
  "Scraping the void...",
  "Reading through the cope...",
  "Counting the reposts...",
  "Calculating NPC score...",
  "Analyzing posting patterns at 2am...",
  "Profiling the average sufferer...",
  "Consulting the algorithm...",
  "Generating your NPC...",
  "Almost there, probably...",
]

const POPULAR = [
  // drama & advice
  "AmItheAsshole", "relationship_advice", "antiwork", "unpopularopinion",
  "mildlyinfuriating", "tifu", "confessions", "offmychest", "TrueOffMyChest",
  "pettyrevenge", "ProRevenge", "entitledparents", "raisedbynarcissists",
  "survivorsofabuse", "legaladvice", "weddingplanning", "divorce",

  // finance
  "wallstreetbets", "personalfinance", "investing", "stocks", "CryptoCurrency",
  "Bitcoin", "ethereum", "financialindependence", "Frugal", "realestate",
  "smallbusiness", "entrepreneur", "passive_income", "churning",

  // tech
  "programming", "python", "javascript", "webdev", "linux", "MachineLearning",
  "ChatGPT", "artificial", "deeplearning", "gamedev", "cybersecurity",
  "hacking", "netsec", "sysadmin", "devops", "rust", "golang",
  "ProgrammerHumor", "cscareerquestions", "learnprogramming",

  // gaming
  "gaming", "pcgaming", "PS5", "xboxone", "NintendoSwitch", "Steam",
  "leagueoflegends", "Minecraft", "Fortnite", "valorant", "DotA2",
  "worldofwarcraft", "Overwatch", "pokemon", "zelda",
  "truegaming", "indiegaming", "retrogaming",

  // lifestyle
  "fitness", "loseit", "bodybuilding", "running", "yoga", "meditation",
  "vegan", "vegetarian", "keto", "intermittentfasting", "nutrition",
  "MealPrepSunday", "Cooking", "food", "Coffee", "tea", "beer", "cocktails",

  // entertainment
  "movies", "television", "Netflix", "music", "hiphopheads", "LetsTalkMusic",
  "books", "scifi", "Fantasy", "horror", "anime", "manga", "cosplay",
  "Marvel", "StarWars", "DnD", "boardgames",

  // sports
  "nfl", "nba", "soccer", "baseball", "hockey", "tennis", "formula1",
  "MMA", "boxing", "cricket", "rugbyunion", "Olympics",

  // science & education
  "science", "physics", "chemistry", "biology", "space", "Futurology",
  "askscience", "explainlikeimfive", "todayilearned", "history",
  "philosophy", "psychology", "neuro",

  // misc fun
  "cats", "dogs", "aww", "funny", "memes", "dankmemes", "shitposting",
  "AskReddit", "Showerthoughts", "LifeProTips", "CrappyDesign",
  "mildlyinteresting", "interestingasfuck", "nextfuckinglevel",
  "HumansBeingBros", "MadeMeSmile", "wholesomememes",

  // careers & life
  "jobs", "careerguidance", "college", "GradSchool",
  "personalstatement", "resumes", "interviews", "digitalnomad", "freelance",
]

const FEATURED = [
  "wallstreetbets", "vegan", "AmItheAsshole", "gaming", "antiwork", "cats",
]

export default function App() {
  const [subreddit, setSubreddit] = useState('')
  const [subredditB, setSubredditB] = useState('')
  const [compareMode, setCompareMode] = useState(false)
  const [loading, setLoading] = useState(false)
  const [profile, setProfile] = useState(null)
  const [profileB, setProfileB] = useState(null)
  const [error, setError] = useState(null)
  const [msgIdx, setMsgIdx] = useState(0)
  const [elapsed, setElapsed] = useState(0)
  const [progress, setProgress] = useState(0)
  const [showDropdown, setShowDropdown] = useState(false)
  const [activeIdx, setActiveIdx] = useState(-1)
  const startTime = useRef(null)
  const inputRef = useRef(null)
  const dropdownRef = useRef(null)

  const clean = subreddit.replace(/^r\//, '').trim()

  const filtered = clean.length > 0
    ? POPULAR.filter(s => s.toLowerCase().includes(clean.toLowerCase()) && s.toLowerCase() !== clean.toLowerCase()).slice(0, 6)
    : []

  useEffect(() => {
    if (!loading) return
    startTime.current = Date.now()
    setElapsed(0)
    setProgress(0)
    const id = setInterval(() => {
      const ms = Date.now() - startTime.current
      setElapsed(ms)
      const p = ms < ESTIMATED_MS
        ? (ms / ESTIMATED_MS) * 90
        : 90 + Math.min(9, ((ms - ESTIMATED_MS) / 15000) * 9)
      setProgress(Math.min(p, 99))
    }, 200)
    const msgId = setInterval(() => setMsgIdx(i => (i + 1) % LOADING_MESSAGES.length), 3500)
    return () => { clearInterval(id); clearInterval(msgId) }
  }, [loading])

  // close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (!dropdownRef.current?.contains(e.target) && !inputRef.current?.contains(e.target)) {
        setShowDropdown(false)
        setActiveIdx(-1)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const fetchProfile = async (sub, refresh = false) => {
    const res = await fetch('https://amnotlucifer-reddit-npc-backend.hf.space/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subreddit: sub, refresh }),
    })
    if (!res.ok) {
      const err = await res.json()
      throw new Error(err.detail || `Failed: r/${sub}`)
    }
    return (await res.json()).profile
  }

  const analyze = async (sub = clean, refresh = false) => {
    if (!sub) return
    setShowDropdown(false)
    setLoading(true)
    setError(null)
    setProfile(null)
    setProfileB(null)
    setMsgIdx(0)
    window.scrollTo({ top: 0, behavior: 'smooth' })
    try {
      if (compareMode) {
        const cleanB = subredditB.replace(/^r\//, '').trim()
        if (!cleanB) throw new Error('Enter second subreddit')
        const [pA, pB] = await Promise.all([fetchProfile(sub, refresh), fetchProfile(cleanB, refresh)])
        setProgress(100)
        setTimeout(() => { setProfile(pA); setProfileB(pB) }, 300)
      } else {
        const p = await fetchProfile(sub, refresh)
        setProgress(100)
        setTimeout(() => {
          setProfile(p)
          window.history.pushState({}, '', `?sub=${encodeURIComponent(sub)}`)
        }, 300)
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  // auto-analyze from URL param on load
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const sub = params.get('sub')
    if (sub) { setSubreddit(sub); analyze(sub) }
  }, [])

  const selectSuggestion = (s) => {
    setSubreddit(s)
    setShowDropdown(false)
    setActiveIdx(-1)
    analyze(s)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setActiveIdx(i => Math.min(i + 1, filtered.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setActiveIdx(i => Math.max(i - 1, -1))
    } else if (e.key === 'Enter') {
      if (activeIdx >= 0 && filtered[activeIdx]) {
        selectSuggestion(filtered[activeIdx])
      } else if (!loading) {
        analyze()
      }
    } else if (e.key === 'Escape') {
      setShowDropdown(false)
      setActiveIdx(-1)
    }
  }

  const reset = () => { setProfile(null); setProfileB(null); setError(null); setSubreddit(''); setSubredditB('') }
  const elapsedSec = (elapsed / 1000).toFixed(1)

  return (
    <div className="app">
      {!profile && !loading && (
        <div className="hero">
          <div className="hero-badge">NPC GENERATOR 3000</div>
          <h1 className="title">
            <span className="title-sub">Who is the average</span>
            <span className="title-main">REDDITOR</span>
            <span className="title-sub">of any subreddit?</span>
          </h1>
          <p className="hero-desc">
            Drop any subreddit. We scrape the comments, run NLP, and generate a character profile of the average person who posts there.
          </p>

          {/* search */}
          <div className="search-wrap">
            <div className="search-container">
              <span className="r-prefix">r/</span>
              <input
                ref={inputRef}
                className="search-input"
                type="text"
                placeholder="wallstreetbets"
                value={clean}
                onChange={e => { setSubreddit(e.target.value); setShowDropdown(true); setActiveIdx(-1) }}
                onFocus={() => setShowDropdown(true)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                autoFocus
              />
              {!compareMode && (
                <button className="analyze-btn" onClick={() => analyze()} disabled={loading || !clean}>
                  {loading ? '...' : 'PROFILE IT'}
                </button>
              )}
            </div>

            {/* dropdown */}
            {showDropdown && filtered.length > 0 && (
              <div className="dropdown" ref={dropdownRef}>
                {filtered.map((s, i) => (
                  <div
                    key={s}
                    className={`dropdown-item ${i === activeIdx ? 'active' : ''}`}
                    onMouseDown={() => selectSuggestion(s)}
                  >
                    <span className="dropdown-prefix">r/</span>{s}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* compare mode second input + battle button */}
          {compareMode && (
            <>
              <div className="search-wrap">
                <div className="search-container">
                  <span className="r-prefix">r/</span>
                  <input
                    className="search-input"
                    type="text"
                    placeholder="carnivore"
                    value={subredditB.replace(/^r\//, '')}
                    onChange={e => setSubredditB(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && !loading && analyze()}
                    disabled={loading}
                  />
                </div>
              </div>
              <button
                className="battle-btn"
                onClick={() => analyze()}
                disabled={loading || !clean || !subredditB.trim()}
              >
                {loading ? '...' : '⚔ BATTLE IT'}
              </button>
            </>
          )}

          {/* compare toggle */}
          <button
            className={`compare-toggle ${compareMode ? 'active' : ''}`}
            onClick={() => { setCompareMode(m => !m); setSubredditB('') }}
          >
            {compareMode ? '✕ cancel compare' : '⚔ COMPARE TWO SUBREDDITS'}
          </button>

          {/* featured chips */}
          {!compareMode && (
            <div className="featured-wrap">
              <span className="featured-label">try:</span>
              <div className="featured-chips">
                {FEATURED.map(s => (
                  <button key={s} className="chip" onClick={() => selectSuggestion(s)}>
                    r/{s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {error && <div className="error">{error}</div>}
        </div>
      )}

      {loading && (
        <div className="loading">
          <p className="loading-sub">
            {compareMode
              ? `r/${clean} vs r/${subredditB.replace(/^r\//, '').trim()}`
              : `r/${clean}`}
          </p>
          <p key={msgIdx} className="loading-msg">{LOADING_MESSAGES[msgIdx]}</p>
          <div className="progress-wrap">
            <div className="progress-bar" style={{ width: `${progress}%` }} />
          </div>
          <div className="progress-meta">
            <span className="progress-pct">{Math.floor(progress)}%</span>
            <span className="progress-time">{elapsedSec}s elapsed</span>
          </div>
        </div>
      )}

      {profile && !profileB && (
        <>
          <CharacterCard profile={profile} />
          <p className="img-disclaimer">
            portrait generates via pollinations free tier — may take up to 60s. consecutive requests queue.
          </p>
          <div className="card-actions">
            <button className="share-btn" onClick={() => {
              navigator.clipboard.writeText(window.location.href)
                .then(() => alert('Link copied!'))
            }}>⎘ SHARE LINK</button>
            <button className="refresh-btn" onClick={() => analyze(profile.subreddit, true)}>
              ↺ REFRESH DATA
            </button>
            <button className="reset-btn" onClick={reset}>← Try another</button>
          </div>
        </>
      )}

      {profile && profileB && (
        <CompareView profileA={profile} profileB={profileB} onReset={reset} />
      )}
    </div>
  )
}
