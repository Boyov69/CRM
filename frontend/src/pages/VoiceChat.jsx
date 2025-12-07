import { useState, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { Mic, MicOff, Phone, PhoneOff, User } from 'lucide-react'
import axios from 'axios'

function VoiceChat() {
    const location = useLocation()
    const practice = location.state?.practice || null

    const [isConnected, setIsConnected] = useState(false)
    const [isListening, setIsListening] = useState(false)
    const [time, setTime] = useState(0)
    const [transcript, setTranscript] = useState([])
    const [currentMessage, setCurrentMessage] = useState('')
    const wsRef = useRef(null)
    const transcriptEndRef = useRef(null)

    // Timer voor gespreksduur
    useEffect(() => {
        let intervalId
        if (isConnected) {
            intervalId = setInterval(() => {
                setTime((t) => t + 1)
            }, 1000)
        } else {
            setTime(0)
        }
        return () => clearInterval(intervalId)
    }, [isConnected])

    // Auto-scroll naar laatste bericht
    useEffect(() => {
        transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [transcript])

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60)
        const secs = seconds % 60
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }

    const startCall = async () => {
        try {
            // Start WebSocket verbinding
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
            const wsUrl = `${protocol}//${window.location.hostname}:5000/api/voice/stream`

            wsRef.current = new WebSocket(wsUrl)

            wsRef.current.onopen = () => {
                console.log('WebSocket verbonden met Sofie')
                setIsConnected(true)
                addMessage('system', 'Verbonden met Sofie...')
                if (practice) {
                    addMessage('system', `Gesprek met ${practice.naam || 'Praktijk'}`)
                }
            }

            wsRef.current.onmessage = (event) => {
                const data = JSON.parse(event.data)

                if (data.type === 'transcript') {
                    // Sofie's antwoord
                    if (data.speaker === 'assistant') {
                        addMessage('sofie', data.text)
                    } else {
                        // Jouw spraak
                        setCurrentMessage(data.text)
                    }
                }

                if (data.type === 'final_transcript') {
                    addMessage('user', data.text)
                    setCurrentMessage('')
                }
            }

            wsRef.current.onerror = (error) => {
                console.error('WebSocket error:', error)
                addMessage('system', 'Verbindingsfout')
            }

            wsRef.current.onclose = () => {
                console.log('WebSocket gesloten')
                setIsConnected(false)
                setIsListening(false)
                addMessage('system', 'Gesprek beëindigd')
                saveTranscript()
            }

            // Start audio opname
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
            // TODO: Audio streaming implementatie

        } catch (error) {
            console.error('Fout bij starten gesprek:', error)
            alert('Kon geen verbinding maken met Sofie. Check of de backend draait.')
        }
    }

    const endCall = () => {
        if (wsRef.current) {
            wsRef.current.close()
        }
        setIsConnected(false)
        setIsListening(false)
    }

    const toggleMute = () => {
        setIsListening(!isListening)
        // TODO: Mute/unmute audio stream
    }

    const addMessage = (speaker, text) => {
        setTranscript(prev => [...prev, {
            speaker,
            text,
            timestamp: new Date().toISOString()
        }])
    }

    const saveTranscript = async () => {
        if (transcript.length === 0) return

        try {
            await axios.post('/api/voice/save-transcript', {
                transcript,
                duration: time,
                practice_id: practice?.nr,
                practice_name: practice?.naam,
                date: new Date().toISOString()
            })
            console.log('Transcript opgeslagen')
        } catch (error) {
            console.error('Fout bij opslaan transcript:', error)
        }
    }

    return (
        <div className="container mx-auto p-4">
            <div className="card" style={{ maxWidth: '800px', margin: '0 auto' }}>
                <div className="card-header">
                    <h2 className="card-title">💬 Praat met Sofie</h2>
                    <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                        AI Sales Assistent voor HuisDocAssist
                    </p>
                </div>

                {/* Practice Info Card */}
                {practice && (
                    <div style={{
                        margin: '1rem',
                        padding: '1rem',
                        backgroundColor: '#f0f9ff',
                        borderRadius: '0.5rem',
                        border: '1px solid #0ea5e9',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '1rem'
                    }}>
                        <div style={{
                            width: '48px',
                            height: '48px',
                            borderRadius: '50%',
                            backgroundColor: '#0ea5e9',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white'
                        }}>
                            <User size={24} />
                        </div>
                        <div>
                            <div style={{ fontWeight: '600', fontSize: '1rem' }}>
                                {practice.naam || 'Onbekende Praktijk'}
                            </div>
                            <div style={{ fontSize: '0.875rem', color: '#4b5563' }}>
                                📍 {practice.gemeente || 'Onbekend'}
                            </div>
                            <div style={{ fontSize: '0.875rem', color: '#4b5563' }}>
                                📞 {practice.tel || 'Geen nummer'}
                            </div>
                        </div>
                    </div>
                )}

                {/* Voice Interface */}
                <div style={{ padding: '2rem', textAlign: 'center' }}>
                    {/* Call Controls */}
                    <div style={{ marginBottom: '2rem' }}>
                        {!isConnected ? (
                            <button
                                onClick={startCall}
                                className="btn btn-success"
                                style={{
                                    width: '80px',
                                    height: '80px',
                                    borderRadius: '50%',
                                    fontSize: '2rem'
                                }}
                            >
                                <Phone size={32} />
                            </button>
                        ) : (
                            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                                <button
                                    onClick={toggleMute}
                                    className={`btn ${isListening ? 'btn-warning' : 'btn-secondary'}`}
                                    style={{
                                        width: '60px',
                                        height: '60px',
                                        borderRadius: '50%'
                                    }}
                                >
                                    {isListening ? <Mic size={24} /> : <MicOff size={24} />}
                                </button>

                                <button
                                    onClick={endCall}
                                    className="btn btn-danger"
                                    style={{
                                        width: '60px',
                                        height: '60px',
                                        borderRadius: '50%'
                                    }}
                                >
                                    <PhoneOff size={24} />
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Timer */}
                    <div style={{
                        fontFamily: 'monospace',
                        fontSize: '1.5rem',
                        marginBottom: '1rem',
                        color: isConnected ? '#059669' : '#6b7280'
                    }}>
                        {formatTime(time)}
                    </div>

                    {/* Audio Visualizer */}
                    <div style={{
                        height: '60px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '2px',
                        marginBottom: '1rem'
                    }}>
                        {[...Array(48)].map((_, i) => (
                            <div
                                key={i}
                                style={{
                                    width: '3px',
                                    height: isListening ? `${20 + Math.random() * 80}%` : '10%',
                                    backgroundColor: isConnected ? '#3b82f6' : '#d1d5db',
                                    borderRadius: '2px',
                                    transition: 'height 0.1s',
                                    animation: isListening ? 'pulse 1.5s ease-in-out infinite' : 'none',
                                    animationDelay: `${i * 0.05}s`
                                }}
                            />
                        ))}
                    </div>

                    {/* Status */}
                    <p style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                        {!isConnected && 'Klik om te starten'}
                        {isConnected && !isListening && 'Gedempt - Klik microfoon om te spreken'}
                        {isConnected && isListening && 'Luisteren...'}
                    </p>
                </div>

                {/* Transcript */}
                {transcript.length > 0 && (
                    <div style={{
                        borderTop: '1px solid #e5e7eb',
                        padding: '1.5rem',
                        maxHeight: '400px',
                        overflowY: 'auto'
                    }}>
                        <h3 style={{ marginBottom: '1rem', fontSize: '1rem', fontWeight: '600' }}>
                            📝 Gesprek Transcript
                        </h3>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                            {transcript.map((msg, idx) => (
                                <div
                                    key={idx}
                                    style={{
                                        display: 'flex',
                                        justifyContent: msg.speaker === 'user' ? 'flex-end' : 'flex-start'
                                    }}
                                >
                                    <div
                                        style={{
                                            maxWidth: '70%',
                                            padding: '0.75rem',
                                            borderRadius: '0.5rem',
                                            backgroundColor:
                                                msg.speaker === 'sofie' ? '#eff6ff' :
                                                    msg.speaker === 'user' ? '#f0fdf4' :
                                                        '#f3f4f6',
                                            border: '1px solid',
                                            borderColor:
                                                msg.speaker === 'sofie' ? '#3b82f6' :
                                                    msg.speaker === 'user' ? '#059669' :
                                                        '#d1d5db'
                                        }}
                                    >
                                        <div style={{
                                            fontSize: '0.75rem',
                                            fontWeight: '600',
                                            marginBottom: '0.25rem',
                                            color:
                                                msg.speaker === 'sofie' ? '#1e40af' :
                                                    msg.speaker === 'user' ? '#047857' :
                                                        '#4b5563'
                                        }}>
                                            {msg.speaker === 'sofie' ? '🤖 Sofie' :
                                                msg.speaker === 'user' ? '👤 Jij' :
                                                    'ℹ️ Systeem'}
                                        </div>
                                        <div style={{ fontSize: '0.875rem' }}>
                                            {msg.text}
                                        </div>
                                    </div>
                                </div>
                            ))}

                            {/* Current message (typing) */}
                            {currentMessage && (
                                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                                    <div style={{
                                        maxWidth: '70%',
                                        padding: '0.75rem',
                                        borderRadius: '0.5rem',
                                        backgroundColor: '#f0fdf4',
                                        border: '1px dashed #059669',
                                        opacity: 0.7
                                    }}>
                                        <div style={{ fontSize: '0.875rem', fontStyle: 'italic' }}>
                                            {currentMessage}...
                                        </div>
                                    </div>
                                </div>
                            )}

                            <div ref={transcriptEndRef} />
                        </div>
                    </div>
                )}
            </div>

            <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
        </div>
    )
}

export default VoiceChat
