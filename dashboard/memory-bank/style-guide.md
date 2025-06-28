# SENSORS DASHBOARD STYLE GUIDE

**Version**: 1.0
**Date**: 2025-06-26
**Framework**: Plotly Dash with Dash Bootstrap Components
**Target**: Responsive sensors monitoring dashboard

## 🎨 COLOR PALETTE

### Primary Colors
- **Primary Blue**: `#2E86AB` - Main brand color, primary actions, headers
- **Secondary Blue**: `#A23B72` - Secondary actions, highlights
- **Accent Teal**: `#F18F01` - Data points, interactive elements

### Status Colors
- **Success Green**: `#10B981` - Success states, positive metrics
- **Warning Orange**: `#F59E0B` - Warning states, attention needed
- **Error Red**: `#EF4444` - Error states, critical alerts
- **Info Blue**: `#3B82F6` - Information, neutral states

### Neutral Colors
- **Dark Gray**: `#1F2937` - Primary text, headers
- **Medium Gray**: `#6B7280` - Secondary text, labels
- **Light Gray**: `#F3F4F6` - Backgrounds, borders
- **White**: `#FFFFFF` - Card backgrounds, content areas

### Data Visualization Colors
- **Temperature**: `#FF6B6B` - Temperature charts and indicators
- **Humidity**: `#4ECDC4` - Humidity charts and indicators  
- **Battery**: `#45B7D1` - Battery level indicators
- **Multi-location**: `['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']`

## 📝 TYPOGRAPHY

### Font Families
- **Primary**: `'Inter', 'Segoe UI', 'Roboto', sans-serif` - Clean, modern, readable
- **Monospace**: `'Fira Code', 'Monaco', 'Consolas', monospace` - Data values, timestamps

### Font Sizes & Weights
```css
/* Headers */
.h1 { font-size: 2.5rem; font-weight: 700; } /* Page title */
.h2 { font-size: 2rem; font-weight: 600; }   /* Section headers */
.h3 { font-size: 1.5rem; font-weight: 600; } /* Component headers */
.h4 { font-size: 1.25rem; font-weight: 500; }/* Sub-headers */

/* Body Text */
.body-large { font-size: 1.125rem; font-weight: 400; } /* Important text */
.body { font-size: 1rem; font-weight: 400; }           /* Standard text */
.body-small { font-size: 0.875rem; font-weight: 400; } /* Secondary text */

/* Data & Labels */
.label { font-size: 0.75rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.data-large { font-size: 2rem; font-weight: 700; font-family: monospace; } /* Key metrics */
.data { font-size: 1.25rem; font-weight: 600; font-family: monospace; }    /* Data values */
```

## 📏 SPACING SYSTEM

### Base Unit: 8px
```css
/* Spacing Scale (based on 8px base unit) */
.space-1 { margin/padding: 4px; }   /* 0.5 units */
.space-2 { margin/padding: 8px; }   /* 1 unit - base */
.space-3 { margin/padding: 12px; }  /* 1.5 units */
.space-4 { margin/padding: 16px; }  /* 2 units */
.space-6 { margin/padding: 24px; }  /* 3 units */
.space-8 { margin/padding: 32px; }  /* 4 units */
.space-12 { margin/padding: 48px; } /* 6 units */
.space-16 { margin/padding: 64px; } /* 8 units */
```

### Layout Spacing
- **Component Margin**: 24px (space-6)
- **Section Padding**: 32px (space-8)
- **Card Padding**: 24px (space-6)
- **Button Padding**: 12px 24px (space-3 space-6)
- **Input Padding**: 12px 16px (space-3 space-4)

## 🔘 COMPONENT STYLES

### Buttons
```python
# Primary Button
primary_button_style = {
    'backgroundColor': '#2E86AB',
    'color': 'white',
    'border': 'none',
    'borderRadius': '8px',
    'padding': '12px 24px',
    'fontSize': '1rem',
    'fontWeight': '500',
    'cursor': 'pointer',
    'transition': 'all 0.2s ease'
}

# Secondary Button
secondary_button_style = {
    'backgroundColor': 'transparent',
    'color': '#2E86AB',
    'border': '2px solid #2E86AB',
    'borderRadius': '8px',
    'padding': '10px 22px',
    'fontSize': '1rem',
    'fontWeight': '500',
    'cursor': 'pointer',
    'transition': 'all 0.2s ease'
}

# Icon Button
icon_button_style = {
    'backgroundColor': '#F3F4F6',
    'color': '#6B7280',
    'border': 'none',
    'borderRadius': '6px',
    'padding': '8px',
    'cursor': 'pointer',
    'transition': 'all 0.2s ease'
}
```

