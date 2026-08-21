import json
import os
import time

SCHEME_PATH = os.path.expanduser("~/.local/state/caelestia/scheme.json")
# We will generate BOTH css and js just in case
CSS_OUT_PATH = os.path.expanduser("~/.local/share/ZapZap/customizations/global/css/caelestia.css")
JS_OUT_PATH = os.path.expanduser("~/.local/share/ZapZap/customizations/global/js/caelestia.js")

def update():
    if not os.path.exists(SCHEME_PATH):
        return
    with open(SCHEME_PATH, "r") as f:
        data = json.load(f)
    
    colors = data.get("colours", {})
    
    bg = f"#{colors.get('background', '0b141a')}"
    surface = f"#{colors.get('surface', '111b21')}"
    surface_container = f"#{colors.get('surfaceContainer', '202c33')}"
    
    primary = f"#{colors.get('primary', '00a884')}"
    on_primary = f"#{colors.get('onPrimary', 'ffffff')}"
    
    secondary = f"#{colors.get('secondary', '202c33')}"
    on_secondary = f"#{colors.get('onSecondary', 'ffffff')}"
    
    tertiary = f"#{colors.get('tertiary', '202c33')}"
    on_tertiary = f"#{colors.get('onTertiary', 'ffffff')}"

    # Generate CSS with CSS variables and data attributes
    css = f"""
/* Generated Caelestia Theme for ZapZap */
:root {{
    --c-bg: {bg} !important;
    --c-surface: {surface} !important;
    --c-primary: {primary} !important;
    --c-on-primary: {on_primary} !important;
    --c-secondary: {secondary} !important;
    --c-on-secondary: {on_secondary} !important;
    --c-tertiary: {tertiary} !important;
    --c-on-tertiary: {on_tertiary} !important;
}}

[data-caelestia="chat-bg"] {{
    background-color: var(--c-bg) !important;
    background-image: none !important;
}}

[data-caelestia="sidebar"] {{
    background-color: var(--c-primary) !important;
}}

/* Target the text in the sidebar to ensure readability on primary */
[data-caelestia="sidebar"] span, [data-caelestia="sidebar"] div {{
    color: var(--c-on-primary) !important;
}}

[data-caelestia="bubble-out"] {{
    background-color: var(--c-primary) !important;
}}
[data-caelestia="bubble-out"] span, [data-caelestia="bubble-out"] div {{
    color: var(--c-on-primary) !important;
}}

[data-caelestia="bubble-in"] {{
    background-color: var(--c-secondary) !important;
}}
[data-caelestia="bubble-in"] span, [data-caelestia="bubble-in"] div {{
    color: var(--c-on-secondary) !important;
}}
"""
    
    js = """
// Generated Caelestia JS script for ZapZap
(function() {
    function findBubble(row) {
        // Find the deepest div that has a background color or border-radius
        // A simple heuristic: bubbles usually have multiple classes and are deep in the tree.
        // Actually, the bubble is typically the first div inside the row that contains the text.
        // Let's just find the div with the class that starts with 'copyable-text' and get its parent, 
        // or just apply it to the first child of the first child.
        try {
            return row.children[0].children[0];
        } catch(e) {
            return row;
        }
    }

    function applyTheme() {
        // Chat background
        document.querySelectorAll('[data-asset-chat-background-dark]').forEach(el => {
            el.setAttribute('data-caelestia', 'chat-bg');
        });

        // Sidebar (Chat List Panel)
        const chatList = document.querySelector('[aria-label="Chat list"]');
        if (chatList) {
            // Find the container that represents the whole left sidebar
            // Usually it's a few levels up, sibling to the main chat pane
            let p = chatList;
            for(let i=0; i<4; i++) {
                if (p && p.parentElement) p = p.parentElement;
            }
            if (p) {
                p.setAttribute('data-caelestia', 'sidebar');
            }
        }

        // Outgoing Bubbles (Sent)
        document.querySelectorAll('div[data-id^="true_"]').forEach(row => {
            const bubble = findBubble(row);
            if (bubble) bubble.setAttribute('data-caelestia', 'bubble-out');
        });

        // Incoming Bubbles (Received)
        document.querySelectorAll('div[data-id^="false_"]').forEach(row => {
            const bubble = findBubble(row);
            if (bubble) bubble.setAttribute('data-caelestia', 'bubble-in');
        });
    }

    // Run periodically to catch new messages and DOM changes (React dynamically loads content)
    setInterval(applyTheme, 500);
})();
"""

    os.makedirs(os.path.dirname(CSS_OUT_PATH), exist_ok=True)
    with open(CSS_OUT_PATH, "w") as f:
        f.write(css)

    os.makedirs(os.path.dirname(JS_OUT_PATH), exist_ok=True)
    with open(JS_OUT_PATH, "w") as f:
        f.write(js)

update()
