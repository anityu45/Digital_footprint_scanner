# Advanced UI Styling & Components Guide

## 📦 What's New

This guide covers the complete UI enhancement system including professional components library, advanced animations, and the new components showcase page.

## File Structure

```
frontend/
├── app.py                      # Main app (updated with theme toggle)
├── style_manager.py            # Enhanced with new features
├── styles.css                  # Enhanced with animations & components
├── components.py               # NEW - Components library
├── STYLING_GUIDE.md            # Original styling guide
├── api.py
├── pages/
│   ├── dashbord.py
│   ├── new_scan.py
│   ├── image_tools.py
│   ├── components_showcase.py  # NEW - Component showcase
```

---

## 🎨 Components Library

### Overview

The `components.py` module provides pre-built, professionally styled UI components. All components return HTML strings that can be rendered with `st.markdown()`.

### Component Types

#### 1. **Badges** - Status/Category Labels

```python
from components import create_badge, BadgeType

# Create different badge types
badge_primary = create_badge("Processing", BadgeType.PRIMARY, "🔄")
badge_success = create_badge("Complete", BadgeType.SUCCESS, "✅")
badge_warning = create_badge("Pending", BadgeType.WARNING, "⏳")
badge_danger = create_badge("Failed", BadgeType.DANGER, "❌")
badge_secondary = create_badge("Info", BadgeType.SECONDARY, "ℹ️")

st.markdown(badge_primary, unsafe_allow_html=True)
```

#### 2. **Pills** - Interactive Button-like Elements

```python
from components import create_pill_button

pill = create_pill_button("Filter Results", "🔍")
st.markdown(pill, unsafe_allow_html=True)
```

#### 3. **Tags Cloud** - Multiple Tags

```python
from components import create_tags_cloud

tags = ["Security", "OSINT", "Analysis", "Real-time", "Professional"]
cloud = create_tags_cloud(tags)
st.markdown(cloud, unsafe_allow_html=True)
```

#### 4. **Widgets** - Dashboard Cards

```python
from components import create_widget

widget = create_widget(
    title="Total Scans",
    content="<div style='font-size: 2rem; color: #4facfe; font-weight: 700;'>1,234</div>",
    icon="📊",
    footer_text="Last 30 days"
)
st.markdown(widget, unsafe_allow_html=True)
```

#### 5. **Status Indicators** - Animated Status Dots

```python
from components import create_status_indicator, StatusType

online = create_status_indicator(StatusType.ONLINE, "System Online")
pending = create_status_indicator(StatusType.PENDING, "Processing")
error = create_status_indicator(StatusType.ERROR, "Error")

st.markdown(online, unsafe_allow_html=True)
```

#### 6. **Progress Bars** - Visual Progress

```python
from components import create_progress_bar

progress = create_progress_bar(
    label="Scan Progress",
    value=75,
    max_value=100,
    show_percentage=True
)
st.markdown(progress, unsafe_allow_html=True)
```

#### 7. **Breadcrumbs** - Navigation Path

```python
from components import create_breadcrumb

breadcrumb_items = [
    {"label": "Dashboard", "url": "#"},
    {"label": "Scans", "url": "#"},
    {"label": "Current Scan", "url": "#"},
]
breadcrumb = create_breadcrumb(breadcrumb_items)
st.markdown(breadcrumb, unsafe_allow_html=True)
```

#### 8. **Chart Container** - Enhanced Chart Layout

```python
from components import create_chart_container

chart = create_chart_container(
    title="Threat Analysis",
    chart_content="<p>Your chart here</p>",
    legend_items=[
        {"label": "Critical", "color": "#ff006e"},
        {"label": "High", "color": "#ffc107"},
        {"label": "Medium", "color": "#4facfe"},
    ]
)
st.markdown(chart, unsafe_allow_html=True)
```

#### 9. **Animated Cards** - Eye-catching Component

```python
from components import create_animated_card

card = create_animated_card(
    title="Real-time Detection",
    description="Active monitoring",
    value="24/7",
    icon="🛡️",
    animation="slide-in"  # or "fade-in", "slide-in-left", "slide-in-right"
)
st.markdown(card, unsafe_allow_html=True)
```

#### 10. **Timeline Items** - Activity History

```python
from components import create_timeline_item

timeline = create_timeline_item(
    title="Scan Initiated",
    description="User started OSINT scan",
    timestamp="2 hours ago",
    status="completed",  # or "pending", "error"
    icon="▶️"
)
st.markdown(timeline, unsafe_allow_html=True)
```

#### 11. **Info Boxes** - Alert Messages

```python
from components import create_info_box

info = create_info_box(
    message="Operation successful!",
    box_type="success",  # or "info", "warning", "error"
    icon="✅"
)
st.markdown(info, unsafe_allow_html=True)
```

#### 12. **Helper Function** - Render Component

```python
from components import render_component

# Automatically wraps in container and renders
render_component(widget_html)
```

---

## 🎭 Advanced Animations

All animations are CSS-based and smooth. Available animations:

```css
slideIn         /* Fade in with slide down */
fadeIn          /* Simple fade in */
slideInLeft     /* Slide in from left */
slideInRight    /* Slide in from right */
pulse           /* Pulsing opacity */
glow            /* Glowing box shadow */
shimmer         /* Shimmer effect */
```

### Using Animations in Components

```python
card = create_animated_card(
    title="Example",
    description="Desc",
    value="100",
    animation="slide-in"  # Applies animation on load
)
```

### Applying Animations to Elements

```python
html = f'<div class="animate-slide-in">Animated content</div>'
st.markdown(html, unsafe_allow_html=True)
```

---

## 🌓 Theme Toggle

### Enable Theme Toggle

The theme toggle is automatically added to the sidebar:

