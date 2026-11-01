---
type: regex
target: { source: file, path: .stub/requests.log }
pattern: '^(?:GET [^\n]*\n)+$'
arm: both
---
