# Semantic Tools and Planning

## 5. The Semantic Tool Layer

This is the new piece, and it's what lets one small model cover "all sorts of animations" without
retraining per animation type. It's a library of plain Python functions in your backend — **not**
a second MCP server, just internal abstractions that generate the right `bpy` code for whichever
rig is currently loaded (by looking up its manifest, see §8) and execute it via blender-mcp's
`execute_blender_code`.

Starting tool set (grow this over time; adding a tool doesn't require retraining the model if the
Plan schema already has a slot for it — see §6):

| Tool | Covers |
|---|---|
| `lip_sync(character, audio_file, transcript?)` | Speech — pulls the Rhubarb viseme timeline and maps it to this rig's mouth shape keys/bones |
| `set_emotion(character, emotion, intensity)` | Facial expression blend (brows, mouth corners, eye shape) |
| `gesture(character, type, start, end, intensity)` | Wave, raise-hand, point, shrug, and other short arm/hand actions |
| `look_at(character, target, start, end)` | Eye/head aim at camera, another character, or a point |
| `blink(character, rate)` | Natural / increased / rare blink cycles |
| `head_motion(character, style, intensity)` | Nodding, small tension movements, idle sway |
| `create_walk(character, path, speed, style)` | Locomotion — walk/run cycles along a path |
| `idle(character, style)` | Subtle breathing/weight-shift loop for moments with no explicit action |
| `camera_pan(...)` / `camera_follow(...)` / `camera_shot(type)` | Camera framing and movement |
| `export_video(output_path, mux_audio=True)` | Final render + ffmpeg mux |

Each tool internally resolves *this specific rig's* controller names from the rig manifest/RAG
before generating code — the model calling `gesture("Aiko", "wave", 2.3, 3.1, 0.6)` never needs to
know that Aiko's arm controller is called `CTRL_ArmR_IK`.

---

## 6. The Animation Intent Plan

This is the model's actual fine-tuning *output target* — a structured, rig-agnostic JSON document
covering any combination of animation types in one request:

```json
{
  "character": "Aiko",
  "duration_seconds": 5.2,
  "emotion": { "primary": "nervous", "intensity": 0.6 },
  "body_language": { "posture": "tense_shoulders", "energy": "low" },
  "head_motion": { "style": "small_movements", "nod_frequency": "rare" },
  "eye_behavior": { "target": "camera", "blink_rate": "increased", "eye_darts": true },
  "lip_sync": { "enabled": true, "audio_file": "line_04.wav", "transcript": "Hello everyone..." },
  "gestures": [
    { "start": 2.3, "end": 3.1, "type": "raise_right_hand", "intensity": 0.4 },
    { "start": 4.0, "end": 4.6, "type": "adjust_collar" }
  ],
  "locomotion": null,
  "camera": { "shot": "medium_close_up", "movement": "static" },
  "notes": "Keep gestures small and hesitant to match the nervous emotional state."
}
```

The Plan Compiler (deterministic, no LLM) walks this JSON and calls the matching Semantic Tools —
`lip_sync(...)`, `gesture("raise_right_hand", 2.3, 3.1, 0.4)`, `camera_shot("medium_close_up")`,
etc. Because `locomotion` is just `null` here and becomes a populated object for a walk request,
**one schema covers every animation type you listed** — speech, gesture, full-body movement,
camera direction — instead of needing a separate model or dataset per category.

> **On the multi-stage "Intent → Emotion → Gesture → Camera → Validator" pipeline from the other
> conversation:** it's a reasonable idea for a production studio with GPU headroom to spare, but
> running five or six sequential LLM calls per request adds real latency on a single 6GB card
> serving one small local model. Start with **one call producing the whole Plan above in a single
> pass** — a well-built dataset (§7) can teach a 3B/7B model to reason through emotion, gesture,
> and camera together. Only split it into sequential prompts *to the same model* (different system
> prompts per stage, not different models) later, and only if evaluation shows the single-pass
> version is conflating concerns badly enough to justify the extra latency.

The Animation Studio UI should show this Plan before compiling it — see §10 — so you can nudge a
slider (emotion intensity, gesture timing) without touching a JSON file directly.

---

## 7. The Fine-Tuning Dataset

Same distillation-and-validate approach as before, but the target output is now a Plan, not code:

1. **Bootstrap** — use a strong model you already have access to (Claude, or an Antigravity-style
   session) to generate `(character context + request) → Animation Plan` pairs across a wide
   variety of requests: dialogue delivery, gestures, walk cycles, camera direction, reactive
   emotional beats. Include a short reasoning trace before the JSON, the way an animator would
   think it through — this is genuinely useful training signal, not filler:
   ```
   Reasoning: nervous before a speech -> avoid large gestures, keep shoulders tense, increase
   blink frequency, add small eye darts, keep head motion minimal.

   Plan: { ...json... }
   ```
