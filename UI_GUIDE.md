# Dashboard & Signin — Visual UI Guide

## Signin Page

### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    Gradient Background                          │
│                  (Blue to Indigo)                               │
│                                                                 │
│                  ┌─────────────────────┐                        │
│                  │   The Rental Shop   │                        │
│                  │ Hardware Rental     │                        │
│                  │ Management          │                        │
│                  └─────────────────────┘                        │
│                                                                 │
│                  ┌─────────────────────┐                        │
│                  │ Username            │                        │
│                  │ [_______________]   │                        │
│                  │                     │                        │
│                  │ Password            │                        │
│                  │ [_______________]   │                        │
│                  │                     │                        │
│                  │ [  Sign In  ]       │                        │
│                  │                     │                        │
│                  │ Demo: admin/admin123│                        │
│                  └─────────────────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Features
- **Gradient Background**: Blue to indigo gradient
- **Centered Card**: White background with shadow
- **Form Fields**: Username and password inputs
- **Sign In Button**: Indigo color with hover effect
- **Demo Credentials**: Displayed below form
- **Error Messages**: Red background with border
- **Loading State**: Button shows "Signing in..."
- **Keyboard Support**: Enter key triggers login

### Color Scheme
- Background: `from-blue-50 to-indigo-100`
- Card: White with shadow
- Button: Indigo-600 (hover: Indigo-700)
- Error: Red-50 background, Red-700 text
- Input Focus: Indigo-500 ring

### Responsive
- Mobile: Full width with padding
- Tablet: Centered, max-width 28rem
- Desktop: Centered, max-width 28rem

---

## Dashboard Header

### Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ The Rental Shop              [👤 admin ▼]                      │
│ Hardware Rental Management                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Features
- **Logo**: "The Rental Shop" title
- **Subtitle**: "Hardware Rental Management"
- **User Profile**: Avatar with username
- **Dropdown Menu**: Sign Out option
- **Responsive**: Stacks on mobile

### Profile Dropdown
```
┌──────────────────┐
│ Sign Out         │
└──────────────────┘
```

---

## Dashboard Tabs

### Tab Navigation
```
┌─────────────────────────────────────────────────────────────────┐
│ 📦 Available Devices | 🚚 Rented Devices | 📋 History          │
└─────────────────────────────────────────────────────────────────┘
```

### Tab Styling
- **Active Tab**: Indigo-600 text, indigo-600 bottom border
- **Inactive Tab**: Gray-600 text, transparent border
- **Hover**: Gray-900 text
- **Transition**: Smooth color change

---

## Available Devices Tab

### Grid Layout
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Device Name  │  │ Device Name  │  │ Device Name  │          │
│  │ Brand        │  │ Brand        │  │ Brand        │          │
│  │              │  │              │  │              │          │
│  │ ✓ Available  │  │ ✓ Available  │  │ ✓ Available  │          │
│  │              │  │              │  │              │          │
│  │ Purchased:   │  │ Purchased:   │  │ Purchased:   │          │
│  │ 2021-11-23   │  │ 2021-11-23   │  │ 2021-11-23   │          │
│  │              │  │              │  │              │          │
│  │ [  Rent  ]   │  │ [  Rent  ]   │  │ [  Rent  ]   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Device Name  │  │ Device Name  │  │ Device Name  │          │
│  │ Brand        │  │ Brand        │  │ Brand        │          │
│  │              │  │              │  │              │          │
│  │ ✓ Available  │  │ ✓ Available  │  │ ✓ Available  │          │
│  │              │  │              │  │              │          │
│  │ Purchased:   │  │ Purchased:   │  │ Purchased:   │          │
│  │ 2021-11-23   │  │ 2021-11-23   │  │ 2021-11-23   │          │
│  │              │  │              │  │              │          │
│  │ [  Rent  ]   │  │ [  Rent  ]   │  │ [  Rent  ]   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Device Card
```
┌──────────────────────────────┐
│ Apple iPhone 13 Pro Max      │
│ Apple                        │
│                              │
│ ✓ Available                  │
│                              │
│ Purchased: 2021-11-23        │
│ Notes: Great camera          │
│                              │
│ [  Rent  ]                   │
└──────────────────────────────┘
```

### Status Badge Colors
- **Available**: Green background, green text
- **In Use**: Blue background, blue text
- **Repair**: Yellow background, yellow text
- **Unknown**: Gray background, gray text

### Responsive Grid
- Mobile (< 768px): 1 column
- Tablet (768px - 1024px): 2 columns
- Desktop (> 1024px): 3 columns

---

## Rented Devices Tab

### Layout
Same as Available Devices, but:
- Shows devices with status "In Use"
- Button says "Return" instead of "Rent"
- Button color: Orange-600 (hover: Orange-700)

