# Frontend: Animation Pipeline UI

React 19 + TypeScript + Vite UI for the Blender LLM Animator backend. It has three working studios:

| Studio | Component | Backend endpoints |
| :--- | :--- | :--- |
| Fine-Tuning Studio | `src/components/FineTuningStudio.tsx` | `/api/dataset/generate`, `/api/dataset/list`, `/api/finetune/status` |
| Knowledge Studio (RAG) | `src/components/KnowledgeStudio.tsx` | `/api/knowledge/add`, `/api/knowledge/query` |
| Animation Studio | `src/components/AnimationStudio.tsx` | `/api/plan`, `/api/compile` |

The "Blender Bridge" tab is a placeholder.

## Getting started

Requires Node.js 20.19+ and a running backend (see the root README).

```bash
npm ci            # install exact versions from package-lock.json
npm run dev       # dev server on http://localhost:5173
```

## Scripts

| Command | What it does |
| :--- | :--- |
| `npm run dev` | Vite dev server with HMR |
| `npm run build` | Type-check (`tsc -b`) and build to `dist/` |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Run [oxlint](https://oxc.rs) |

## Configuration

The backend URL comes from `VITE_API_URL` (default `http://localhost:8000`):

```bash
cp .env.example .env.local   # git-ignored
# edit VITE_API_URL=http://192.168.1.20:8000
```

If you serve the UI from a different origin than `http://localhost:5173`, add it to the backend's `CORS_ORIGINS`.

All requests go through `src/api.ts` (`getJson` / `postJson`), which throws a readable `Error` for non-2xx responses, including FastAPI 422 validation details.
