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
    
    # Base colors (Solid, no transparency to avoid QtWebEngine rendering bugs)
    bg = f"#{bg_hex}"
    surface = f"#{surface_hex}"
    surface_container = f"#{surface_container_hex}"
    primary = f"#{colors.get('primary', '00a884')}"
    primary_container = f"#{primary_container_hex}"
    on_primary_container = f"#{colors.get('onPrimaryContainer', 'e9edef')}"
    surface_variant = f"#{surface_variant_hex}"
    on_surface_variant = f"#{colors.get('onSurfaceVariant', '8696a0')}"
    on_surface = f"#{colors.get('onSurface', 'e9edef')}"
    
    css = f"""
/* Generated Caelestia Theme for ZapZap */
:root, .dark, body.dark, [data-theme="dark"], html[dir="ltr"] .dark {{
    /* Caelestia Variables */
    --c-bg: {bg} !important;
    --c-surface: {surface} !important;
    --c-surface-container: {surface_container} !important;
    --c-primary-container: {primary_container} !important;
    --c-on-primary-container: {on_primary_container} !important;
    --c-surface-variant: {surface_variant} !important;
    --c-on-surface: {on_surface} !important;
    --c-on-surface-variant: {on_surface_variant} !important;

    /* Native Variables (Fallback) */
    --background-default: var(--c-surface) !important;
    --background-default-hover: var(--c-surface-container) !important;
    --panel-header-background: var(--c-surface-container) !important;
    --panel-background: var(--c-surface) !important;
    --chat-background: var(--c-bg) !important;
    --conversation-panel-background: var(--c-bg) !important;
    --compose-input-background: var(--c-surface-container) !important;
    --search-input-background: var(--c-surface-container) !important;
}}

/* App Backgrounds */
body, #app, .app-wrapper-web, #main {{
    background-color: var(--c-bg) !important;
}}

/* Sidebar Background */
#side, #pane-side {{
    background-color: var(--c-surface) !important;
}}

/* Chat List Panel Items (The panels themselves) */
.caelestia-chat-row {{
    background-color: var(--c-surface) !important;
}}
.caelestia-chat-row:hover {{
    background-color: var(--c-surface-container) !important;
}}
.caelestia-chat-row * {{
    border-color: transparent !important;
}}

/* Headers */
header {{
    background-color: var(--c-surface-container) !important;
}}

/* Disable WhatsApp Doodle */
[data-asset-chat-background-dark="true"], 
[data-asset-chat-background="true"] {{
    background-color: var(--c-bg) !important;
    background-image: none !important;
}}

/* Dynamic Message Bubbles injected by JS */
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
// Uses structural DOM walking to perfectly theme WhatsApp Web!
(function() {
    function themeElements() {
        try {
            // 1. Theme Message Bubbles
            const rows = document.querySelectorAll('div[data-id]');
            rows.forEach(row => {
                if (row.dataset.caelestiaThemed) return;
                
                const isSent = row.getAttribute('data-id').startsWith('true_');
                const colorClass = isSent ? 'caelestia-msg-out' : 'caelestia-msg-in';
                
                // Find the text node inside the message
                const textNodes = row.querySelectorAll('[data-preplain-text], .copyable-text');
                if (textNodes.length > 0) {
                    // Start from the text node and walk UP the DOM tree to find the painted bubble wrapper
                    let bubble = textNodes[0];
                    while (bubble && bubble !== row) {
                        const style = window.getComputedStyle(bubble);
                        const bg = style.backgroundColor;
                        
                        // If it has a solid background color, it's the bubble container!
                        if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
                            bubble.classList.add(colorClass);
                            bubble.style.setProperty('background-image', 'none', 'important');
                            
                            // Color the little message tail arrow if it exists (usually an SVG or pseudo-element sibling)
                            const svgs = bubble.parentElement.querySelectorAll('svg');
                            svgs.forEach(svg => {
                                // Sometimes the arrow is a span with an svg
                                svg.style.color = isSent ? 'var(--c-primary-container)' : 'var(--c-surface-variant)';
                            });
                            
                            break;
                        }
                        bubble = bubble.parentElement;
                    }
                } else {
                    // Fallback for image-only/sticker messages without text
                    const divs = row.querySelectorAll('div');
                    for (let i = 0; i < divs.length; i++) {
                        const bg = window.getComputedStyle(divs[i]).backgroundColor;
                        if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
                            divs[i].classList.add(colorClass);
                            break;
                        }
                    }
                }
                row.dataset.caelestiaThemed = 'true';
            });
            
            // 2. Theme Sidebar Chat Rows
            const chatList = document.querySelector('[aria-label="Chat list"]');
            if (chatList) {
                const chatRows = chatList.querySelectorAll('[role="listitem"]');
                chatRows.forEach(item => {
                    // Find the deepest inner div that paints the background
                    let innerBg = item.querySelector('div > div > div');
                    if (innerBg) {
                        innerBg.classList.add('caelestia-chat-row');
                    } else {
                        item.classList.add('caelestia-chat-row');
                    }
                });
            }
            
        } catch (e) {
            console.error("Caelestia Theme Error:", e);
        }
    }

    // Run periodically to catch new DOM elements
    setInterval(themeElements, 1000);
})();
"""

    os.makedirs(os.path.dirname(CSS_OUT_PATH), exist_ok=True)
    with open(CSS_OUT_PATH, "w") as f:
        f.write(css)

    os.makedirs(os.path.dirname(JS_OUT_PATH), exist_ok=True)
    with open(JS_OUT_PATH, "w") as f:
        f.write(js)

update()