### Device Card
```
┌──────────────────────────────┐
│ Dell XPS 15                  │
│ Dell                         │
│                              │
│ 🔵 In Use                    │
│                              │
│ Purchased: 2023-01-15        │
│ Assigned to: john.doe        │
│                              │
│ [  Return  ]                 │
└──────────────────────────────┘
```

---

## History Tab

### Table Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ Device Name    │ Brand  │ Status    │ Purchased  │ Assigned To │
├─────────────────────────────────────────────────────────────────┤
│ iPhone 13 Pro  │ Apple  │ Available │ 2021-11-23 │ —           │
│ Dell XPS 15    │ Dell   │ In Use    │ 2023-01-15 │ john.doe    │
│ Samsung S21    │ Samsung│ Repair    │ 2022-06-10 │ —           │
│ MacBook Pro    │ Apple  │ Available │ 2023-03-20 │ —           │
│ iPad Air       │ Apple  │ In Use    │ 2022-09-05 │ jane.smith  │
│ Pixel 7        │ Google │ Available │ 2022-10-13 │ —           │
│ Surface Pro    │ Microsoft│ Available│ 2023-02-28 │ —           │
│ Galaxy Tab     │ Samsung│ In Use    │ 2022-11-01 │ bob.wilson  │
└─────────────────────────────────────────────────────────────────┘
```

### Table Features
- **Sortable Columns**: Click to sort
- **Status Badges**: Color-coded
- **Responsive**: Horizontal scroll on mobile
- **Hover Effects**: Row highlight on hover
- **Empty State**: Message if no devices

### Status Badge Colors (in table)
- **Available**: Green badge
- **In Use**: Blue badge
- **Repair**: Yellow badge
- **Unknown**: Gray badge

---

## Loading State

### Spinner
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                      ⟳ Loading...                               │
│                                                                 │
│                  Loading devices...                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Features
- Animated spinner
- "Loading devices..." message
- Centered on page
- Appears while fetching data

---

## Error State

### Error Box
```
┌─────────────────────────────────────────────────────────────────┐
│ ⚠️ Failed to fetch devices                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Features
- Red background
- Red border
- Red text
- Error message
- User can retry by switching tabs

---

## Empty States

### No Available Devices
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│              No available devices at the moment                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### No Rented Devices
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│              You don't have any rented devices                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### No History
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                 No device history available                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Mobile View

### Signin Page (Mobile)
```
┌──────────────────────┐
│                      │
│ The Rental Shop      │
│ Hardware Rental      │
│ Management           │
│                      │
│ Username             │
│ [______________]     │
│                      │
│ Password             │
│ [______________]     │
│                      │
│ [  Sign In  ]        │
│                      │
│ Demo: admin/admin123 │
│                      │
└──────────────────────┘
```

### Dashboard Header (Mobile)
```
┌──────────────────────┐
│ The Rental Shop      │
│ Hardware Rental      │
│ Management           │
│              [👤 ▼]  │
└──────────────────────┘
```

### Tabs (Mobile)
```
┌──────────────────────┐
│ 📦 Available         │
│ 🚚 Rented           │
│ 📋 History          │
└──────────────────────┘
```

### Device Cards (Mobile)
```
┌──────────────────────┐
│ Device Name          │
│ Brand                │
│                      │
│ ✓ Available          │
│                      │
│ Purchased: 2021-... │
│                      │
│ [  Rent  ]           │
└──────────────────────┘
```

### Table (Mobile)
```
Horizontal scroll →

Device Name │ Brand │ Status │ ...
─────────────────────────────────
iPhone 13   │ Apple │ Avail. │ ...
Dell XPS    │ Dell  │ In Use │ ...
```

---

## Tablet View

