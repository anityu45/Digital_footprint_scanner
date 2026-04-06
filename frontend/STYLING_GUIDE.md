# UI Styling System for Nexus OSINT

## Overview

The styling system has been completely revamped to provide a modular, maintainable approach to CSS management. All styles are now centralized in a dedicated CSS file with a Python style management module for easy integration.

## File Structure

```
frontend/
├── app.py                 # Main app (updated to use style_manager)
├── style_manager.py       # Style management module (NEW)
├── styles.css             # Global CSS file (NEW)
├── api.py
├── pages/
│   ├── dashbord.py       # Dashboard (updated)
│   ├── new_scan.py       # New Scan page (updated)
│   ├── image_tools.py    # Image Tools page (updated)
```

## Using the Style Manager

### Basic Usage

In any Streamlit page, simply import and call the styling function:

```python
from style_manager import apply_custom_page_style

# Set page config
st.set_page_config(...)

# Apply styles
apply_custom_page_style("PageName")
```

### Available Functions

#### 1. `apply_styles(css_file_path="styles.css")`
Loads and applies the CSS file to your Streamlit app.

```python
from style_manager import apply_styles

apply_styles()  # Loads styles.css
apply_styles("custom.css")  # Loads custom.css
```

#### 2. `apply_custom_page_style(page_title)`
Applies both global and page-specific styling.

```python
# Apply Dashboard-specific styling
apply_custom_page_style("Dashboard")

# Apply Scan page-specific styling
apply_custom_page_style("Scan")
```

Supported page titles:
- "Dashboard"
- "Scan"
- "Login"
- "Forensics"

#### 3. `get_theme_colors()`
Returns a dictionary of theme colors for dynamic styling:

```python
colors = get_theme_colors()
primary_color = colors["primary_blue"]  # #4facfe
```

Available colors:
- `primary_blue`, `primary_cyan`, `primary_purple`, `primary_dark_purple`
- `accent_pink`, `accent_green`
- `bg_dark`, `bg_darker`
- `text_primary`, `text_secondary`

#### 4. `create_metric_card_html(label, value, delta, icon)`
Create styled metric cards:

```python
from style_manager import create_metric_card_html

card_html = create_metric_card_html(
    label="Total Scans",
    value="42",
    delta="↑ 5 from yesterday",
    icon="📊"
)
st.markdown(card_html, unsafe_allow_html=True)
```

#### 5. `create_alert_html(message, alert_type, icon)`
Create styled alert boxes:

```python
from style_manager import create_alert_html

alert = create_alert_html(
    message="Operation completed successfully!",
    alert_type="success",
    icon="✅"
)
st.markdown(alert, unsafe_allow_html=True)
```

Alert types: `"info"`, `"success"`, `"error"`, `"warning"`

## CSS File Structure

The `styles.css` file is organized into sections:

```css
/* Root Variables - Theme colors and spacing */
/* Global Typography - Font families and basic text styling */
/* Headers - H1-H6 styling */
/* Text Elements - Paragraphs, code, etc */
/* Input Fields - Text inputs, selects, etc */
/* Buttons - Button styling and hover effects */
/* Tabs - Tab navigation styling */
/* Containers & Cards - Box styling */
/* Alerts & Messages - Alert/message styling */
/* Dataframe & Tables - Table styling */
/* Metrics - Metric card styling */
/* Sidebar - Sidebar styling */
/* Markdown - Markdown element styling */
/* Spinners & Loading - Loading indicators */
/* Utility Classes - Reusable utility classes */
/* Responsive Design - Mobile breakpoints */
```

## Theme Colors

### Primary Colors
- **Primary Blue**: `#4facfe`
- **Primary Cyan**: `#00f2fe`
- **Primary Purple**: `#667eea`
- **Primary Dark Purple**: `#764ba2`

### Accent Colors
- **Accent Pink**: `#ff006e`
- **Accent Green**: `#06d6a0`

### Neutral Colors
- **Dark Background**: `#0f1419`
- **Darker Background**: `#0a0d13`
- **Text Primary**: `#f0f2f6`
- **Text Secondary**: `#b8bcc4`

## CSS Variables Reference

All colors and values are defined as CSS variables for easy customization:

```css
--primary-blue: #4facfe
--primary-cyan: #00f2fe
--shadow-md: 0 4px 12px rgba(118, 75, 162, 0.2)
--radius-md: 8px
--space-md: 1rem
--transition-normal: 0.3s ease
```

To customize, edit the `:root` section in `styles.css`.

## Customization Guide

### Adding New Colors
Edit the `:root` section in `styles.css`:

```css
:root {
    --custom-red: #e63946;
    --custom-orange: #f4a261;
}
```

### Adding Page-Specific Styles
Update the `apply_custom_page_style()` function in `style_manager.py`:

```python
elif page_title == "NewPage":
    st.markdown("""
    <style>
        .new-page-header {
            background: linear-gradient(...);
            /* Your custom styles */
        }
    </style>
    """, unsafe_allow_html=True)
```

### Creating Reusable Utility Classes
Add utility classes to the "UTILITY CLASSES" section in `styles.css`:

```css
.highlight-box {
    border: 2px solid var(--primary-blue);
    background: rgba(79, 172, 254, 0.1);
    padding: var(--space-lg);
    border-radius: var(--radius-md);
}
```

Then use in your pages:

```html
<div class="highlight-box">
    Important content here
</div>
```

## Advanced Usage

### Dynamic Styling with Python
Create module-specific styling functions:

```python
def create_dashboard_metrics():
    """Create styled metrics for dashboard"""
    colors = get_theme_colors()
    
    html = f"""
    <div style="border-left: 4px solid {colors['primary_blue']}; padding: 1rem;">
        Your content here
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
```

### Responsive Design
The CSS includes responsive breakpoints for mobile devices:

```css
@media (max-width: 768px) {
    /* Tablet and smaller screens */
}

@media (max-width: 480px) {
    /* Mobile phones */
}
```

## Best Practices

1. **Use CSS Variables**: Always use CSS variables for colors and sizing for consistency:
   ```css
   color: var(--primary-blue);  /* Good */
   color: #4facfe;              /* Avoid */
   ```

2. **Consistency**: Keep similar elements styled the same way

3. **Reuse Components**: Use the helper functions for common patterns (metrics, alerts, etc.)

4. **Mobile First**: Consider responsive design when adding new styles

5. **Dark Mode**: The theme is optimized for dark mode - test thoroughly if changing

## Troubleshooting

### Styles Not Applying
1. Ensure `style_manager.py` and `styles.css` are in the same directory as your page
2. Check that you've called `apply_custom_page_style()` after `st.set_page_config()`
3. Clear Streamlit cache: `streamlit cache clear`

### CSS Not Loading from File
- Verify the file path is correct relative to the frontend directory
- Check file permissions
- Restart the Streamlit server

### Conflicting Styles
- Streamlit's default styles may conflict with custom CSS
- Use `!important` flag sparingly for overrides
- Increase CSS specificity if needed

## Future Enhancements

Potential improvements to the styling system:

- [ ] Light mode theme support
- [ ] Customizable theme builder
- [ ] Animation library
- [ ] Component library (buttons, cards, etc.)
- [ ] Accessibility improvements
- [ ] Print-friendly styles

## Support

For issues or questions about the styling system:
1. Check this guide first
2. Review the source files: `styles.css` and `style_manager.py`
3. Check Streamlit's CSS documentation: https://docs.streamlit.io/develop/concepts/design/styling
