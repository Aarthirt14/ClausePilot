# ClausePilot Design System Reference

## Color Palette

### Primary Colors
```css
--primary: #0d6efd        /* Bootstrap Blue - primary actions, links */
--primary-dark: #0a58ca   /* Darker blue for hover states */
```

### Semantic Colors
```css
--success: #22c55e        /* Green - low risk, success states */
--danger: #dc2626         /* Red - high risk, errors */
--warning: #ea580c        /* Orange - medium risk, warnings */
--info: #0ea5e9           /* Cyan - informational messages */
--secondary: #6c757d      /* Gray - secondary actions */
```

### Gray Scale (Light Mode)
```css
--gray-50:  #f9fafb       /* Lightest - backgrounds */
--gray-100: #f3f4f6       /* Light - card backgrounds */
--gray-200: #e5e7eb       /* Borders, dividers */
--gray-300: #d1d5db       /* Disabled states */
--gray-400: #9ca3af       /* Placeholders */
--gray-500: #6b7280       /* Secondary text */
--gray-600: #4b5563       /* Body text */
--gray-700: #374151       /* Dark text */
--gray-800: #1f2937       /* Headings */
--gray-900: #111827       /* Darkest - high emphasis */
```

### Risk Category Colors
```css
Liability Risk:      #dc2626 (Red)
Termination Risk:    #ea580c (Orange)
Data Privacy Risk:   #2563eb (Blue)
Payment Risk:        #a16207 (Yellow-brown)
Neutral:             #6b7280 (Gray)
```

### Severity Level Colors
```css
High:    #dc2626 (Red)
Medium:  #ea580c (Orange)
Low:     #22c55e (Green)
None:    #6b7280 (Gray)
```

## Typography

### Font Family
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Font Sizes
```css
Display:     3rem (48px)
Heading 1:   2.5rem (40px)
Heading 2:   2rem (32px)
Heading 3:   1.75rem (28px)
Heading 4:   1.5rem (24px)
Heading 5:   1.25rem (20px)
Heading 6:   1rem (16px)
Body:        0.95rem (15.2px)
Small:       0.875rem (14px)
Tiny:        0.75rem (12px)
```

### Font Weights
```css
Light:       300
Regular:     400
Medium:      500
Semibold:    600
Bold:        700
```

### Line Heights
```css
Tight:    1.2    /* Headings */
Normal:   1.5    /* Default */
Relaxed:  1.7    /* Body text, clauses */
```

## Spacing Scale

Bootstrap 5 spacing utilities (multiples of 8px):
```css
0: 0px
1: 0.25rem (4px)
2: 0.5rem (8px)
3: 1rem (16px)
4: 1.5rem (24px)
5: 3rem (48px)
```

Custom spacing:
```css
Card padding:    1.25rem - 2rem
Section gap:     2rem - 3rem
Element gap:     0.75rem - 1.5rem
```

## Border Radius
```css
--border-radius:     12px    /* Cards, buttons */
--border-radius-lg:  16px    /* Large cards, modals */

Small elements:      8px     /* Badges, tooltips */
Standard:            12px    /* Most UI elements */
Large:               16px    /* Feature cards */
Circle:              50%     /* Avatars, icons */
```

## Shadows
```css
--shadow-sm:  0 1px 2px rgba(0, 0, 0, 0.05)        /* Subtle lift */
--shadow:     0 4px 6px -1px rgba(0, 0, 0, 0.1)    /* Standard cards */
--shadow-lg:  0 10px 15px -3px rgba(0, 0, 0, 0.1)  /* Modals, popovers */
```

## Layout Dimensions
```css
--sidebar-width:    260px
--topbar-height:    64px
--card-max-width:   1200px
```

## Transitions
```css
--transition: all 0.2s ease-in-out

Hover effects:     0.2s
State changes:     0.3s
Sidebar toggle:    0.3s
Page transitions:  0.4s
```

## Breakpoints
```css
Mobile:     < 768px
Tablet:     768px - 992px
Desktop:    992px - 1200px
Large:      > 1200px
```

## Component Dimensions

### Buttons
```css
Small:   padding: 0.35rem 0.75rem; font-size: 0.875rem
Medium:  padding: 0.5rem 1rem; font-size: 1rem
Large:   padding: 0.75rem 1.5rem; font-size: 1.125rem
```