### Grid Layout (Tablet)
```
┌──────────────────────────────────────────────────┐
│                                                  │
│  ┌──────────────┐  ┌──────────────┐             │
│  │ Device Name  │  │ Device Name  │             │
│  │ Brand        │  │ Brand        │             │
│  │              │  │              │             │
│  │ ✓ Available  │  │ ✓ Available  │             │
│  │              │  │              │             │
│  │ Purchased:   │  │ Purchased:   │             │
│  │ 2021-11-23   │  │ 2021-11-23   │             │
│  │              │  │              │             │
│  │ [  Rent  ]   │  │ [  Rent  ]   │             │
│  └──────────────┘  └──────────────┘             │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐             │
│  │ Device Name  │  │ Device Name  │             │
│  │ Brand        │  │ Brand        │             │
│  │              │  │              │             │
│  │ ✓ Available  │  │ ✓ Available  │             │
│  │              │  │              │             │
│  │ Purchased:   │  │ Purchased:   │             │
│  │ 2021-11-23   │  │ 2021-11-23   │             │
│  │              │  │              │             │
│  │ [  Rent  ]   │  │ [  Rent  ]   │             │
│  └──────────────┘  └──────────────┘             │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## Desktop View

### Full Layout
```
┌─────────────────────────────────────────────────────────────────┐
│ The Rental Shop              [👤 admin ▼]                      │
│ Hardware Rental Management                                      │
├─────────────────────────────────────────────────────────────────┤
│ 📦 Available Devices | 🚚 Rented Devices | 📋 History          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Device Name  │  │ Device Name  │  │ Device Name  │          │
│  │ Brand        │  │ Brand        │  │ Brand        │          │
│  │              │  │              │  │              │          │
│  │ ✓ Available  │  │ ✓ Available  │  │ ✓ Available  │          │
│  │              │  │              │  │              │          │
│  │ Purchased:   │  │ Purchased:   │  │ Purchased:   │          │
│  │ 2021-11-23   │  │ 2021-11-23   │  │ 2021-11-23   │          │
│  │              │  │              │  │              │          │
│  │ [  Rent  ]   │  │ [  Rent  ]   │  │ [  Rent  ]   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Device Name  │  │ Device Name  │  │ Device Name  │          │
│  │ Brand        │  │ Brand        │  │ Brand        │          │
│  │              │  │              │  │              │          │
│  │ ✓ Available  │  │ ✓ Available  │  │ ✓ Available  │          │
│  │              │  │              │  │              │          │
│  │ Purchased:   │  │ Purchased:   │  │ Purchased:   │          │
│  │ 2021-11-23   │  │ 2021-11-23   │  │ 2021-11-23   │          │
│  │              │  │              │  │              │          │
│  │ [  Rent  ]   │  │ [  Rent  ]   │  │ [  Rent  ]   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Color Palette

### Primary Colors
- **Indigo-600**: Primary action (buttons, active tabs)
- **Indigo-700**: Hover state
- **Indigo-50**: Light background

### Status Colors
- **Green**: Available (green-100 bg, green-800 text)
- **Blue**: In Use (blue-100 bg, blue-800 text)
- **Yellow**: Repair (yellow-100 bg, yellow-800 text)
- **Gray**: Unknown (gray-100 bg, gray-800 text)

### Semantic Colors
- **Red**: Errors (red-50 bg, red-700 text)
- **Orange**: Return button (orange-600, hover: orange-700)
- **White**: Cards and backgrounds
- **Gray**: Text and borders

### Text Colors
- **Gray-900**: Primary text
- **Gray-700**: Secondary text
- **Gray-600**: Tertiary text
- **White**: On colored backgrounds

---

## Typography

### Headings
- **H1**: "The Rental Shop" (text-3xl, font-bold)
- **H2**: Tab labels (text-sm, font-medium)
- **H3**: Device name (font-semibold)

### Body Text
- **Regular**: Device details (text-sm, text-gray-600)
- **Semibold**: Labels (font-semibold)
- **Bold**: Important info (font-bold)

### Button Text
- **Semibold**: Button labels (font-semibold)

---

## Spacing

### Padding
- **Card**: px-4 py-3
- **Input**: px-4 py-2
- **Button**: py-2 px-4
- **Container**: px-4 sm:px-6 lg:px-8

### Margins
- **Section**: mb-8
- **Form field**: mb-4
- **Card gap**: gap-6

### Border Radius
- **Card**: rounded-lg
- **Input**: rounded-lg
- **Button**: rounded-lg
- **Badge**: rounded-full

---

## Interactions

### Hover Effects
- **Card**: Shadow increases
- **Button**: Background darkens
- **Tab**: Text color changes
- **Row**: Background highlights

### Focus States
- **Input**: Ring-2 ring-indigo-500
- **Button**: Outline visible
- **Tab**: Underline visible

### Active States
- **Tab**: Indigo text, indigo border
- **Button**: Darker background
- **Input**: Ring visible

### Disabled States
- **Button**: Gray background, cursor not-allowed
- **Input**: Gray background, opacity reduced

---

## Animations

### Transitions
- **Color**: 200ms ease
- **Shadow**: 200ms ease
- **Border**: 200ms ease

### Loading Spinner
- **Rotation**: Continuous 360° rotation
- **Duration**: 1s per rotation
- **Easing**: Linear

### Tab Switch
- **Fade**: Instant (no animation)
- **Content**: Appears immediately

---

## Accessibility

### Keyboard Navigation
- Tab through form fields
- Enter to submit form
- Tab through tabs
- Enter to activate tab

### Screen Readers
- Form labels associated with inputs
- Button labels descriptive
- Status badges have text labels
- Error messages announced

### Color Contrast
- All text meets WCAG AA standards
- Status badges have text + color
- Buttons have sufficient contrast

---

## Summary

The UI is designed to be:
- **Clean**: Minimal, focused design
- **Modern**: Gradient backgrounds, smooth transitions
- **Responsive**: Works on all screen sizes
- **Accessible**: Keyboard navigation, screen reader support
- **Intuitive**: Clear labels, obvious actions
- **Professional**: Polished, production-ready appearance
