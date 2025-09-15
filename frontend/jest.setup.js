import '@testing-library/jest-dom'

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ id: 'test-conversation' }),
  })
)

// Mock Web Audio API
global.AudioContext = class {
  constructor() {
    this.state = 'running'
    this.sampleRate = 44100
  }
  createMediaStreamSource() {
    return {
      connect: jest.fn(),
      disconnect: jest.fn(),
    }
  }
  createGain() {
    return {
      connect: jest.fn(),
      disconnect: jest.fn(),
      gain: { value: 1 },
    }
  }
  createAnalyser() {
    return {
      connect: jest.fn(),
      disconnect: jest.fn(),
      frequencyBinCount: 1024,
      getByteFrequencyData: jest.fn(),
    }
  }
  close() {
    this.state = 'closed'
  }
}

// Mock MediaRecorder
global.MediaRecorder = class {
  constructor(stream, options = {}) {
    this.stream = stream
    this.mimeType = options.mimeType || 'audio/webm'
    this.state = 'inactive'
    this.ondataavailable = null
    this.onstart = null
    this.onstop = null
    this.onerror = null
  }
  
  start() {
    this.state = 'recording'
    if (this.onstart) this.onstart()
  }
  
  stop() {
    this.state = 'inactive'
    if (this.ondataavailable) {
      this.ondataavailable({ data: new Blob(['mock audio data']) })
    }
    if (this.onstop) this.onstop()
  }
  
  static isTypeSupported() {
    return true
  }
}

// Mock getUserMedia
Object.defineProperty(navigator, 'mediaDevices', {
  writable: true,
  value: {
    getUserMedia: jest.fn(() => Promise.resolve({
      getTracks: () => [{ stop: jest.fn() }],
    })),
  },
})

// Mock WebSocket
global.WebSocket = class {
  constructor(url) {
    this.url = url
    this.readyState = WebSocket.CONNECTING
    this.onopen = null
    this.onmessage = null
    this.onclose = null
    this.onerror = null
  }
  
  send = jest.fn()
  close = jest.fn()
  
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3
}

// Mock HTMLAudioElement
global.HTMLAudioElement = class {
  constructor() {
    this.src = ''
    this.currentTime = 0
    this.duration = 0
    this.paused = true
    this.volume = 1
    this.onloadeddata = null
    this.oncanplay = null
    this.onplay = null
    this.onpause = null
    this.onended = null
    this.onerror = null
  }
  
  play = jest.fn(() => Promise.resolve())
  pause = jest.fn()
  load = jest.fn()
}

// Mock ResizeObserver
global.ResizeObserver = class {
  constructor(callback) {
    this.callback = callback
  }
  observe = jest.fn()
  unobserve = jest.fn()
  disconnect = jest.fn()
}

// Mock IntersectionObserver
global.IntersectionObserver = class {
  constructor(callback) {
    this.callback = callback
  }
  observe = jest.fn()
  unobserve = jest.fn()
  disconnect = jest.fn()
}
