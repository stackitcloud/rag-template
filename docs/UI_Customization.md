# UI Customization Guide

This guide explains how to customize the RAG Template frontend applications, including bot branding, theming, and logo configuration.

Note: In this document, “frontend” refers to the folder at services/frontend in this repository. All links below point to files in that folder or elsewhere in this repo.

## Overview

The RAG Template frontend supports several customization options:

- **Bot name** and **initial message**
- **Logos** for light and dark mode
- **Brand colors and themes** (Tailwind v4 + daisyUI v5)

## Quick Start (Most Common Rebranding)

If you just want to rename/rebrand the UI, these are the usual knobs:

1. **Bot display name**: set `VITE_BOT_NAME`
2. **Welcome message text**: edit `services/frontend/libs/i18n/chat/en.json` → `chat.initialMessage` (keep `{bot_name}`)
3. **Navigation logo**: set `VITE_UI_LOGO_PATH_LIGHT` / `VITE_UI_LOGO_PATH_DARK` and add the files under each app’s `public/assets/`
4. **Brand colors**: edit `services/frontend/libs/ui-styles/src/tailwind.css` (daisyUI theme tokens)
5. **App titles + favicons**: edit `services/frontend/apps/*/index.html` and `services/frontend/apps/*/public/favicon.ico`

## How Configuration Works (Build-Time vs Runtime)

Vite apps are **static builds**. By default, all `VITE_*` variables are read at **build time** and baked into the built JS/CSS.

This repository also supports **runtime overrides** in container deployments:

- `services/frontend/.env.production` contains placeholder values like `VITE_BOT_NAME=VITE_BOT_NAME`
- `services/frontend/env.sh` replaces those placeholder strings inside built `*.js`/`*.css` files at startup

That replacement only happens if you **run `env.sh` against the directory that nginx serves** (default: `/usr/share/nginx/html`).

| Scenario | Where to set `VITE_BOT_NAME` | When it takes effect |
|---|---|---|
| Local dev (`npm run chat:serve`) | `services/frontend/.env.development` (or `.env.development.local`) | on server restart |
| Static hosting (S3, nginx without `env.sh`) | build environment or `services/frontend/.env.production` with real values | at build time |
| Docker/Kubernetes (with `env.sh`) | container env vars + `env.sh` run at startup (in `infrastructure/rag/values.yaml` set `frontend.envs.vite.VITE_BOT_NAME`) | at container startup |

## Configuration Options

### Environment Variables

UI rebranding uses `VITE_*` environment variables (see “Build-Time vs Runtime” above):

| Variable | Description | Default Value | Example |
|----------|-------------|---------------|---------|
| `VITE_BOT_NAME` | The AI assistant's display name | "Knowledge Agent" | "DocBot" |
| `VITE_UI_LOGO_PATH` | Common path to the main navigation logo (fallback for both light/dark) | "/assets/navigation-logo.svg" | "/assets/my-logo.png" |
| `VITE_UI_LOGO_PATH_LIGHT` | Path to logo used in light mode (falls back to `VITE_UI_LOGO_PATH`) | — | "/assets/logo-light.svg" |
| `VITE_UI_LOGO_PATH_DARK` | Path to logo used in dark mode (falls back to `VITE_UI_LOGO_PATH`) | — | "/assets/logo-dark.svg" |
| `VITE_UI_THEME_DEFAULT` | Default theme when user first visits | "dark" | "light" |
| `VITE_UI_THEME_OPTIONS` | Available theme options (comma-separated) | "light,dark" | "light" |

### Bot Name & Welcome Message

The bot name is read from `VITE_BOT_NAME` (see `services/frontend/libs/shared/settings.ts`) and is used in:

- the sender name for assistant chat bubbles (`services/frontend/libs/chat-app/ui/ChatMessages.vue`)
- the first “welcome” message when a chat session starts (`services/frontend/libs/chat-app/data-access/+state/chat.store.ts`)

#### Change the bot name

- **Local development**: set `VITE_BOT_NAME` in `services/frontend/.env.development` (or create `services/frontend/.env.development.local`) and restart `npm run chat:serve`.
- **Build-time (no runtime injection)**: set `VITE_BOT_NAME` in your environment before building (for example `VITE_BOT_NAME="Acme Assistant" npm -C services/frontend run chat:build`).
- **Runtime (Docker/Kubernetes)**: set `VITE_BOT_NAME` in the container environment and ensure `services/frontend/env.sh` runs (see “Docker Deployment” / “Kubernetes/Helm Deployment” below).