### Cards
```python
# Main Card
card_style = {
    'backgroundColor': 'white',
    'borderRadius': '12px',
    'boxShadow': '0 1px 3px rgba(0, 0, 0, 0.1)',
    'border': '1px solid #F3F4F6',
    'padding': '24px',
    'marginBottom': '24px'
}

# Statistics Card
stats_card_style = {
    'backgroundColor': 'white',
    'borderRadius': '8px',
    'boxShadow': '0 1px 3px rgba(0, 0, 0, 0.1)',
    'border': '1px solid #F3F4F6',
    'padding': '20px',
    'textAlign': 'center',
    'minHeight': '120px'
}
```

### Form Elements
```python
# Input Field
input_style = {
    'border': '2px solid #F3F4F6',
    'borderRadius': '8px',
    'padding': '12px 16px',
    'fontSize': '1rem',
    'backgroundColor': 'white',
    'transition': 'border-color 0.2s ease'
}

# Dropdown
dropdown_style = {
    'border': '2px solid #F3F4F6',
    'borderRadius': '8px',
    'backgroundColor': 'white',
    'fontSize': '1rem'
}
```

## 📱 RESPONSIVE DESIGN

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px  
- **Desktop**: > 1024px

### Layout Grid
- **Mobile**: Single column, full width
- **Tablet**: 2-column grid for statistics, single column for charts
- **Desktop**: 3-4 column grid for statistics, side-by-side charts

### Component Behavior
- **Navigation**: Collapsible on mobile
- **Charts**: Full width on mobile, responsive scaling
- **Statistics Cards**: Stack vertically on mobile
- **Control Panel**: Vertical layout on mobile

## 📊 CHART STYLING

### Chart Colors
```python
chart_config = {
    'temperature': {
        'line_color': '#FF6B6B',
        'fill_color': 'rgba(255, 107, 107, 0.1)',
        'marker_color': '#FF6B6B'
    },
    'humidity': {
        'line_color': '#4ECDC4',
        'fill_color': 'rgba(78, 205, 196, 0.1)',
        'marker_color': '#4ECDC4'
    },
    'battery': {
        'line_color': '#45B7D1',
        'fill_color': 'rgba(69, 183, 209, 0.1)',
        'marker_color': '#45B7D1'
    }
}
```

### Chart Layout
```python
chart_layout = {
    'plot_bgcolor': 'white',
    'paper_bgcolor': 'white',
    'font': {'family': 'Inter, sans-serif', 'size': 12, 'color': '#1F2937'},
    'title': {'font': {'size': 16, 'color': '#1F2937'}},
    'xaxis': {
        'gridcolor': '#F3F4F6',
        'linecolor': '#E5E7EB',
        'tickcolor': '#E5E7EB'
    },
    'yaxis': {
        'gridcolor': '#F3F4F6',
        'linecolor': '#E5E7EB',
        'tickcolor': '#E5E7EB'
    },
    'margin': {'l': 60, 'r': 20, 't': 40, 'b': 60}
}
```

## 🎯 INTERACTION PATTERNS

### Hover States
- **Buttons**: Slightly darker background, subtle scale (1.02x)
- **Cards**: Subtle shadow increase
- **Chart Points**: Highlight with tooltip

### Loading States
- **Spinner**: Primary blue color with smooth rotation
- **Skeleton**: Light gray placeholder matching content structure
- **Progress**: Linear progress bar in primary color

### Error States
- **Input Validation**: Red border with error message below
- **Data Loading**: Error card with retry button
- **Connection Issues**: Warning banner with status

## 🔍 ACCESSIBILITY

### Color Contrast
- All text meets WCAG AA standards (4.5:1 ratio minimum)
- Interactive elements have sufficient contrast
- Status colors work for colorblind users

### Focus States
- Clear focus indicators for keyboard navigation
- Logical tab order through interface
- Skip links for screen readers

### Semantic HTML
- Proper heading hierarchy (h1 → h2 → h3)
- ARIA labels for interactive elements
- Alt text for icons and images

## 💡 USAGE GUIDELINES

### Do's
- Use consistent spacing from the 8px grid system
- Maintain color palette consistency
- Ensure responsive behavior on all devices
- Provide clear visual hierarchy
- Use loading states for data fetching

### Don'ts
- Don't mix different color schemes
- Don't use colors outside the defined palette
- Don't break the spacing system
- Don't create overly complex layouts
- Don't ignore accessibility requirements

## 🔧 Dash Bootstrap Components Classes

### Utility Classes
```python
# Layout
'container-fluid'  # Full width container
'row'             # Bootstrap row
'col-12 col-md-6 col-lg-4'  # Responsive columns

# Spacing
'mb-4'    # Margin bottom (24px)
'p-3'     # Padding (16px)
'mx-auto' # Horizontal center

# Text
'text-center'    # Center align
'text-muted'     # Secondary text color
'fw-bold'        # Bold font weight
```

### Component Classes
```python
# Cards
'card'           # Basic card
'card-body'      # Card content area
'card-header'    # Card header

# Buttons
'btn btn-primary'    # Primary button
'btn btn-outline-primary'  # Secondary button
'btn btn-sm'         # Small button
```

This style guide ensures consistent, modern, and accessible design across the sensors dashboard application.
