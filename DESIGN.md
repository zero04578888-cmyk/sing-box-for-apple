---
name: NEBULA
description: A calm, connection-first dark interface for the sing-box iOS client.
colors:
  primary: "#7DB3FF"
  secondary: "#B8A1FF"
  neutral-bg: "#060B16"
  neutral-surface: "#0E1525"
  neutral-raised: "#161E32"
typography:
  system:
    fontFamily: "SF Pro, iOS system font"
    fontWeight: 400
  title:
    fontFamily: "SF Pro, iOS system font"
    fontWeight: 700
  measurement:
    fontFamily: "SF Pro, iOS system font, monospaced digits"
    fontWeight: 400
rounded:
  node: "12pt"
  surface: "16pt"
spacing:
  compact: "8pt"
  regular: "16pt"
  spacious: "24pt"
components:
  surface:
    backgroundColor: "{colors.neutral-surface}"
    rounded: "{rounded.surface}"
    padding: "16pt"
---

# Design System: NEBULA

## Overview

**Creative North Star: “One Clear Connection.”**

NEBULA carries the user's specified navy-black, blue-violet world into the native iOS client. Its signature is the quiet gradient around the primary power control; node selection and directional traffic use the same restrained blue and violet accents. The existing iOS navigation, SF Symbols, SwiftUI controls, and system type remain the foundation.

The dashboard places the existing connection action first and leaves profile controls and configurable service cards in their existing roles. A separate Statistics tab presents current service telemetry. Node groups keep their existing selection, testing, and expansion actions. Color and motion describe UI state; neither is evidence that the VPN tunnel is healthy.

**Key Characteristics:**
- Dark navy background and layered, solid surfaces.
- Blue and violet accents reserved for the primary action, selected nodes, and directional traffic.
- Native iOS type, navigation, and VoiceOver actions.
- Live counters shown as reported by the current service.

## Colors

The palette moves from nearly black navy surfaces to clear blue and violet signals; system colors remain responsible for adaptable text.

### Primary
- **Nebula Blue** (#7DB3FF): The connection ring, interactive tint, selected node, and download chart.

### Secondary
- **Nebula Violet** (#B8A1FF): The opposite end of the connection gradient and the upload chart. It pairs with blue to distinguish direction.

### Neutral
- **Night Ground** (#060B16): The iOS screen background.
- **Deep Surface** (#0E1525): Dashboard cards.
- **Raised Navy** (#161E32): The selected node's inset surface and the connection control's inner disc.
- Surface outlines use white at 14% opacity in standard contrast and strengthen to 45% in increased contrast. Use the semantic `.primary`, `.secondary`, and `.foreground` colors for text.

**The Signal Color Rule.** Apply an accent to a real action, selection, or data direction; do not use the gradient as a text fill or as a substitute for state.

## Typography

**Display Font:** SF Pro, supplied by iOS.
**Body Font:** SF Pro, supplied by iOS.
**Label/Mono Font:** SF Pro with monospaced digits for measurements.

**Character:** System typography keeps the screens familiar, legible, and responsive to the user's text settings. The implementation uses semantic SwiftUI text styles instead of a fixed display scale.

### Hierarchy
- **Display** (system weight, Dynamic Type `largeTitle`): The scalable symbol inside the connection control.
- **Headline** (semibold, Dynamic Type `headline`): Connection status and card headings.
- **Title** (bold, Dynamic Type `title2`): The app identity and statistics destination heading.
- **Body** (system weight, Dynamic Type `body`): Explanations and primary reading text.
- **Label** (system weight, Dynamic Type `caption` and `footnote`): Secondary context and unit labels.

**The System Type Rule.** Use semantic iOS text styles and monospaced digits only where a value changes; allow users' Dynamic Type settings to change the layout.

## Layout

Keep the dashboard's native navigation bar and five bottom tabs. The dashboard vertically presents the connection surface before the existing configurable card grid; preserve profile management, card configuration, and their native sheets. The Statistics page uses a centered content column capped at 760 points with 20 points of outer padding; it presents rate charts before service-health cards. Node groups remain a vertically scrolling list of expanded and collapsed groups, with selectable outbound items arranged in an adaptive grid.

Use the observed 8-point close spacing, 16-point regular spacing, and 24-point section spacing where implemented. At iOS accessibility text sizes, paired dashboard and statistics cards become a single column, and adaptive node grids become one column. Keep controls inside native safe areas. Size primary actions and profile/group controls to at least 44 points where specified.

At accessibility text sizes, use one column; keep every control visible and let the native scroll view carry longer content.

## Elevation & Depth

Use tonal surfaces with a fine, one-point outline. The dashboard's shared card surface does not use a shadow. Increased Contrast strengthens the outline. Avoid decorative blur and layered halos.

**The Surface Separation Rule.** Separate cards with a difference in fill and a subtle outline, not a shadow.

## Shapes

Use continuous 16-point corners on common surfaces and 12-point corners on selected outbound items and the profile selector. The power action is circular, with a gradient outline and a raised navy inner circle. Interactive accents and outlines do not replace semantic selection or status.

## Components

### Buttons
- **Primary connection action:** A 144-point circular power affordance inside the shared label; blue-violet outline, raised inner disc, and a Dynamic Type `headline` Start/Stop label. Its action calls the existing `StartStopButton`; keep its profile validation, VPN operation, and error alert.
- **Focus and press:** Use the system button interaction. Do not fake a new tunnel state from animation or the initiating tap.
- **Compact actions:** Use the native Groups and Connections links with 44-point minimum height.

### Cards / Containers
- **Corner Style:** Continuous, 16 points.
- **Background:** Deep Surface with a one-point semantic outline.
- **Shadow Strategy:** None.
- **Internal Padding:** 16 points for the shared dashboard card; 20 points around the statistics content.

### Navigation
- Use the platform `TabView` and `NavigationStack` behavior, with the existing Dashboard, Logs, Tools, and Settings destinations plus Statistics on iOS. Retain edge-swipe back and standard sheet interactions.

### Selected outbound item
- An item keeps its existing native button and group-selection action. The selected state uses a blue outline, Nebula Blue at 12% fill opacity, and VoiceOver's selected trait/value; unselected items use Raised Navy. The token schema cannot express an accent color at a specific opacity, so no selected-fill component token is defined. Keep URL testing in its existing context menu.

### Traffic measurements
- The existing upload and download cards display a rate, the current service total, and the 30-point rate history supplied by `CommandClient`. Violet marks upload; blue marks download. Hide the chart and prior rate while disconnected. These totals have no daily or monthly window.

### Status
- Treat each `NEVPNStatus` separately: show Connected only for `.connected`; show connecting, reconnecting, and disconnecting as their own transient states. A connected label is interface status evidence, not real-device VPN validation.

## Do's and Don'ts

### Do:
- **Do** reuse the existing `ExtensionProfile` start/stop operation and its error handling.
- **Do** retain native tabs, navigation gestures, system fonts, SF Symbols, and sheet behavior.
- **Do** honor increased-contrast outlines, Reduce Motion, Dynamic Type, safe areas, and VoiceOver selection.
- **Do** expose totals and short-lived rates as reported by the current local or remote service.

### Don't:
- **Don't** infer a connected tunnel from the start button press or an in-progress `NEVPNStatus`.
- **Don't** label service totals as daily, monthly, or historical accounting.
- **Don't** display retained rate samples as current data after disconnection.
- **Don't** make macOS or tvOS inherit the iOS-only NEBULA system automatically.