#### Change the welcome message text

Edit the translation string and keep `{bot_name}` for interpolation:

Files:
- `services/frontend/libs/i18n/chat/en.json`
- `services/frontend/libs/i18n/chat/de.json`

### Logo Customization

The logo appears in the navigation header of both chat and admin applications. You can configure separate logos for light and dark themes.

**Setting Custom Logos:**

1. Place your logo files in the app assets directory:

- Chat app: services/frontend/apps/chat-app/public/assets/ ([open folder](../services/frontend/apps/chat-app/public/assets))
- Admin app: services/frontend/apps/admin-app/public/assets/ ([open folder](../services/frontend/apps/admin-app/public/assets))

1. Set the environment variables:

  ```bash
  # Preferred: specify light and dark explicitly
  VITE_UI_LOGO_PATH_LIGHT=/assets/my-logo-light.svg
  VITE_UI_LOGO_PATH_DARK=/assets/my-logo-dark.svg

  # Optional: common fallback used when LIGHT/DARK are not set
  VITE_UI_LOGO_PATH=/assets/my-logo.svg
  ```

**Logo Requirements:**

- **Format**: SVG, PNG, or JPG
- **Size**: Optimized for 128px width (will be scaled to w-32 class)
- **Background**: Transparent recommended for better theme compatibility
- **Path**: Must be accessible from the public assets directory

**Fallback order:**

- Light: `VITE_UI_LOGO_PATH_LIGHT` → `VITE_UI_LOGO_PATH` → `/assets/navigation-logo-light.svg` (default asset exists in both apps: [chat](../services/frontend/apps/chat-app/public/assets/navigation-logo-light.svg), [admin](../services/frontend/apps/admin-app/public/assets/navigation-logo-light.svg))
- Dark: `VITE_UI_LOGO_PATH_DARK` → `VITE_UI_LOGO_PATH` → `/assets/navigation-logo-dark.svg` (default asset exists in both apps: [chat](../services/frontend/apps/chat-app/public/assets/navigation-logo-dark.svg), [admin](../services/frontend/apps/admin-app/public/assets/navigation-logo-dark.svg))

**Examples:**

```bash
# Separate light/dark logos
VITE_UI_LOGO_PATH_LIGHT=/assets/company-logo-light.svg
VITE_UI_LOGO_PATH_DARK=/assets/company-logo-dark.svg

# Only a common logo
VITE_UI_LOGO_PATH=/assets/company-logo.svg
```

### Other Rebranding Assets

#### Chat avatars (user + assistant)

The chat bubbles use static avatar files by default:

- `services/frontend/apps/chat-app/public/assets/ai-avatar.svg`
- `services/frontend/apps/chat-app/public/assets/user.svg`

Replace those files (keep the same filenames), or update the constants in `services/frontend/libs/chat-app/ui/ChatMessages.vue`.

#### Favicons

- `services/frontend/apps/chat-app/public/favicon.ico`
- `services/frontend/apps/admin-app/public/favicon.ico`

#### Browser tab titles

- `services/frontend/apps/chat-app/index.html` (`<title>`)
- `services/frontend/apps/admin-app/index.html` (`<title>`)

### Theme System (Tailwind v4 + daisyUI v5)

The frontend uses Tailwind v4 with daisyUI v5. In the following, we describe how to customize the theme using central CSS (recommended for brand colors shared by both apps):

- File: `services/frontend/libs/ui-styles/src/tailwind.css`
- This file loads Tailwind v4 and defines daisyUI themes via CSS `@plugin` blocks.
- Themes are defined in two blocks:
  - `light`: Light mode
  - `dark`: Dark mode (default via `VITE_UI_THEME_DEFAULT`)
- Update semantic tokens under the `@plugin "daisyui/theme"` blocks, for example:

```css
--color-primary: #a90303;            /* CTA/buttons */
--color-primary-content: #ffffff;    /* readable text on primary */
--color-base-100: #ffffff;           /* page background */
--color-base-200: #EDEDED;           /* cards */
```

Common class ↔ token mapping:

- `btn btn-primary`, `bg-primary`, `text-primary` → `--color-primary` / `--color-primary-content`
- `bg-secondary`, `text-secondary-content` → `--color-secondary` / `--color-secondary-content`
- `bg-base-100/200/300`, `border-base-300`, `text-base-content` → `--color-base-*` / `--color-base-content`

Custom CSS variables used by this repo are also defined per theme in `tailwind.css`:

