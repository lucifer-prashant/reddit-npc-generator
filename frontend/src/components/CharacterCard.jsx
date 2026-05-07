import { useRef, useState, useEffect } from 'react'
import { toPng } from 'html-to-image'
import './CharacterCard.css'

const SENTIMENT_COLOR = { positive: '#4ADE80', negative: '#F87171', neutral: '#FBBF24' }
const SENTIMENT_LABEL = { positive: 'net positive', negative: 'chronically negative', neutral: 'emotionally unresolved' }
const VERBOSITY_LABEL = { terse: 'man of few words', moderate: 'moderate', verbose: 'cannot stop typing' }

function Avatar({ name, imageUrl, loading, onImageLoad }) {
  if (imageUrl) return (
    <>
      {loading && (
        <div className="avatar-placeholder avatar-placeholder-overlay">
          <div className="avatar-spinner" />
        </div>
      )}
      <img
        src={imageUrl}
        alt={name}
        className="avatar-img"
        style={{ opacity: loading ? 0 : 1, transition: 'opacity 0.3s ease' }}
        onLoad={onImageLoad}
        onError={onImageLoad}
      />
    </>
  )
  if (loading) return (
    <div className="avatar-placeholder">
      <div className="avatar-spinner" />
    </div>
  )
  return (
    <div className="avatar-placeholder">
      <span>{name.slice(0, 2).toUpperCase()}</span>
    </div>
  )
}

export default function CharacterCard({ profile, embedded = false, imageDelay = 0 }) {
  const cardRef = useRef(null)
  const [imageUrl, setImageUrl] = useState(profile.image_url || null)
  const [imgLoading, setImgLoading] = useState(!profile.image_url)
  useEffect(() => {
    if (profile.image_url || !profile.kling_prompt) return
    let cancelled = false
    setImgLoading(true)
    const pollinationsUrl = `https://image.pollinations.ai/prompt/${encodeURIComponent(profile.kling_prompt)}?width=512&height=512&nologo=true&model=turbo`
    const proxyUrl = `https://amnotlucifer-reddit-npc-backend.hf.space/image-proxy?url=${encodeURIComponent(pollinationsUrl)}`

    const doFetch = () => {
      if (cancelled) return
      fetch(proxyUrl)
        .then(r => { if (!r.ok) throw new Error(); return r.blob() })
        .then(blob => { if (!blob.type.startsWith('image/')) throw new Error(); return blob })
        .then(blob => {
          if (cancelled) return
          const reader = new FileReader()
          reader.onload = () => setImageUrl(reader.result)
          reader.readAsDataURL(blob)
        })
        .catch(() => { if (!cancelled) setImgLoading(false) })
    }

    const t = setTimeout(doFetch, imageDelay)
    return () => { cancelled = true; clearTimeout(t) }
  }, [profile.kling_prompt, imageDelay])

  const download = async () => {
    if (!cardRef.current) return
    const url = await toPng(cardRef.current, { pixelRatio: 2, cacheBust: true })
    const a = document.createElement('a')
    a.download = `r-${profile.subreddit}-npc.png`
    a.href = url
    a.click()
  }

  const sentColor = SENTIMENT_COLOR[profile.sentiment] || '#FBBF24'

  return (
    <div className="card-outer">
      <div className={`character-card ${embedded ? 'embedded' : ''}`} ref={cardRef}>

        {/* holographic shimmer layer */}
        <div className="card-shimmer" />

        {/* top strip */}
        <div className="card-top-strip">
          <span className="card-type-label">AVERAGE REDDITOR</span>
          <span className="card-sub-label">r/{profile.subreddit}</span>
        </div>

        {/* avatar */}
        <div className="card-avatar-wrap">
          <div className={`card-avatar-ring ${imgLoading ? 'avatar-loading' : ''}`}>
            <Avatar
              name={profile.name}
              imageUrl={imageUrl}
              loading={imgLoading}
              onImageLoad={() => setImgLoading(false)}
            />
          </div>
          <div className="avatar-glow-blob" style={{ background: sentColor }} />
        </div>

        {/* name + catchphrase */}
        <div className="card-identity">
          <h2 className="card-name">{profile.name}</h2>
          <div className="card-job">{profile.job}</div>
          <blockquote className="card-catchphrase">{profile.catchphrase}</blockquote>
        </div>

        {/* stat grid */}
        <div className="stat-grid">
          {[
            { label: 'AGE', value: profile.age_range },
            { label: 'MOOD', value: profile.mood },
            { label: 'FUEL', value: profile.drink },
            { label: 'ONLINE', value: profile.online_hours },
            { label: 'ENERGY', value: profile.energy_label || VERBOSITY_LABEL[profile.verbosity] },
            { label: 'READING LVL', value: `Grade ${profile.reading_grade}` },
          ].map(({ label, value }) => (
            <div key={label} className="stat-cell">
              <span className="stat-label">{label}</span>
              <span className="stat-value">{value}</span>
            </div>
          ))}
        </div>

        {/* sentiment bar */}
        <div className="sentiment-row">
          <span className="sentiment-dot" style={{ background: sentColor }} />
          <span className="sentiment-text" style={{ color: sentColor }}>
            {profile.sentiment_vibe || SENTIMENT_LABEL[profile.sentiment]}
          </span>
        </div>

        {/* topics */}
        {profile.topics?.length > 0 && (
          <div className="card-section">
            <div className="section-heading">INTERESTS</div>
            <div className="tag-row">
              {profile.topics.map(t => (
                <span key={t} className="tag tag-orange">{t}</span>
              ))}
            </div>
          </div>
        )}

        {/* vocab */}
        {profile.top_words?.length > 0 && !embedded && (
          <div className="card-section vocab-section">
            <div className="section-heading">VOCABULARY</div>
            <div className="tag-row">
              {profile.top_words.map(w => (
                <span key={w} className="tag tag-dim">{w}</span>
              ))}
            </div>
          </div>
        )}

        {/* owns */}
        {profile.owns?.length > 0 && (
          <div className="card-section">
            <div className="section-heading">OWNS</div>
            <ul className="owns-list">
              {profile.owns.map((item, i) => <li key={i}>{item}</li>)}
            </ul>
          </div>
        )}

        {/* footer */}
        <div className="card-footer">
          <span className="footer-text">
            Based on <strong>{profile.total_comments_analyzed}</strong> comments
          </span>
          <span className="footer-brand">SubredditProfiler</span>
        </div>

      </div>

      {!embedded && <button className="download-btn" onClick={download}>↓ DOWNLOAD CARD</button>}
    </div>
  )
}