```python
from style_manager import render_theme_toggle

render_theme_toggle()
```

### Theme Management

```python
from style_manager import set_theme, get_theme

# Set theme
set_theme("dark")  # or "light"

# Get current theme
current = get_theme()
```

---

## 📊 New Style Manager Features

### Enhanced Functions

#### `create_stat_box()` - Statistics Boxes

```python
from style_manager import create_stat_box

stat = create_stat_box(
    label="Active Users",
    value="2,847",
    change="+12%",
    change_positive=True,
    icon="👥"
)
st.markdown(stat, unsafe_allow_html=True)
```

#### `apply_animation()` - Get Animation Class

```python
animation_class = apply_animation("element-id", "slide-in")
# Returns: "animate-slide-in"
```

---

## 🎨 CSS Classes Reference

### Badges
```css
.badge-primary   /* Blue/cyan gradient */
.badge-success   /* Green */
.badge-warning   /* Yellow */
.badge-danger    /* Pink */
.badge-secondary /* Grey with border */
```

### Status Indicators
```css
.status-online   /* Green with glow */
.status-offline  /* Grey */
.status-pending  /* Yellow with glow */
.status-error    /* Pink with glow */
```

### Utilities
```css
.gradient-primary    /* Purple gradient */
.gradient-cool       /* Blue/cyan gradient */
.gradient-warm       /* Red/pink gradient */
.animate-*           /* See animations above */
```

---

## 📋 Complete Example

```python
import streamlit as st
from style_manager import apply_custom_page_style, render_theme_toggle
from components import (
    create_widget, create_badge, create_progress_bar,
    create_status_indicator, BadgeType, StatusType
)

st.set_page_config(page_title="Dashboard", layout="wide")
apply_custom_page_style("Dashboard")
render_theme_toggle()

st.title("📊 Dashboard")

# Row 1: Stat Widgets
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(create_widget(
        title="Total Scans",
        content="<div style='font-size: 2rem; color: #4facfe; font-weight: 700;'>1,234</div>",
        icon="📊"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(create_widget(
        title="Success Rate",
        content="<div style='font-size: 2rem; color: #06d6a0; font-weight: 700;'>94.2%</div>",
        icon="✅"
    ), unsafe_allow_html=True)

with col3:
    st.markdown(create_widget(
        title="Threats",
        content="<div style='font-size: 2rem; color: #ff006e; font-weight: 700;'>127</div>",
        icon="🚨"
    ), unsafe_allow_html=True)

# Row 2: Status & Progress
col1, col2 = st.columns(2)

with col1:
    st.markdown(create_status_indicator(StatusType.ONLINE, "System Status"), unsafe_allow_html=True)
    st.markdown(create_progress_bar("Processing", 65, 100), unsafe_allow_html=True)

with col2:
    st.markdown(create_badge("Active", BadgeType.SUCCESS, "🟢"), unsafe_allow_html=True)
```

---

## 🚀 Best Practices

1. **Import Efficiently**
   ```python
   from components import create_widget, create_badge
   # Avoid importing entire module if not needed
   ```

2. **Use `render_component()` for Simplicity**
   ```python
   render_component(widget_html)  # Automatic rendering
   # vs
   st.markdown(widget_html, unsafe_allow_html=True)
   ```

3. **Combine Components**
   ```python
   # Multiple components in grid
   col1, col2, col3 = st.columns(3)
   with col1:
       render_component(create_widget(...))
   with col2:
       render_component(create_widget(...))
   ```

4. **Use Constants for Types**
   ```python
   from components import BadgeType, StatusType
   
   # Good
   create_badge("text", BadgeType.SUCCESS)
   # Avoid
   create_badge("text", "success")
   ```

5. **CSS Variables in Content**
   ```python
   content = "<div style='color: #4facfe; font-weight: 700;'>Value</div>"
   # Uses theme colors defined in styles.css
   ```

---

## 🔍 Component Showcase

Visit the **Components Showcase** page from the sidebar to see all components in action:
- Live examples of each component
- Interactive demonstrations
- Code snippets for reference

---

## 📱 Responsive Behavior

All components are fully responsive:
- **Tablets (768px)**: Adjusted padding and font sizes
- **Mobile (480px)**: Optimized layout and spacing

Components automatically adapt to screen size without additional configuration.

---

## 🛠️ Customization

### Adding New Badges

Edit `styles.css`:
```css
.badge-custom {
    background: linear-gradient(135deg, #ff6b6b, #ff8787);
    color: white;
}
```

Then in `components.py`:
```python
def create_badge(label, badge_type="custom", icon=""):
    return f'<span class="badge badge-{badge_type}">{icon}{label}</span>'
```

### Creating Custom Components

```python
def create_custom_widget(title, value, description):
    html = f"""
    <div class="widget">
        <div class="widget-title">{title}</div>
        <div style="font-size: 2rem; color: #4facfe;">{value}</div>
        <div class="widget-footer">{description}</div>
    </div>
    """
    return html
```

---

## 📚 Additional Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **CSS Animations**: Check `styles.css` for all keyframes
- **Component Examples**: Visit the Components Showcase page
- **Original Guide**: See `STYLING_GUIDE.md`

---

## 🎯 Summary

### What's Included

✅ 12+ Pre-built UI Components  
✅ Advanced CSS Animations  
✅ Theme Toggle System  
✅ Professional Color Palette  
✅ Responsive Design  
✅ Component Showcase Page  
✅ Complete Code Examples  

### Quick Start

```python
from style_manager import apply_custom_page_style, render_theme_toggle
from components import create_widget, render_component

st.set_page_config(...)
apply_custom_page_style("Dashboard")
render_theme_toggle()

widget_html = create_widget("Title", "Content", "📊")
render_component(widget_html)
```

Enjoy building beautiful Streamlit applications! ✨
