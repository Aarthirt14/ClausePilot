# Testing Instructions for UI/UX Upgrade

## Quick Start

1. **Start Flask Server:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   python app.py
   ```

2. **Open Browser:**
   Navigate to `http://localhost:5000`

## Test Checklist

### Upload Page (`/`)
- [ ] Page loads with sidebar visible (desktop) or hidden (mobile)
- [ ] Hero section displays with ClausePilot icon
- [ ] Drag and drop zone is visible
- [ ] Clicking "Browse Files" opens file picker
- [ ] Drag a PDF over the zone → border turns blue
- [ ] Drop a PDF → file preview shows with name and size
- [ ] Click trash icon → file is removed and zone resets
- [ ] "Analyze Contract" button is disabled until file is selected
- [ ] Submit form → redirects to results page

### Dark Mode
- [ ] Click theme toggle in sidebar footer
- [ ] Background turns dark, text turns light
- [ ] Refresh page → theme persists
- [ ] Toggle back to light mode

### Sidebar (Mobile)
- [ ] Resize browser to < 992px width
- [ ] Sidebar slides off-screen
- [ ] Click hamburger menu (top left) → sidebar slides in
- [ ] Click X button → sidebar closes
- [ ] Click outside sidebar → sidebar closes

### Results Page (`/result/<filename>`)
- [ ] Overall risk score card displays with gradient background
- [ ] 4 stat cards show counts and percentages
- [ ] Executive summary lists bullet points
- [ ] Risk impact weights table shows all 5 categories
- [ ] 3 charts render correctly (pie, bar, histogram)
- [ ] Filter section has 4 controls (search, risk, severity, sort)
- [ ] Type in search → clauses are filtered in real-time
- [ ] Select risk filter → only matching clauses show
- [ ] Select severity filter → only matching clauses show
- [ ] Change sort order → clauses reorder
- [ ] Click clause accordion → expands to show full text
- [ ] Hover over badges → tooltips appear
- [ ] Click "Generate Explanation" → SHAP data loads and highlights words
- [ ] Click breadcrumb "Home" → returns to upload page

### Evaluation Page (`/evaluation`)
- [ ] Model comparison card shows BERT and Baseline F1 scores
- [ ] Metadata card shows generation timestamp
- [ ] Per-model metric cards display for BERT and Baseline
- [ ] Per-class tables show precision/recall/F1 for each label
- [ ] Confusion matrix image displays
- [ ] Class distribution image displays
- [ ] Reliability diagram image displays

### Responsive Design
Test on different screen sizes:
- [ ] Desktop (> 1200px): Full layout with sidebar
- [ ] Tablet (768px - 992px): Condensed layout, hamburger menu
- [ ] Mobile (< 768px): Single column, stacked cards

## Common Issues & Fixes

### Issue: Sidebar not showing
**Fix:** Ensure `base.html` is in templates folder and Flask template inheritance is working

### Issue: Charts not rendering
**Fix:** Check browser console for Chart.js errors. Verify CDN link is accessible.

### Issue: Dark mode not persisting
**Fix:** Check browser localStorage is enabled. Clear cache and test again.

### Issue: Upload drag-drop not working
**Fix:** Ensure `script.js` is loaded. Check browser console for JavaScript errors.

### Issue: SHAP button does nothing
**Fix:** Verify `/explain` Flask route exists and returns JSON. Check network tab in dev tools.

## Browser Console Checks

Open Developer Tools (F12) and check:
1. **Console tab**: No JavaScript errors
2. **Network tab**: All assets (CSS, JS, fonts) load with 200 status
3. **Elements tab**: Inspect sidebar, verify class names match CSS

## Performance Test

1. Upload a large contract (50+ clauses)
2. Check page load time (should be < 2 seconds)
3. Test filter responsiveness (should be instant)
4. Test chart rendering (should complete in < 500ms)

## Accessibility Test

1. Tab through page with keyboard
2. Ensure all interactive elements are focusable
3. Test screen reader compatibility (optional)
4. Verify color contrast ratios (use Chrome DevTools Lighthouse)

## Final Validation

Run Flask app and navigate through the complete workflow:
1. Upload → Results → Evaluation → Home
2. Try all features at least once
3. Test on mobile device (actual phone or Chrome DevTools device emulation)
4. Verify dark mode works on all pages

## Success Criteria

- ✅ All pages load without errors
- ✅ Sidebar navigation works
- ✅ Dark mode toggle works
- ✅ Drag-drop upload works
- ✅ Charts render correctly
- ✅ Filters and search work in real-time
- ✅ SHAP explanations load
- ✅ Responsive on mobile, tablet, desktop
- ✅ No JavaScript console errors
- ✅ All Flask template variables render correctly