- `--scrollbar-track` / `--scrollbar-thumb` (scrollbar styling)
- `--base-200-highlight` (highlight “jump to source” anchors)

Theme behavior:

1. **Set Default Theme:**

   ```bash
   # Users will see dark mode by default
   VITE_UI_THEME_DEFAULT=dark
   ```

1. **Configure Available Options:**

   ```bash
   # Only allow light mode (remove theme toggle)
   VITE_UI_THEME_OPTIONS=light

   # Support both themes (default)
   VITE_UI_THEME_OPTIONS=light,dark
   ```

**Theme Behavior:**

- Theme preference is saved in browser's localStorage
- Theme persists across browser sessions
- The built-in theme toggle is shown only when both `light` and `dark` are available
- Manual theme switching overrides the default setting
- Theme selection is stored under `localStorage["app-theme"]` and applied via `html[data-theme]`

### Markdown / Chat Content Styling

Chat answers, user prompts, and citations are rendered from Markdown via `marked` (see `services/frontend/libs/shared/utils/src/lib/marked.utils.ts`) and styled via global CSS in `services/frontend/libs/shared/global.css`.

Rebrandable bits:

- Code blocks: `--chat-code-*` variables and `.chat-code-block*` styles
- Typography: `.prose` overrides keep headings/links readable across themes

## Development Setup

### Local Development

Vite reads env files from `services/frontend/`. Common ones:

- `services/frontend/.env.development` / `services/frontend/.env.development.local` (local dev)
- `services/frontend/.env.production` / `services/frontend/.env.production.local` (production build)

1. **Create/modify an env file** (recommended: `services/frontend/.env.development.local`):

   ```bash
   # Bot customization
   VITE_BOT_NAME=Development Bot

   # Logo customization
   VITE_UI_LOGO_PATH_LIGHT=/assets/dev-logo-light.svg
   VITE_UI_LOGO_PATH_DARK=/assets/dev-logo-dark.svg
   # Optional common fallback
   # VITE_UI_LOGO_PATH=/assets/dev-logo.svg

   # Theme customization
   VITE_UI_THEME_DEFAULT=light
   VITE_UI_THEME_OPTIONS=light,dark
   ```

1. **Start development server** (scripts are defined in [services/frontend/package.json](../services/frontend/package.json)):

   ```bash
   npm run chat:serve
   # or
   npm run admin:serve
   ```

### Docker Deployment

The app Docker images are built from:

- `services/frontend/apps/chat-app/Dockerfile`
- `services/frontend/apps/admin-app/Dockerfile`

These images contain:

- built files under `/app/frontend` (read-only)
- `env.sh` at `/app/env.sh`
- nginx serving `/usr/share/nginx/html`

To use runtime variables in Docker, you must ensure the container runs:

```sh
cp -r /app/frontend/. /usr/share/nginx/html && /bin/sh /app/env.sh
```

before nginx serves the files (otherwise placeholders like `VITE_BOT_NAME` will remain).

See `services/frontend/env.sh` for details, including `TARGET_DIR` override.

### Kubernetes/Helm Deployment

The Helm chart wires env vars via `frontend.envs.vite` into a ConfigMap and mounts a writable `/usr/share/nginx/html`. It also runs the copy + `env.sh` step (see `infrastructure/rag/templates/frontend/deployment.yaml`).

1. **Configure in your Helm `values.yaml`** (example values at [infrastructure/rag/values.yaml](../infrastructure/rag/values.yaml)):

   ```yaml
   frontend:
     envs:
       vite:
         VITE_BOT_NAME: "Enterprise Knowledge Bot"
         VITE_UI_LOGO_PATH_LIGHT: "/assets/enterprise-logo-light.svg"
         VITE_UI_LOGO_PATH_DARK: "/assets/enterprise-logo-dark.svg"
         VITE_UI_THEME_DEFAULT: "dark"
         VITE_UI_THEME_OPTIONS: "light,dark"
   ```

