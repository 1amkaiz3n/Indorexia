const KEY = 'indorexia_visitor_id'

function generate(): string {
  return crypto.randomUUID
    ? crypto.randomUUID()
    : 'v-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10)
}

export function getVisitorId(): string {
  let id = localStorage.getItem(KEY)
  if (!id) {
    id = generate()
    localStorage.setItem(KEY, id)
  }
  return id
}
