# UI Customization Guide

This guide explains how to customize the RAG Template frontend applications, including bot branding, theming, and logo configuration.

## Overview

The RAG Template frontend supports several customization options:
- **Bot Name**: Customize the AI assistant's name in chat messages
- **Logo/Branding**: Replace the default logo with your organization's branding
- **Theme System**: Switch between light and dark modes with user preference persistence

## Configuration Options

### Environment Variables

All customization is done through environment variables that can be set at build time or runtime:

| Variable | Description | Default Value | Example |
|----------|-------------|---------------|---------|
| `VITE_BOT_NAME` | The AI assistant's display name | "Knowledge Agent" | "DocBot" |
| `VITE_UI_LOGO_PATH` | Common path to the main navigation logo (fallback for both light/dark) | "/assets/navigation-logo.svg" | "/assets/my-logo.png" |
| `VITE_UI_LOGO_PATH_LIGHT` | Path to logo used in light mode (falls back to `VITE_UI_LOGO_PATH`) | — | "/assets/logo-light.svg" |
| `VITE_UI_LOGO_PATH_DARK` | Path to logo used in dark mode (falls back to `VITE_UI_LOGO_PATH`) | — | "/assets/logo-dark.svg" |
| `VITE_UI_THEME_DEFAULT` | Default theme when user first visits | "light" | "dark" |
| `VITE_UI_THEME_OPTIONS` | Available theme options (comma-separated) | "light,dark" | "light,dark,auto" |

### Bot Name Customization

The bot name appears in the initial welcome message in the chat interface.

**Default Message:**
```text
Hi 👋, I'm your AI Assistant Knowledge Agent, here to support you with any questions regarding the provided documents!
```

**Setting Custom Bot Name:**

1. **Development Environment:**
   ```bash
   # In your .env file
   VITE_BOT_NAME=DocBot
   ```

2. **Docker/Production:**
   ```bash
   # Environment variable
   export VITE_BOT_NAME="Your Custom Bot Name"
   ```

3. **Kubernetes/Helm:**
   ```yaml
   # In your values.yaml or deployment
   env:
     - name: VITE_BOT_NAME
       value: "Corporate Knowledge Assistant"
   ```

### Logo Customization

The logo appears in the navigation header of both chat and admin applications. You can configure separate logos for light and dark themes.

**Setting Custom Logos:**

1. Place your logo files in the `frontend/apps/[app-name]/public/assets/` directory
2. Set the environment variables:
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

- Light: `VITE_UI_LOGO_PATH_LIGHT` → `VITE_UI_LOGO_PATH` → `/assets/navigation-logo.svg`
- Dark: `VITE_UI_LOGO_PATH_DARK` → `VITE_UI_LOGO_PATH` → `/assets/navigation-logo.svg`

**Examples:**
```bash
# Separate light/dark logos
VITE_UI_LOGO_PATH_LIGHT=/assets/company-logo-light.svg
VITE_UI_LOGO_PATH_DARK=/assets/company-logo-dark.svg

# Only a common logo
VITE_UI_LOGO_PATH=/assets/company-logo.svg
```

### Theme System

The application supports a flexible theme system with user preference persistence.

**Available Themes:**
- `light`: Light mode (default)
- `dark`: Dark mode

**Theme Configuration:**

1. **Set Default Theme:**
   ```bash
   # Users will see dark mode by default
   VITE_UI_THEME_DEFAULT=dark
   ```

2. **Configure Available Options:**
   ```bash
   # Only allow light mode (remove theme toggle)
   VITE_UI_THEME_OPTIONS=light

   # Support both themes (default)
   VITE_UI_THEME_OPTIONS=light,dark
   ```

**Theme Behavior:**
- Theme preference is saved in browser's localStorage
- Theme persists across browser sessions
- Theme toggle button appears only when multiple options are available
- Manual theme switching overrides the default setting

## Development Setup

### Local Development

1. **Create/modify `.env` file in frontend directory:**
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

2. **Start development server:**

   ```bash
   npm run chat:serve
   # or
   npm run admin:serve
   ```

### Docker Deployment

For Docker deployments, the frontend uses a special script (`env.sh`) to replace environment variables at runtime:

1. **Set environment variables in your container:**

   ```dockerfile
   ENV VITE_BOT_NAME="Production Assistant"
   ENV VITE_UI_LOGO_PATH_LIGHT="/assets/prod-logo-light.svg"
   ENV VITE_UI_LOGO_PATH_DARK="/assets/prod-logo-dark.svg"
   ENV VITE_UI_THEME_DEFAULT="light"
   ```

2. **The env.sh script automatically replaces variables** in built JS/CSS files when the container starts.

### Kubernetes/Helm Deployment

1. **Configure in your Helm values.yaml:**

   ```yaml
   frontend:
     env:
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

To add custom themes beyond light/dark:

1. **Update the settings configuration:**

   ```typescript
   // frontend/libs/shared/settings.ts
   const defaultSettings: AppSettings = {
     ui: {
       theme: {
         default: "light",
         options: ["light", "dark", "custom"], // Add your theme
       },
     },
   };
   ```

2. **Configure DaisyUI themes** in `tailwind.config.js`:

   ```javascript
   module.exports = {
     daisyui: {
       themes: [
         "light",
         "dark",
         {
           custom: {
             "primary": "#your-color",
             "secondary": "#your-color",
             // ... more theme colors
           }
         }
       ],
     },
   };
   ```

### Internationalization

Bot names and messages support internationalization:

1. **Modify translation files:**

   ```json
   // frontend/libs/i18n/chat/en.json
   {
     "chat": {
       "initialMessage": "Hi 👋, I'm your AI Assistant {bot_name}, here to help!"
     }
   }
   ```

2. **Add language-specific bot names:**

   ```json
   // frontend/libs/i18n/chat/de.json
   {
     "chat": {
       "initialMessage": "Hallo 👋, ich bin dein KI-Assistent {bot_name}, hier um zu helfen!"
     }
   }
   ```

## Troubleshooting

### Bot Name Not Updating

- **Issue**: Bot name shows as `{bot_name}` instead of actual name
- **Cause**: Vue computed property not accessed correctly
- **Solution**: Use `initialMessage.value` instead of `initialMessage` in the store

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