2. **Or use ConfigMap:**

   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: frontend-config
   data:
     VITE_BOT_NAME: "K8s Assistant"
     VITE_UI_LOGO_PATH_LIGHT: "/assets/k8s-logo-light.svg"
     VITE_UI_LOGO_PATH_DARK: "/assets/k8s-logo-dark.svg"
   ```

## Advanced Customization

### Adding Custom Themes

This repo is optimized for `light`/`dark` theming. You can still add a custom theme, but note:

- The built-in UI toggle only switches between `light` and `dark` (`services/frontend/libs/shared/ui/ThemeToggle.vue`).
- If you want a custom theme without adding a theme picker, set `VITE_UI_THEME_OPTIONS` to a single theme and the toggle will disappear.

To add a custom theme, define it in `services/frontend/libs/ui-styles/src/tailwind.css`:

CSS (Tailwind v4):

```css
@plugin "daisyui/theme" {
  name: "brand-red";
  --color-primary: #a90303;
  --color-primary-content: #ffffff;
  /* ... other tokens ... */
}
```

Then select it via env vars:

```bash
VITE_UI_THEME_DEFAULT=brand-red
VITE_UI_THEME_OPTIONS=brand-red
```

### Internationalization

Bot names and messages support internationalization:

1. **Modify translation files:**

  ```json
  // services/frontend/libs/i18n/chat/en.json
   {
     "chat": {
       "initialMessage": "Hi 👋, I'm your AI Assistant {bot_name}, here to help!"
     }
   }
   ```

1. **Add language-specific bot names:**

  ```json
  // services/frontend/libs/i18n/chat/de.json
   {
     "chat": {
       "initialMessage": "Hallo 👋, ich bin dein KI-Assistent {bot_name}, hier um zu helfen!"
     }
   }
   ```
  Files: [en.json](../services/frontend/libs/i18n/chat/en.json), [de.json](../services/frontend/libs/i18n/chat/de.json)

## Troubleshooting

### Bot Name Not Updating

- **Issue**: Bot name stays at the default or shows a placeholder value (e.g. `VITE_BOT_NAME`)
- **Cause**: Runtime env replacement did not run (Vite env vars are build-time by default)
- **Solutions**:
  - Ensure `services/frontend/.env.production` contains placeholders for the variables you want to replace (this repo includes `VITE_BOT_NAME`, `VITE_UI_*`, etc.)
  - Ensure the container runs `env.sh` after copying the built files into `/usr/share/nginx/html`
  - Verify the variable is set in the container environment (Kubernetes `ConfigMap`/`Secret`, Docker `-e`, etc.)

### Logo Not Loading / Wrong for Theme

- **Issue**: Logo doesn't appear or shows broken image
- **Cause**: Incorrect path or missing asset
- **Solutions**:
  - Verify files exist in `public/assets/` directory
  - Check `VITE_UI_LOGO_PATH_LIGHT` / `VITE_UI_LOGO_PATH_DARK` (or `VITE_UI_LOGO_PATH` fallback)
  - Ensure path starts with `/assets/`
  - Check browser network tab for 404 errors

### Theme Not Persisting

- **Issue**: Theme resets to default on page refresh
- **Cause**: localStorage not being saved/loaded correctly
- **Solutions**:
  - Check browser localStorage for `app-theme` key
  - Verify theme value is in available options
  - Clear localStorage and try again

### Environment Variables Not Working in Production

- **Issue**: Customization works in development but not production
- **Cause**: Vite environment variables are build-time only
- **Solutions**:
  - Ensure the variables exist as placeholders at build time (see `services/frontend/.env.production`)
  - For Docker: Ensure `env.sh` script runs after copying files
  - For Kubernetes: Use ConfigMap/Secret with proper mounting
  - Verify environment variables are set in container

## Example Configurations

### Corporate Deployment

```bash
VITE_BOT_NAME="Corporate Knowledge Assistant"
VITE_UI_LOGO_PATH_LIGHT="/assets/corporate-logo-light.svg"
VITE_UI_LOGO_PATH_DARK="/assets/corporate-logo-dark.svg"
# Optional common fallback
# VITE_UI_LOGO_PATH="/assets/corporate-logo.svg"
VITE_UI_THEME_DEFAULT="light"
VITE_UI_THEME_OPTIONS="light,dark"
```

### Development Environment

```bash
VITE_BOT_NAME="Dev Bot"
VITE_UI_LOGO_PATH_LIGHT="/assets/dev-logo-light.png"
VITE_UI_LOGO_PATH_DARK="/assets/dev-logo-dark.png"
VITE_UI_THEME_DEFAULT="dark"
VITE_UI_THEME_OPTIONS="light,dark"
```

### Minimal Configuration

```bash
VITE_BOT_NAME="Assistant"
VITE_UI_THEME_DEFAULT="light"
VITE_UI_THEME_OPTIONS="light"
```

This customization system provides flexible branding options while maintaining a clean, maintainable codebase.