2. **Validate mechanically** — run every candidate Plan through the *real* Plan Compiler + Semantic
   Tool Layer in headless Blender and check it executes without error and produces sane keyframes.
   This is free (CPU time only) and catches Plans that reference fields your tool layer doesn't
   support yet.
3. **Curate lightly** — spot-check survivors before they enter the training set. 500 clean,
   verified examples reliably beats 5,000 noisy ones for behavior/format adaptation.
4. **Cover the long tail on purpose** — dialogue delivery across emotions, the full gesture list,
   locomotion requests, camera-only requests, combined requests ("walk over while waving, nervous"),
   and a few **"ask instead of guess"** examples for when a request needs a capability the current
   rig genuinely doesn't have (e.g., asking a rig with no leg rig to walk) — the target output
   should be a clarifying/limitation note, not an invented capability.

---

## 8. Understanding "Production Quality" Rigs

The model never needs literal bone names anymore — that job moved to the Semantic Tool Layer. But
the *Planning* model still needs to know what a given rig **can do**, so it doesn't plan a walk
cycle for an upper-body-only rig. The Rig Indexer now produces two things instead of one:

1. **Literal manifest** (as before — bone hierarchy, shape key names, naming-convention guesses) —
   consumed only by the Semantic Tool Layer when it compiles a Plan into real keyframes.
2. **Capability summary** (new) — a short, human-readable abstraction fed into the Planning model's
   context: *"Aiko: full upper-body FK+IK, 9 facial visemes (ARKit subset), no leg rig — cannot
   walk, neck rotation capped at 35°, uses a Rigify face-rig extension."* This is what makes the
   model's reasoning rig-aware without ever exposing it to bone names directly.

```json
{
  "character_name": "Aiko_v3",
  "blend_file": "aiko_v3_rigged.blend",
  "capability_summary": "Full upper-body FK+IK, 9 facial visemes (ARKit subset), no leg/locomotion rig, neck rotation capped at 35 degrees.",
  "armature": {
    "name": "AikoRig",
    "bone_count": 214,
    "face_bones": ["jaw", "tongue_01", "tongue_02", "lip_upper_L", "lip_upper_R"],
    "naming_convention_guess": "Rigify (face rig extension)"
  },
  "shape_keys": {
    "mesh": "Aiko_Head",
    "basis": "Basis",
    "keys": ["viseme_AA", "viseme_E", "viseme_FV", "viseme_L", "viseme_M", "viseme_O", "viseme_U", "viseme_WQ", "eyeBlink_L", "eyeBlink_R"],
    "naming_convention_guess": "ARKit-52 subset"
  },
  "existing_actions": ["idle_loop", "blink_cycle"],
  "fps": 24,
  "notes_for_llm": "No neutral-pose action found; use the 'Basis' shape key as the mouth-closed reference."
}
```

Stored in the RAG store as a retrievable per-character document; the capability summary is also
injected directly into context for the current session so the Planning model always knows the
current rig's limits without a retrieval round-trip.

**Optional, later:** a lightweight **rig graph** (which controller affects which region — e.g.
"which control moves the upper lip") instead of a flat manifest, so the Semantic Tool Layer can
answer structural questions when compiling a Plan for an unfamiliar rig convention. This is worth
building once you have enough rigs that flat name-matching starts missing things — not a Phase 1–4
requirement. A plain Python dict/`networkx` graph alongside the manifest is enough; you don't need
a dedicated graph database at this scale.

---

## 9. Pipeline Walkthrough — Two Examples

**A. "Make her nervous before this speech, using this audio"**
1. Rhubarb extracts a viseme timeline from the audio (deterministic, no LLM).
2. Backend retrieves Aiko's capability summary + personality sheet from RAG.
3. Planning model produces the Animation Plan in §6 (emotion, blinks, gestures, lip_sync, camera).
4. You review/tweak the Plan in the UI (§10).
5. Plan Compiler calls `set_emotion`, `blink`, `gesture`, `lip_sync`, `camera_shot` in sequence.
6. Each tool resolves Aiko's actual controllers and executes via blender-mcp.
7. `export_video` renders and muxes the audio in with ffmpeg.

**B. "Have her walk across the room and wave at the camera"**
1. No audio involved — `lip_sync` stays disabled in the Plan.
2. Capability summary check: does this rig have a locomotion rig? (If not, this is exactly the
   "ask instead of guess" case from §7 — the model should say so, not fake it.)
3. Plan includes a populated `locomotion` object (path, speed, style) and a `gesture` entry for the
   wave, timed to land near the end of the walk.
4. Plan Compiler calls `create_walk` then `gesture("wave", ...)` then `camera_follow`.
5. Same render/export step as above.

Same model, same schema, same tool layer — different Plan contents. This is the concrete answer to
"it should be able to do all sorts of animations."
