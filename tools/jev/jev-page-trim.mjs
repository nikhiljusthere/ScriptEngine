#!/usr/bin/env bun
// jev-page-trim — trim a large web page (or saved HTML/text) with the fast lane
// before it feeds the 27B. Same design as the bash-pruner: chunk scoring by the
// local decider (0.8b via :8018), kept content verbatim, omissions marked, full
// text archived with a recovery footer. Reuses the JEV trim engine.
//
//   ~/.bun/bin/bun jev-page-trim.mjs --url https://... --task "what I'm looking for"
//   ~/.bun/bin/bun jev-page-trim.mjs --file page.html --task "..." --out trimmed.txt
//
// Under ~4k tokens the page passes through untrimmed (no model call).
// Fail-open: any error prints the (possibly untrimmed) text and exits 0.

import { trimOutput } from "/home/goblin/tools/jev/src/opencode-jev-pruner/dist/src/output.js"
import { createLocalChunkAsker } from "/home/goblin/tools/jev/src/opencode-jev-pruner/dist/plugin/local-asker.js"
import { estimateTokens } from "/home/goblin/tools/jev/src/opencode-jev-pruner/dist/src/jev.js"
import { JevClient } from "/home/goblin/tools/jev/src/opencode-context-pruner/dist/vendor/client.js"
import crypto from "node:crypto"
import fs from "node:fs"
import os from "node:os"
import path from "node:path"

const QUESTION =
  "Does this chunk of web page content contain information the task needs? " +
  "Navigation, site chrome, and boilerplate do not count."

function arg(name, def = undefined) {
  const i = process.argv.indexOf(`--${name}`)
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : def
}

const task = arg("task")
const url = arg("url")
const file = arg("file")
const out = arg("out")
const threshold = Number(arg("threshold", "0.3"))
const minTokens = Number(arg("min-tokens", "4000"))
const archiveDir = arg("archive-dir", path.join(os.homedir(), ".opencode", "fast-jev-web"))

if (!task) {
  console.error("usage: jev-page-trim.mjs (--url <u> | --file <f>) --task <what you're looking for>")
  process.exit(2)
}
if (!url && !file) {
  console.error("need --url or --file")
  process.exit(2)
}

function htmlToText(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, "\n")
    .replace(/<style[\s\S]*?<\/style>/gi, "\n")
    .replace(/<nav[\s\S]*?<\/nav>/gi, "\n")
    .replace(/<header[\s\S]*?<\/header>/gi, "\n")
    .replace(/<footer[\s\S]*?<\/footer>/gi, "\n")
    .replace(/<!--[\s\S]*?-->/g, "\n")
    .replace(/<[^>]+>/g, "\n")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\n{3,}/g, "\n\n")
    .trim()
}

let raw = ""
if (url) {
  const res = await fetch(url, { signal: AbortSignal.timeout(60_000), redirect: "follow" })
  if (!res.ok) throw new Error(`fetch ${url} -> ${res.status}`)
  const ctype = res.headers.get("content-type") ?? ""
  raw = await res.text()
  raw = ctype.includes("html") ? htmlToText(raw) : raw
} else {
  raw = fs.readFileSync(file, "utf-8")
  if (/<\s*(html|div|p|article)[\s>]/i.test(raw.slice(0, 2_000))) raw = htmlToText(raw)
}
const text = raw.replace(/\n{3,}/g, "\n\n").trim()

const t0 = Date.now()
const est = estimateTokens(text)
if (est <= minTokens) {
  // small page: no model call needed
  const body = out ? undefined : undefined
  if (out) fs.writeFileSync(out, text)
  else process.stdout.write(text + "\n")
  console.error(`[jev-page-trim] ${text.length} chars (~${est} tokens) <= ${minTokens}: passed through untrimmed -> ${out ?? "stdout"}`)
  process.exit(0)
}

// archive the full text (0600), then trim
fs.mkdirSync(archiveDir, { recursive: true })
const sha = crypto.createHash("sha1").update(text).digest("hex")
const archivePath = path.join(archiveDir, `${sha}.txt`)
fs.writeFileSync(archivePath, text, { mode: 0o600 })

const client = new JevClient({
  apiKey: "local", model: "jev-latest",
  baseUrl: process.env.JEV_SYSTEMONE_URL ?? "http://127.0.0.1:8018/v1/systemone",
  fetch: (u, init) => fetch(u, { ...init, signal: AbortSignal.timeout(60_000) }),
})
// NOTE: bind the client explicitly — JevClient.ask reads this.apiKey.
const asker = createLocalChunkAsker((state, questions) => client.ask(state, questions), {
  concurrency: 2, deadlineMs: 30_000, question: QUESTION,
})

const r = await trimOutput(
  { command: "webpage", goal: task, output: text, fullOutputPath: archivePath },
  asker,
  {
    minTokens,
    keepThreshold: threshold,
    maxScoringRequests: 40,
    maxStateTokens: 6_000,
    compactMarkers: true,
    allowDocumentTrim: true,
    onDecision: (reason) => { globalThis.__decision = reason },
  },
)

const body = r.trimmed ? r.output : text
if (out) fs.writeFileSync(out, body)
else process.stdout.write(body + "\n")
console.error(
  `[jev-page-trim] ${(Date.now() - t0) / 1000}s; ${r.trimmed ? `trimmed ${text.length} -> ${r.output.length} chars (kept ${r.kept}, dropped ${r.dropped} chunks; decision=${globalThis.__decision ?? "?"})` : `kept untrimmed (${globalThis.__decision ?? "below_threshold"})`}; full text: ${archivePath}`)