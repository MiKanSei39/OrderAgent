import test from 'node:test'
import assert from 'node:assert/strict'

globalThis.localStorage = { getItem: () => null, setItem() {} }
const { parseSSE } = await import('../src/api/client.js')

test('SSE保留未完成的JSON帧，中文不丢失', () => {
  const events = []
  let buffer = parseSSE('data: {"type":"token","content":"你', item => events.push(item))
  assert.equal(events.length, 0)
  buffer = parseSSE(buffer + '好"}\n\ndata: {"type":"done"}\n\n', item => events.push(item))
  assert.equal(buffer, '')
  assert.deepEqual(events.map(x => x.type), ['token', 'done'])
  assert.equal(events[0].content, '你好')
})

test('SSE支持CRLF、注释和结束标记', () => {
  const events = []
  parseSSE(': heartbeat\r\n\r\ndata: {"type":"done"}\r\n\r\ndata: [DONE]\r\n\r\n', item => events.push(item))
  assert.equal(events.length, 1)
})
