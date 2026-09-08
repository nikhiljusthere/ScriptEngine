import base64, json, re, subprocess, time, pathlib, urllib.request, urllib.error
URL, MODEL = "http://localhost:18080/v1/chat/completions", "qwen3.8-27b-ninfer"
class ModelDown(Exception): pass                                   # council fix 3/5: model-unavailable ≠ no-op (§6.5 named state)
DENY = ("XF86", "SUPER", "CTRL+ALT+BACKSPACE", "CTRL+ALT+DELETE")  # guard 6a: consequence combos (X restart, power, media)
W, H = (int(v) for v in subprocess.run(["xdotool", "getdisplaygeometry"], capture_output=True, text=True).stdout.split())  # guard 6c
LOG, STOP = pathlib.Path("reports/master-work/work_log.md"), pathlib.Path("reports/master-work/STOP"); TICK, K, MAX_TICKS, MAX_NOOPS = 20, 10, 120, 5
ALLOW = ("click", "double_click", "type", "key", "scroll", "wait", "done", "abort")
TASK = "Finish the pcloop goal in plan/state.md §state; one small action per reply."  # B sets per session
def log(msg):
    with LOG.open("a") as f: f.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] {msg}\n")
def shot():
    subprocess.run(["scrot", "/tmp/pcloop.png"], check=True, stdout=subprocess.DEVNULL); return base64.b64encode(pathlib.Path("/tmp/pcloop.png").read_bytes()).decode()
def ask(img):
    tail = "\n".join(LOG.read_text().splitlines()[-K:]) if LOG.exists() else ""
    req = urllib.request.Request(URL, data=json.dumps({"model": MODEL, "max_tokens": 2048, "messages": [{"role": "user", "content": [
        {"type": "text", "text": f"Task: {TASK}\nRecent work_log:\n{tail}\nReply with ONE JSON object; action in: " + "|".join(ALLOW)},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + img}}]}]}).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r: body = r.read()     # 90 s hard timeout (guard 2)
    except urllib.error.HTTPError as e:
        if e.code >= 500: raise ModelDown(f"HTTP {e.code}")                     # fix 3: saturated/dead model = transient, retry next tick
        raise RuntimeError(f"HTTP {e.code} (4xx — a real error, counts as no-op)") from e
    except (TimeoutError, urllib.error.URLError) as e:
        raise ConnectionError(str(e)[:60])                                      # fix 3: unreachable → main's builtin-ConnectionError path (retry, not a no-op)
    return json.loads(re.search(r"\{.*\}", json.loads(body)["choices"][0]["message"]["content"], re.S).group(0))
def run(a):  # argv-list xdotool only: model-supplied text/combo can never become shell injection
    n, x, y = a.get("action"), a.get("x", 0), a.get("y", 0)
    if n not in ALLOW: return "reject"
    if n == "key" and any(d in str(a.get("combo", "")).upper() for d in DENY): return "reject"   # guard 6a: combo denylist
    if n == "type" and len(str(a.get("text", ""))) > 200: return "reject"                        # guard 6b: type cap
    if n in ("click", "double_click", "scroll") and not (0 <= int(x) < W and 0 <= int(y) < H): return "reject"  # guard 6c: geometry
    if n == "wait": time.sleep(min(int(a.get("seconds", 2)), 10)); return "no-op"
    if n in ("done", "abort"): return n
    cmd = {"click": ["xdotool", "mousemove", str(x), str(y), "click", str(a.get("button", 1))],
           "double_click": ["xdotool", "mousemove", str(x), str(y), "click", "--repeat", "2", "1"],
           "type": ["xdotool", "type", "--delay", "30", a["text"]],
           "key": ["xdotool", "key", a["combo"]],
           "scroll": ["xdotool", "mousemove", str(x), str(y), "click", "--repeat", str(a.get("amount", 3)),
                      {"up": "4", "down": "5", "left": "6", "right": "7"}.get(a.get("direction", "down"), "5")]}[n]
    subprocess.run(cmd, check=True); return "ok"
def main():
    noops = ticks = 0
    while ticks < MAX_TICKS:
        if STOP.exists(): log(f"HALT pcloop: STOP veto ({STOP.read_text().strip()})"); return
        try: a = ask(shot())
        except ModelDown as e: log(f"FAIL pcloop: model-down ({str(e)[:60]}) — named state §6.5, retry next tick, NOT a no-op"); res = "model-down"
        except ConnectionError as e: log(f"FAIL pcloop: model unreachable ({str(e)[:60]}) — timeout incl. the 90 s read-timeout; retry next tick, NOT a no-op (fix 3)"); res = "model-down"
        except Exception as e: log(f"FAIL pcloop: vision ({str(e)[:80]})"); res = "no-op"
        else: res = run(a); log(f"ACT pcloop: {json.dumps(a)} -> {res}")
        ticks += 1
        if res in ("done", "abort"): return
        noops = noops + 1 if res in ("no-op", "reject") else 0   # explicit wait/reject only — model-down never counts (fix 3)
        if noops >= MAX_NOOPS: log("HALT pcloop: no-op streak"); return
        time.sleep(TICK)
if __name__ == "__main__": main()
