import { useRef, useState, useEffect } from 'react'
import { toPng } from 'html-to-image'
import CharacterCard from './CharacterCard'
import './CompareView.css'

export default function CompareView({ profileA, profileB, onReset }) {
  const [shook, setShook] = useState(false)
  const [vsVisible, setVsVisible] = useState(false)
  const sceneRef = useRef(null)

  useEffect(() => {
    // cards fly in → shake → VS appears
    const t1 = setTimeout(() => setShook(true), 600)
    const t2 = setTimeout(() => setShook(false), 1000)
    const t3 = setTimeout(() => setVsVisible(true), 700)
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3) }
  }, [])

  const download = async () => {
    if (!sceneRef.current) return
    const url = await toPng(sceneRef.current, { pixelRatio: 1.5, cacheBust: true })
    const a = document.createElement('a')
    a.download = `r-${profileA.subreddit}-vs-r-${profileB.subreddit}.png`
    a.href = url
    a.click()
  }

  return (
    <div className="compare-wrapper">
      <div className={`compare-scene ${shook ? 'shake' : ''}`} ref={sceneRef}>

        <div className="compare-side compare-left">
          <div className="side-label">r/{profileA.subreddit}</div>
          <CharacterCard profile={profileA} embedded />
        </div>

        <div className={`vs-block ${vsVisible ? 'vs-visible' : ''}`}>
          <div className="vs-flash" />
          <span className="vs-text">VS</span>
          <div className="vs-sub">who wins?</div>
        </div>

        <div className="compare-side compare-right">
          <div className="side-label">r/{profileB.subreddit}</div>
          <CharacterCard profile={profileB} embedded imageDelay={35000} />
        </div>

      </div>

      <div className="compare-note">
        ⚠ images generate sequentially (free tier limit). second portrait loads ~35s after first.
      </div>

      <div className="compare-actions">
        <button className="download-btn" onClick={download}>↓ SAVE BATTLE</button>
        <button className="reset-btn" onClick={onReset}>← Try another</button>
      </div>
    </div>
  )
}
