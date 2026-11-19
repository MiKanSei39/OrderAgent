const BASE = '/api'
let sessionId = localStorage.getItem('orderagent-session') || crypto.randomUUID()
localStorage.setItem('orderagent-session', sessionId)

export function newSession() {
  sessionId = crypto.randomUUID()
  localStorage.setItem('orderagent-session', sessionId)
  return sessionId
}

export function getSession() { return sessionId }

export async function request(path, { method = 'GET', body, signal } = {}) {
  const response = await fetch(BASE + path, { method, signal, headers: { 'Content-Type': 'application/json', 'X-Session-ID': sessionId }, body: body === undefined ? undefined : JSON.stringify(body) })
  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    const detail = Array.isArray(data.detail) ? data.detail.map(x => x.msg).join('；') : data.detail
    throw new Error(detail || '请求失败，请检查后端服务')
  }
  return response.json()
}

export function parseSSE(buffer, onEvent, flush = false) {
  // 接受跨网络分片的帧，不对不完整JSON强行解析。
  const normalized = buffer.replace(/\r\n/g, '\n')
  const frames = normalized.split('\n\n')
  let remainder = frames.pop()
  if (flush && remainder.trim()) { frames.push(remainder); remainder = '' }
  for (const frame of frames) {
    const data = frame.split('\n').filter(line => line.startsWith('data:')).map(line => line.slice(5).trimStart()).join('\n')
    if (data && data !== '[DONE]') onEvent(JSON.parse(data))
  }
  return remainder
}

export async function chat(query, onEvent, signal) {
  const response = await fetch(BASE + '/chat', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Session-ID': sessionId }, body: JSON.stringify({ query }), signal })
  if (!response.ok || !response.body) throw new Error('无法建立对话连接，请检查服务')
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer = parseSSE(buffer + decoder.decode(value, { stream: true }), onEvent)
    }
    parseSSE(buffer + decoder.decode(), onEvent, true)
  } finally { reader.releaseLock() }
}
