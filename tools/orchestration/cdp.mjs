// CDP driver（Node 24 內建 WebSocket；★一律 127.0.0.1、勿用 localhost——origin 不同、token 不共享）
export async function connect(wsUrl) {
  const ws = new WebSocket(wsUrl)
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej })
  let id = 0
  const pending = new Map()
  const events = []
  ws.onmessage = (m) => {
    const msg = JSON.parse(m.data)
    if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id) }
    else if (msg.method) events.push(msg)
  }
  const send = (method, params = {}) => new Promise((res, rej) => {
    const myId = ++id
    pending.set(myId, (msg) => msg.error ? rej(new Error(method + ': ' + JSON.stringify(msg.error))) : res(msg.result))
    ws.send(JSON.stringify({ id: myId, method, params }))
  })
  const evalJs = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true })
    if (r.exceptionDetails) throw new Error('eval 例外：' + JSON.stringify(r.exceptionDetails.exception?.description || r.exceptionDetails))
    return r.result.value
  }
  return { ws, send, evalJs, events, close: () => ws.close() }
}
export const sleep = (ms) => new Promise(r => setTimeout(r, ms))
