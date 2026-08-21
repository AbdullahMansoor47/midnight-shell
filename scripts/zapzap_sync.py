import json
import os

SCHEME_PATH = os.path.expanduser("~/.local/state/caelestia/scheme.json")
CSS_OUT_PATH = os.path.expanduser("~/.local/share/ZapZap/customizations/global/css/caelestia.css")
JS_OUT_PATH = os.path.expanduser("~/.local/share/ZapZap/customizations/global/js/caelestia.js")

def update():
    if not os.path.exists(SCHEME_PATH):
        return
    with open(SCHEME_PATH, "r") as f:
        data = json.load(f)
    
    colors = data.get("colours", {})
    
    bg_hex = colors.get('background', '0b141a')
    surface_hex = colors.get('surface', '111b21')
    surface_container_hex = colors.get('surfaceContainer', '202c33')
    primary_container_hex = colors.get('primaryContainer', '005c4b')
    surface_variant_hex = colors.get('surfaceVariant', '202c33')
    
    # Base colors
    bg = f"#{bg_hex}"
    surface = f"#{surface_hex}"
    surface_container = f"#{surface_container_hex}"
    primary = f"#{colors.get('primary', '00a884')}"
    primary_container = f"#{primary_container_hex}"
    on_primary_container = f"#{colors.get('onPrimaryContainer', 'e9edef')}"
    surface_variant = f"#{surface_variant_hex}"
    on_surface_variant = f"#{colors.get('onSurfaceVariant', '8696a0')}"
    on_surface = f"#{colors.get('onSurface', 'e9edef')}"

    # Translucent variants for glassmorphism
    # bg: 60% opacity (approx 99 in hex)
    bg_trans = f"#{bg_hex}aa" 
    # surface: 75% opacity (approx bf in hex)
    surface_trans = f"#{surface_hex}c0"
    
    css = f"""
/* Generated Caelestia Theme for ZapZap */
:root, .dark, body.dark, [data-theme="dark"], html[dir="ltr"] .dark {{
    /* Caelestia Variables for JS injection */
    --c-primary-container: {primary_container} !important;
    --c-surface-variant: {surface_variant} !important;
    --c-on-primary-container: {on_primary_container} !important;
    --c-on-surface: {on_surface} !important;

    /* General Backgrounds with Transparency */
    --background-default: {surface_trans} !important;
    --background-default-hover: {surface_container} !important;
    
    /* Headers & Panels */
    --panel-header-background: transparent !important;
    --panel-background: transparent !important;
    --drawer-background: {surface_trans} !important;
    
    /* Chat Area */
    --chat-background: {bg_trans} !important;
    --conversation-panel-background: {bg_trans} !important;
    
    /* Inputs */
    --compose-input-background: {surface_container} !important;
    --search-input-background: {surface_container} !important;
}}

/* App Wrapper Transparency */
body, #app, .app-wrapper-web, #main, #pane-side, #side, header {{
    background-color: transparent !important;
    background: transparent !important;
}}

/* We manually set the main blocks to our translucent colors so they stack properly */
#app {{
    background-color: {bg_trans} !important;
}}
#side, #pane-side {{
    background-color: {surface_trans} !important;
}}

/* Disable WhatsApp Doodle Background */
[data-asset-chat-background-dark="true"], 
[data-asset-chat-background="true"] {{
    background-color: transparent !important;
    background-image: none !important;
}}

/* Message Text Fixes */
.caelestia-msg-out {{
    background-color: var(--c-primary-container) !important;
}}
.caelestia-msg-out span, .caelestia-msg-out div {{
    color: var(--c-on-primary-container) !important;
}}

.caelestia-msg-in {{
    background-color: var(--c-surface-variant) !important;
}}
.caelestia-msg-in span, .caelestia-msg-in div {{
    color: var(--c-on-surface) !important;
}}
"""

    js = """
// Generated Caelestia JS script for ZapZap
// Uses Computed Style mapping to flawlessly find and theme bubbles!
(function() {
    // Default WhatsApp Web dark mode bubble colors (to hunt for)
    const WA_SENT_COLOR = "rgb(0, 92, 75)";
    const WA_RECV_COLOR = "rgb(32, 44, 51)";

    function themeBubbles() {
        try {
            // Find all message rows
            const rows = document.querySelectorAll('div[data-id]');
            
            rows.forEach(row => {
                // Skip rows we already processed to save CPU
                if (row.hasAttribute('data-caelestia-themed')) return;
                
                let foundBubble = false;
                
                // Inspect all divs inside this message row
                const divs = row.querySelectorAll('div');
                for (let i = 0; i < divs.length; i++) {
                    const div = divs[i];
                    // getComputedStyle is slow, but we only do it once per message!
                    const bg = window.getComputedStyle(div).backgroundColor;
                    
                    if (bg === WA_SENT_COLOR) {
                        div.classList.add('caelestia-msg-out');
                        foundBubble = true;
                    } else if (bg === WA_RECV_COLOR) {
                        div.classList.add('caelestia-msg-in');
                        foundBubble = true;
                    }
                }
                
                // Mark this row as processed even if we didn't find a bubble (e.g. system message)
                row.setAttribute('data-caelestia-themed', 'true');
            });
        } catch (e) {
            console.error("Caelestia Theme Error:", e);
        }
    }

    // Run every second to catch new messages scrolling into view
    setInterval(themeBubbles, 1000);
})();
"""

    os.makedirs(os.path.dirname(CSS_OUT_PATH), exist_ok=True)
    with open(CSS_OUT_PATH, "w") as f:
        f.write(css)

    os.makedirs(os.path.dirname(JS_OUT_PATH), exist_ok=True)
    with open(JS_OUT_PATH, "w") as f:
        f.write(js)

update()