### Icons
```css
Small:   1.2rem (19px)
Medium:  1.5rem (24px)
Large:   2rem (32px)
XLarge:  2.5rem (40px)
```

### Cards
```css
Padding:       1.25rem - 2rem
Border:        1px solid #e5e7eb
Border radius: 12px - 16px
Background:    #ffffff
```

### Badges
```css
Padding:       0.35rem 0.75rem
Font size:     0.75rem
Border radius: 6px
Font weight:   600
```

## Z-Index Scale
```css
Dropdown:     1000
Sticky:       1020
Fixed:        1030
Sidebar:      1000
Modal:        1050
Tooltip:      1070
```

## Animation Keyframes

### Fade In
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

### Slide In (Sidebar)
```css
@keyframes slideIn {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}
```

### Spin (Loading)
```css
@keyframes spin {
  to { transform: rotate(360deg); }
}
```

## Icon Usage

Using Bootstrap Icons:
```html
<i class="bi bi-file-earmark-check"></i>  <!-- ClausePilot logo -->
<i class="bi bi-cloud-upload"></i>          <!-- Upload -->
<i class="bi bi-shield-check"></i>          <!-- Risk/Security -->
<i class="bi bi-graph-up-arrow"></i>        <!-- Analytics -->
<i class="bi bi-cpu"></i>                   <!-- AI/Model -->
<i class="bi bi-lightbulb"></i>             <!-- Explainability -->
<i class="bi bi-funnel"></i>                <!-- Filters -->
<i class="bi bi-search"></i>                <!-- Search -->
<i class="bi bi-download"></i>              <!-- Download -->
<i class="bi bi-list"></i>                  <!-- Menu -->
<i class="bi bi-x-lg"></i>                  <!-- Close -->
```

## CSS Class Naming Convention

### BEM-inspired
```css
.component              /* Block */
.component-element      /* Element */
.component--modifier    /* Modifier */

Examples:
.sidebar
.sidebar-link
.sidebar-link--active

.stat-card
.stat-icon
.stat-value
```

### Utility Classes
```css
.d-flex                 /* Display flex */
.gap-3                  /* Gap spacing */
.rounded-4              /* Border radius */
.shadow-sm              /* Box shadow */
.text-primary           /* Color */
.bg-primary-subtle      /* Background */
.fw-bold                /* Font weight */
.fs-4                   /* Font size */
```

## Accessibility

### Color Contrast Ratios
```
Body text (gray-700):     4.5:1 (AA)
Headings (gray-900):      7:1 (AAA)
Disabled text (gray-400): 3:1 (minimum)
```

### Focus States
```css
Outline: 2px solid var(--primary)
Offset: 2px
```

### ARIA Labels
```html
<button aria-label="Toggle dark mode">
<nav aria-label="Main navigation">
<div role="alert">
```

## Dark Mode Variables

Dark mode overrides (inverted grayscale):
```css
[data-bs-theme="dark"] {
  --gray-50:  #111827
  --gray-100: #1f2937
  --gray-200: #374151
  --gray-300: #4b5563
  --gray-400: #6b7280
  --gray-500: #9ca3af
  --gray-600: #d1d5db
  --gray-700: #e5e7eb
  --gray-800: #f3f4f6
  --gray-900: #f9fafb
}
```

## Usage Examples

### Primary Button
```html
<button class="btn btn-primary">
  <i class="bi bi-lightning-charge-fill me-2"></i>Analyze Contract
</button>
```

### Info Card
```html
<div class="card border-0 shadow-sm rounded-4">
  <div class="card-header bg-white border-0 pt-4 px-4">
    <h5 class="fw-bold">Title</h5>
  </div>
  <div class="card-body px-4">
    Content here
  </div>
</div>
```

### Stat Display
```html
<div class="stat-card-modern">
  <div class="stat-icon bg-primary-subtle text-primary">
    <i class="bi bi-file-text"></i>
  </div>
  <div>
    <div class="stat-label">Total Clauses</div>
    <div class="stat-value">42</div>
  </div>
</div>
```

### Badge
```html
<span class="badge text-bg-danger-subtle">High Risk</span>
<span class="badge text-bg-warning-subtle">Medium Risk</span>
<span class="badge text-bg-success-subtle">Low Risk</span>
```

This design system ensures consistency across the entire ClausePilot application and makes it easy to extend or modify the UI in the future.
