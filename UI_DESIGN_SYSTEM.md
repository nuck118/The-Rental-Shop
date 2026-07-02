# Professional UI Design — Visual Guide

## Color Palette

### Primary Red
```
#fef2f2 ████ 50
#fee2e2 ████ 100
#fecaca ████ 200
#fca5a5 ████ 300
#f87171 ████ 400
#ef4444 ████ 500
#dc2626 ████ 600 (Main)
#b91c1c ████ 700 (Hover)
#991b1b ████ 800
#7f1d1d ████ 900
```

### Neutral Grey
```
#fafafa ████ 50 (Background)
#f5f5f5 ████ 100
#e5e5e5 ████ 200 (Borders)
#d4d4d4 ████ 300
#a3a3a3 ████ 400
#737373 ████ 500
#525252 ████ 600 (Main text)
#404040 ████ 700
#262626 ████ 800
#171717 ████ 900 (Darkest)
```

### Status Colors
```
Green:  #10b981 (Available)
Blue:   #3b82f6 (In Use)
Yellow: #f59e0b (Repair)
Grey:   #6b7280 (Unknown)
```

---

## Signin Page

### Layout
```
┌─────────────────────────────────────────────────────┐
│                                                     │
│                  Background: #fafafa                │
│                                                     │
│                    ┌─────────────┐                  │
│                    │  [🔒 Icon]  │                  │
│                    │  #dc2626    │                  │
│                    └─────────────┘                  │
│                                                     │
│              The Rental Shop                        │
│              font-light, tracking-tight             │
│                                                     │
│         Hardware Rental Management                  │
│         text-neutral-500, font-light                │
│                                                     │
│         ┌─────────────────────────────┐             │
│         │ Username                    │             │
│         │ [✉️] [________________]     │             │
│         │                             │             │
│         │ Password                    │             │
│         │ [🔒] [________________]     │             │
│         │                             │             │
│         │ [Sign In] [→]               │             │
│         │ bg-primary-600              │             │
│         │                             │             │
│         │ Demo: admin / admin123      │             │
│         └─────────────────────────────┘             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Typography
- **Title**: 24px, font-light, tracking-tight, #171717
- **Subtitle**: 14px, font-light, #737373
- **Label**: 14px, font-medium, #404040
- **Button**: 14px, font-medium, white
- **Demo**: 12px, font-light, #737373

### Spacing
- Header to form: 48px
- Form padding: 32px
- Field spacing: 24px
- Button height: 40px

---

## Dashboard Header

### Layout
```
┌─────────────────────────────────────────────────────┐
│ The Rental Shop          [💬] [👤 admin ▼]         │
│ Hardware Rental Management                          │
└─────────────────────────────────────────────────────┘
```

### Components
- **Logo**: 24px, font-light, #171717
- **Subtitle**: 12px, font-light, #737373
- **Chat Button**: Icon, hover bg-neutral-100
- **Profile**: Avatar + username, hover bg-neutral-100
- **Dropdown**: White bg, border-neutral-200

### Colors
- Background: white
- Border: #e5e5e5
- Text: #171717
- Secondary: #737373
- Hover: #f5f5f5

---

## Tab Navigation

### Layout
```
┌─────────────────────────────────────────────────────┐
│ [📦] Available Devices | [🚚] Rented | [📋] History│
└─────────────────────────────────────────────────────┘
```

### States
**Active Tab**
- Text: #dc2626
- Border: #dc2626 (2px bottom)
- Icon: #dc2626

**Inactive Tab**
- Text: #737373
- Border: transparent
- Icon: #737373
- Hover: #171717

### Spacing
- Gap between tabs: 32px
- Padding: 12px horizontal, 12px vertical
- Border width: 2px

---

## Device Card

### Layout
```
┌──────────────────────────────────┐
│ Device Name        [Available]   │
│ Brand              (green badge) │
│                                  │
│ Purchased: 2021-11-23            │
│ Assigned to: john.doe            │
│ Notes: Great camera              │
│                                  │
│ [Rent] or [Return]               │
└──────────────────────────────────┘
```

### Colors
- Background: white
- Border: #e5e5e5
- Hover border: #d4d4d4
- Hover shadow: subtle
- Title: #171717
- Subtitle: #737373
- Button: #dc2626

### Spacing
- Padding: 16px
- Title spacing: 12px
- Content spacing: 8px
- Button height: 32px

### Status Badges
```
Available: bg-green-100, text-green-700
In Use:    bg-blue-100, text-blue-700
Repair:    bg-yellow-100, text-yellow-700
Unknown:   bg-neutral-100, text-neutral-700
```

---

## Chat Panel

### Layout
```
┌──────────────────────────────────┐
│ AI Assistant            [✕]      │
├──────────────────────────────────┤
│                                  │
│ Assistant: Hello! I'm your AI    │
│ assistant. Tell me what kind     │
│ of device you need...            │
│                                  │
│ User: I need a laptop            │
│                                  │
│ Assistant: Great! For software   │
│ development, I'd recommend...    │
│                                  │
│ ┌────────────────────────────┐   │
│ │ Dell XPS 15                │   │
│ │ Dell                       │   │
│ │ Available                  │   │
│ │ Powerful processor...      │   │
│ └────────────────────────────┘   │
│                                  │
├──────────────────────────────────┤
│ [Ask me...]            [Send →]  │
│ Enter to send, Shift+Enter new   │
└──────────────────────────────────┘
```

### Message Styling
**User Message**
- Background: #dc2626
- Text: white
- Alignment: right
- Border radius: 8px
- Padding: 12px

**Assistant Message**
- Background: white
- Border: 1px #e5e5e5
- Text: #171717
- Alignment: left
- Border radius: 8px
- Padding: 12px

### Recommendation Card
- Background: #f5f5f5
- Border: 1px #e5e5e5
- Padding: 12px
- Border radius: 8px
- Font size: 12px

### Input Area
- Background: white
- Border top: 1px #e5e5e5
- Textarea: border-neutral-200
- Button: bg-primary-600
- Hint text: 12px, #737373

---

## Empty States

### Layout
```
┌──────────────────────────────────┐
│                                  │
│          [📦 Icon]               │
│          (text-neutral-300)      │
│                                  │
│   No available devices at the    │
│   moment                         │
│   (text-neutral-600, 14px)       │
│                                  │
└──────────────────────────────────┘
```

### Icons
- Size: 48px
- Color: #d4d4d4
- Margin bottom: 16px

### Text
- Font size: 14px
- Color: #737373
- Font weight: medium

---

## Buttons

### Primary Button
```
┌─────────────────────────────┐
│ [→] Sign In                 │
│ bg-primary-600              │
│ hover:bg-primary-700        │
│ text-white                  │
│ font-medium                 │
│ py-2.5 px-4                 │
│ rounded-lg                  │
└─────────────────────────────┘
```

### Secondary Button
```
┌─────────────────────────────┐
│ [↩️] Return                 │
│ bg-neutral-600              │
│ hover:bg-neutral-700        │
│ text-white                  │
│ font-medium                 │
│ py-2 px-3                   │
│ rounded-lg                  │
└─────────────────────────────┘
```

### Icon Button
```
┌─────────────────────────────┐
│ [💬]                        │
│ p-2                         │
│ hover:bg-neutral-100        │
│ text-neutral-600            │
│ hover:text-primary-600      │
└─────────────────────────────┘
```

---

## Form Elements

### Input Field
```
┌─────────────────────────────┐
│ Username                    │
│ [✉️] [________________]     │
│ border-neutral-200          │
│ focus:ring-primary-500      │
│ rounded-lg                  │
└─────────────────────────────┘
```

### Textarea
```
┌─────────────────────────────┐
│ [Ask me...]                 │
│ [________________]          │
│ [________________]          │
│ border-neutral-200          │
│ focus:ring-primary-500      │
│ rounded-lg                  │
└─────────────────────────────┘
```

### Error Message
```
┌─────────────────────────────┐
│ ⚠️ Invalid username or      │
│ password                    │
│ bg-primary-50               │
│ border-primary-200          │
│ text-primary-700            │
│ rounded-lg                  │
└─────────────────────────────┘
```

---

## Icons

### Icon Sizes
- Header: 20px (w-5 h-5)
- Tab: 16px (w-4 h-4)
- Button: 16px (w-4 h-4)
- Form: 20px (w-5 h-5)
- Empty state: 48px (w-12 h-12)

### Icon Colors
- Primary: #dc2626
- Secondary: #737373
- Disabled: #d4d4d4
- White: #ffffff

### Common Icons
```
Lock        🔒  Authentication
Mail        ✉️  Email/Username
LogIn       →   Sign in
LogOut      ←   Sign out
Package     📦  Available
Truck       🚚  Rented
History     📋  History
MessageCircle 💬 Chat
Send        ↗️  Send
Loader      ⟳   Loading
X           ✕   Close
```

---

## Responsive Breakpoints

### Mobile (< 768px)
- Chat panel: 100% width
- Chat height: 100vh
- Single column grid
- Padding: 16px
- Font sizes: -1px

### Tablet (768px - 1024px)
- Chat panel: 384px width
- Chat height: 600px
- Two column grid
- Padding: 24px
- Font sizes: normal

### Desktop (> 1024px)
- Chat panel: 384px width
- Chat height: 600px
- Three column grid
- Padding: 32px
- Font sizes: normal

---

## Spacing Scale

```
4px   (1)
8px   (2)
12px  (3)
16px  (4)
24px  (6)
32px  (8)
48px  (12)
64px  (16)
```

---

## Shadow Scale

```
shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05)
shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1)
shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1)
```

---

## Border Radius

```
rounded-lg: 8px
rounded-full: 9999px
```

---

## Transitions

```
transition: all 200ms ease
hover: 200ms
focus: 200ms
```

---

## Accessibility

### Color Contrast
- Text on white: 4.5:1 (WCAG AA)
- Text on colored: 4.5:1 (WCAG AA)
- Icons: Same as text

### Focus States
- Ring: 2px solid #dc2626
- Offset: 2px

### Keyboard Navigation
- Tab order: logical
- Focus visible: always
- Shortcuts: documented

---

## Summary

✅ Professional red/grey palette  
✅ Editorial minimalism  
✅ Consistent spacing  
✅ Clear typography  
✅ Icon integration  
✅ Responsive design  
✅ Accessibility support  
✅ Production-ready  

**Design System**: Complete and ready for implementation
