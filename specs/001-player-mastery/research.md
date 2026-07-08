# Research Notes: Player Mastery Experience

This document details the research, technical decisions, and rationale for the implementation of the Player Mastery progression component.

## 1. Dynamic Potion Icons & Fallback

### Decisions
* **API URL**: Potion icons will be loaded directly from the official Albion Render Service: `https://render.albiononline.com/v1/item/{potion_item_id}.png`.
* **Rendering Method**: Rendered via Streamlit using HTML `<img ...>` within `st.markdown(..., unsafe_allow_html=True)` to leverage native browser-level loading and error handling.
* **Fallback Implementation**: Using the HTML `onerror` attribute to replace the `src` with a lightweight, offline-capable, inline SVG base64 placeholder when the image fails to load.
  * *Placeholder SVG Code*: `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"><rect width="48" height="48" fill="%231e293b" rx="8" stroke="%23334155"/><text x="50%25" y="65%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="24" fill="%2394a3b8">🧪</text></svg>`
  * *Rationale*: Avoids writing binary images to local disk, doesn't require runtime HTTP requests in Python (which would violate "no additional API calls"), and is 100% offline-capable.

### Alternatives Considered
* **Local asset folder**: Rejected because it violates the NFR "Images must never be stored locally."
* **Requests checking**: Making HTTP `GET` requests in Python to check URL validity before rendering. Rejected because it violates NFR "Do not introduce additional API calls" and adds latency to app loading.

---

## 2. Lightweight Local Persistence

### Decisions
* **Mechanism**: A local JSON file located at `data/player-mastery.json`.
* **JSON Structure**:
  ```json
  {
    "T4_POTION_HEAL": 15,
    "T6_POTION_HEAL": 0,
    ...
  }
  ```
* **Integration**: On application startup, the JSON file is loaded into memory. If the file does not exist or fails to parse, it defaults all mastery levels to `0` and silently writes a new default file.
* **Saving**: Whenever a user updates a mastery level in the UI, the updated `PlayerMastery` state is written back to `data/player-mastery.json` and synchronized with `st.session_state`.

---

## 3. UI Component Layout & Interaction

### Decisions
* **Layout**: A horizontal flex row container styled with custom CSS via `st.markdown` to show potion cards. Since Streamlit columns can wrap or cause spacing issues with many elements, a custom HTML/CSS grid or flexbox layout inside `st.container` provides a premium, compact layout resembling Albion's UI.
* **Interaction**: Clicking a potion card opens an editor. Since Streamlit doesn't support click events on raw HTML divs natively without custom components, we will implement a clean selectbox and slider/number input in an expander or dialog, or a clear control block below the mastery bar:
  * *Control design*: A `st.expander("⚙️ Gerenciar Especializações (Mastery)")` positioned right under the bar. Inside, a selectbox lists all potions, and a slider adjusts the mastery level from 0 to 100, updating the JSON file immediately on change. This fits Streamlit's native input architecture perfectly and is highly reliable.
* **Visual Progress Feedback**: Custom CSS progress bars or rings styled with custom HTML/CSS.
