"""
Advanced UI Components Library for Nexus OSINT
==============================================
Provides pre-built components with professional styling
"""

import streamlit as st
from typing import Optional, List, Dict


class BadgeType:
    """Badge type constants"""
    PRIMARY = "primary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    SECONDARY = "secondary"


class StatusType:
    """Status indicator type constants"""
    ONLINE = "online"
    OFFLINE = "offline"
    PENDING = "pending"
    ERROR = "error"


def create_badge(label: str, badge_type: str = BadgeType.PRIMARY, icon: str = "") -> str:
    """
    Create a styled badge component.
    
    Args:
        label: Badge text
        badge_type: Type of badge (primary, success, warning, danger, secondary)
        icon: Optional emoji icon
        
    Returns:
        HTML string for the badge
    """
    icon_html = f"<span style='margin-right: 0.25rem;'>{icon}</span>" if icon else ""
    return f'<span class="badge badge-{badge_type}">{icon_html}{label}</span>'


def create_pill_button(label: str, icon: str = "", onclick: str = "") -> str:
    """
    Create an interactive pill-shaped button.
    
    Args:
        label: Button label
        icon: Optional emoji icon
        onclick: Optional JavaScript onclick handler
        
    Returns:
        HTML string for the pill button
    """
    icon_html = f"<span style='margin-right: 0.375rem;'>{icon}</span>" if icon else ""
    onclick_attr = f'onclick="{onclick}"' if onclick else ""
    return f'<span class="pill" {onclick_attr}>{icon_html}{label}</span>'


def create_tags_cloud(tags: List[str], clickable: bool = False) -> str:
    """
    Create a cloud of tag elements.
    
    Args:
        tags: List of tag strings
        clickable: Whether tags are clickable
        
    Returns:
        HTML string for the tags cloud
    """
    tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in tags])
    return f'<div style="display: flex; flex-wrap: wrap;">{tags_html}</div>'


def create_widget(
    title: str,
    content: str,
    icon: str = "📊",
    footer_text: str = "",
    clickable: bool = False
) -> str:
    """
    Create a dashboard widget card.
    
    Args:
        title: Widget title
        content: Widget main content
        icon: Emoji icon for the widget
        footer_text: Optional footer text
        clickable: Whether widget should be hoverable
        
    Returns:
        HTML string for the widget
    """
    footer_html = f'<div class="widget-footer">{footer_text}</div>' if footer_text else ""
    clickable_class = "cursor-pointer" if clickable else ""
    
    html = f"""
    <div class="widget {clickable_class}">
        <div class="widget-header">
            <div class="widget-title">{title}</div>
            <div class="widget-icon">{icon}</div>
        </div>
        <div class="widget-content">{content}</div>
        {footer_html}
    </div>
    """
    return html


def create_status_indicator(status: str, text: str = "") -> str:
    """
    Create a status indicator with animated dot.
    
    Args:
        status: Status type (online, offline, pending, error)
        text: Optional status text
        
    Returns:
        HTML string for the status indicator
    """
    text_html = f"<span>{text}</span>" if text else ""
    return f'<span style="display: inline-flex; align-items: center; gap: 0.5rem;"><span class="status-indicator status-{status}"></span>{text_html}</span>'


def create_progress_bar(
    label: str,
    value: float,
    max_value: float = 100,
    show_percentage: bool = True,
    color: str = "primary"
) -> str:
    """
    Create a styled progress bar.
    
    Args:
        label: Progress bar label
        value: Current value
        max_value: Maximum value
        show_percentage: Whether to show percentage
        color: Color theme (primary, success, warning, danger)
        
    Returns:
        HTML string for the progress bar
    """
    percentage = (value / max_value) * 100 if max_value > 0 else 0
    percentage = min(100, max(0, percentage))  # Clamp between 0-100
    
    percentage_text = f"<span>{percentage:.0f}%</span>" if show_percentage else ""
    
    html = f"""
    <div class="progress-label">
        <span>{label}</span>
        {percentage_text}
    </div>
    <div class="progress-container">
        <div class="progress-bar" style="width: {percentage}%;"></div>
    </div>
    """
    return html


def create_breadcrumb(items: List[Dict[str, str]]) -> str:
    """
    Create a breadcrumb navigation.
    
    Args:
        items: List of dicts with 'label' and optional 'url' keys
               Last item is considered active
               
    Returns:
        HTML string for the breadcrumb
    """
    breadcrumb_items = []
    
    for i, item in enumerate(items):
        label = item.get('label', 'Item')
        url = item.get('url', '#')
        is_active = i == len(items) - 1
        
        if is_active:
            breadcrumb_items.append(f'<span class="breadcrumb-item active">{label}</span>')
        else:
            breadcrumb_items.append(f'<a href="{url}" class="breadcrumb-item" style="cursor: pointer; text-decoration: none; color: inherit;">{label}</a>')
        
        if i < len(items) - 1:
            breadcrumb_items.append('<span class="breadcrumb-separator">/</span>')
    
    return f'<div class="breadcrumb">{"".join(breadcrumb_items)}</div>'


