# deviation_reasons.md

One entry per **refuted premise**. This file records halts, not substitutions.

**A deviation is a refusal.** When a step's PREMISE is refuted, the step stops
and surfaces. It does not authorise doing something else instead. Both times
the executing agent deviated in this project and was right, it *refused* — it
declined to rewrite `arc_key`, which would have broken the only consumer.
Refusal fails safe and is cheap to review; substitution fails silently.

**Every entry must carry the raw evidence that refuted the premise** — query
output, or `file:line`. This file is agent-authored, which puts it in the same
class as reports that have been wrong five times. The evidence requirement is
what makes it checkable rather than narrative.

---

## Template

```
## <step id> — premise refuted <date>

- **premise as written:**
- **verified on tree:**            <path — a check on the wrong checkout is worse than none>
- **what the check returned:**     <raw output, or file:line>
- **why the step cannot proceed as written:**
- **what is now blocked:**
- **what would unblock it:**       <a question or a decision, not an action taken>
```

---

*No entries yet.*