def create_chart_container(
    title: str,
    chart_content: str,
    legend_items: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Create a styled chart container.
    
    Args:
        title: Chart title
        chart_content: Chart HTML/content
        legend_items: Optional list of legend items with 'label' and 'color' keys
        
    Returns:
        HTML string for the chart container
    """
    legend_html = ""
    if legend_items:
        legend_items_html = []
        for item in legend_items:
            color = item.get('color', '#4facfe')
            label = item.get('label', 'Item')
            legend_items_html.append(f"""
                <div class="chart-legend-item">
                    <div class="chart-legend-color" style="background: {color};"></div>
                    <span>{label}</span>
                </div>
            """)
        legend_html = f'<div class="chart-legend">{"".join(legend_items_html)}</div>'
    
    html = f"""
    <div class="chart-container">
        <div class="chart-title">{title}</div>
        <div>{chart_content}</div>
        {legend_html}
    </div>
    """
    return html


def create_animated_card(
    title: str,
    description: str,
    value: str,
    icon: str = "✨",
    animation: str = "slide-in"
) -> str:
    """
    Create an animated card component.
    
    Args:
        title: Card title
        description: Card description
        value: Main value/metric
        icon: Emoji icon
        animation: Animation type (slide-in, fade-in, slide-in-left, slide-in-right)
        
    Returns:
        HTML string for the animated card
    """
    animation_class = f"animate-{animation}"
    
    html = f"""
    <div class="{animation_class}" style="
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.1), rgba(118, 75, 162, 0.1));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
            <div>
                <div style="font-size: 0.875rem; color: #b8bcc4; font-weight: 500;">{title}</div>
                <div style="font-size: 0.75rem; color: #b8bcc4; margin-top: 0.25rem;">{description}</div>
            </div>
            <div style="font-size: 1.5rem;">{icon}</div>
        </div>
        <div style="font-size: 2rem; font-weight: 700; color: #4facfe;">{value}</div>
    </div>
    """
    return html


def create_timeline_item(
    title: str,
    description: str,
    timestamp: str,
    status: str = "completed",
    icon: str = "✓"
) -> str:
    """
    Create a timeline item for event/activity tracking.
    
    Args:
        title: Item title
        description: Item description
        timestamp: When the event occurred
        status: Status type (completed, pending, error)
        icon: Emoji icon
        
    Returns:
        HTML string for the timeline item
    """
    status_color_map = {
        "completed": "#06d6a0",
        "pending": "#ffc107",
        "error": "#ff006e"
    }
    status_color = status_color_map.get(status, "#4facfe")
    
    html = f"""
    <div style="
        display: flex;
        gap: 1rem;
        margin: 1.5rem 0;
        padding-left: 1rem;
        border-left: 2px solid {status_color};
        padding-bottom: 1rem;
    ">
        <div style="
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, rgba(79, 172, 254, 0.2), rgba(118, 75, 162, 0.2));
            border: 2px solid {status_color};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            flex-shrink: 0;
        ">
            {icon}
        </div>
        <div>
            <div style="font-weight: 600; color: #f0f2f6;">{title}</div>
            <div style="font-size: 0.875rem; color: #b8bcc4; margin-top: 0.25rem;">{description}</div>
            <div style="font-size: 0.75rem; color: #b8bcc4; margin-top: 0.5rem;">{timestamp}</div>
        </div>
    </div>
    """
    return html


def create_info_box(
    message: str,
    box_type: str = "info",
    icon: str = "ℹ️",
    dismissible: bool = False
) -> str:
    """
    Create an info/alert box.
    
    Args:
        message: Message text
        box_type: Type (info, success, error, warning)
        icon: Emoji icon
        dismissible: Whether box can be dismissed
        
    Returns:
        HTML string for the info box
    """
    colors = {
        "info": ("#4facfe", "rgba(79, 172, 254, 0.1)"),
        "success": ("#06d6a0", "rgba(6, 214, 160, 0.1)"),
        "error": ("#ff006e", "rgba(255, 0, 110, 0.1)"),
        "warning": ("#ffc107", "rgba(255, 193, 7, 0.1)"),
    }
    
    color, bg_color = colors.get(box_type, colors["info"])
    close_btn = '<span style="cursor: pointer; margin-left: auto; font-size: 1.25rem; color: inherit;">×</span>' if dismissible else ""
    
    html = f"""
    <div style="
        background-color: {bg_color};
        border-left: 4px solid {color};
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    ">
        <div style="font-size: 1.5rem;">{icon}</div>
        <div style="color: #f0f2f6; font-size: 0.95rem; flex: 1;">{message}</div>
        {close_btn}
    </div>
    """
    return html


def render_component(html_content: str, use_container: bool = True) -> None:
    """
    Render HTML component in Streamlit.
    
    Args:
        html_content: HTML string to render
        use_container: Whether to use a container
    """
    if use_container:
        with st.container():
            st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.markdown(html_content, unsafe_allow_html=True)
