# Login Page Specification

## 🎯 Overview

This document specifies the login page design, functionality, and user experience for the Phase 3 Todo Assistant application. The login page is the entry point for authenticated users and must provide a modern, professional, and user-friendly authentication experience that matches the overall application aesthetics.

---

## 🎨 Design Requirements

### Visual Design

**Design Principles:**
- **Modern & Professional:** Glass morphism card on gradient background
- **Consistent Branding:** Match landing page visual language
- **Accessible:** WCAG 2.1 AA compliance
- **Responsive:** Seamless experience on mobile, tablet, and desktop

**Color Palette:**
- Primary: `#667eea` (Purple)
- Secondary: `#764ba2` (Deep Purple)
- Accent: `#f093fb` (Pink)
- Background: Gradient from `#667eea` to `#764ba2`
- Card: `rgba(255, 255, 255, 0.95)` with `backdrop-filter: blur(20px)`

**Typography:**
- Font Family: Inter (consistent with landing page)
- Title: 2xl-3xl, weight 800
- Subtitle: base, weight 400
- Labels: sm, weight 600
- Inputs: base, weight 400

---

## 🧩 Component Structure

### Layout Hierarchy

```
LoginPage
├── Background Layer
│   ├── Gradient Background
│   └── Animated Orbs (2)
├── Login Card (Glass Morphism)
│   ├── Header Section
│   │   ├── Logo Icon (✨)
│   │   ├── Title ("Todo Assistant")
│   │   └── Subtitle ("Welcome back! Sign in to continue")
│   ├── Form Section
│   │   ├── Email Input Group
│   │   │   ├── Label
│   │   │   ├── Icon (Mail)
│   │   │   └── Input Field
│   │   ├── Password Input Group
│   │   │   ├── Label
│   │   │   ├── Icon (Lock)
│   │   │   ├── Input Field
│   │   │   └── Visibility Toggle (Eye/EyeOff)
│   │   ├── Error Message (conditional)
│   │   └── Submit Button
│   └── Footer Section
│       ├── Back to Home Link
│       └── Sign Up Link (optional)
└── Toast Notifications
```

---

## 📋 Functional Requirements

### FR-1: User Authentication

**Description:** Users must be able to sign in using email and password.

**Acceptance Criteria:**
- Email input validates format (basic HTML5 validation)
- Password input accepts 8+ characters
- Form submits to backend `/auth/login` endpoint
- On success, stores JWT token and user info in Zustand store
- On success, redirects to `/chat` page
- On failure, displays specific error message

**Error Handling:**
- Invalid email format: "Invalid email address"
- Incorrect password: "Incorrect password"
- Account not found: "Account not found. Please sign up first."
- Network error: "Login failed. Please try again."

### FR-2: Password Visibility Toggle

**Description:** Users can toggle password visibility to prevent input errors.

**Acceptance Criteria:**
- Eye icon button appears on right side of password input
- Click toggles between masked (`••••`) and plain text
- Icon changes between Eye (hidden) and EyeOff (visible)
- Maintains input focus during toggle
- Keyboard accessible (Tab + Enter)

### FR-3: Form Validation

**Description:** Client-side validation prevents invalid submissions.

**Acceptance Criteria:**
- Email field requires valid email format
- Password field requires non-empty value
- Submit button disabled when form is invalid
- Fields marked as required with HTML5 attributes
- Browser native validation messages shown

### FR-4: Loading States

**Description:** Visual feedback during authentication request.

**Acceptance Criteria:**
- Submit button shows spinner during API call
- Button text changes to "Signing in..."
- Form inputs disabled during loading
- Loading state clears on success or error

### FR-5: Navigation

**Description:** Users can navigate back to landing page or to sign-up.

**Acceptance Criteria:**
- "Back to Home" link navigates to `/` (landing page)
- Link includes arrow icon for clarity
- Sign-up link navigates to `/signup` (if applicable)
- Links styled consistently with application theme

### FR-6: Session Management

**Description:** Already authenticated users skip login.

**Acceptance Criteria:**
- If JWT token exists in Zustand store, redirect to `/chat`
- Token validation happens before rendering form
- Invalid/expired tokens clear and show login

---

## 🎨 Visual Specifications

### Background

**Gradient:**
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

**Animated Orbs:**
- Orb 1: 400x400px, top-right, `radial-gradient(circle, #fbbf24 0%, transparent 70%)`
- Orb 2: 500x500px, bottom-left, `radial-gradient(circle, #f093fb 0%, transparent 70%)`
- Animation: Float vertically with 20-25s duration

### Login Card

**Dimensions:**
- Max Width: 450px
- Padding: 3rem (48px)
- Border Radius: 1.5rem (24px)
- Mobile: Margin 1rem, padding 2rem

**Glass Morphism:**
```css
background: rgba(255, 255, 255, 0.95);
backdrop-filter: blur(20px);
border: 1px solid rgba(255, 255, 255, 0.3);
box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
```

**Animation:**
- Fade-in on page load: 0.5s ease-out
- Transform: translateY(-20px) → translateY(0)

### Input Fields

**Structure:**
- Label: 0.875rem, weight 600, color `#374151`
- Input wrapper: relative positioning for icons
- Input: padding-left 3rem (for icon space)
- Icon: absolute left, 1rem from left edge

**States:**
- Default: Border `#e5e7eb`, background white
- Focus: Border `#667eea`, box-shadow `0 0 0 4px rgba(102, 126, 234, 0.1)`
- Disabled: Background `#f9fafb`, cursor not-allowed
- Error: Border `#ef4444`

**Input Field Styles:**
```css
padding: 0.75rem 1rem 0.75rem 3rem;
border: 2px solid #e5e7eb;
border-radius: 0.5rem;
font-size: 1rem;
transition: all 0.2s;
```

### Submit Button

**Default State:**
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
color: white;
padding: 1rem;
border-radius: 0.5rem;
font-size: 1.125rem;
font-weight: 700;
```

**Hover State:**
```css
transform: translateY(-2px);
box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
```

**Disabled State:**
```css
opacity: 0.7;
cursor: not-allowed;
transform: none;
```

**Loading State:**
- Spinner: 16px, white, rotating
- Text: "Signing in..."

### Error Message

**Style:**
```css
background: #fee;
border: 1px solid #fcc;
border-radius: 0.5rem;
color: #c33;
padding: 0.75rem 1rem;
font-size: 0.875rem;
display: flex;
align-items: center;
gap: 0.5rem;
```

**Icon:** ⚠️ (warning emoji)

**Animation:** Fade-in 0.3s ease-out

---

## 🔐 Security Specifications

### Password Input Security

**Requirements:**
- Input type `password` by default
- Auto-complete attribute: `current-password`
- No password stored in local storage
- No password logged to console

### Token Management

**Requirements:**
- JWT token stored in Zustand persist (localStorage)
- Token sent in `Authorization: Bearer {token}` header
- Token validated on protected routes
- Token cleared on logout or 401 errors

### HTTPS Requirement

**Production:**
- All authentication requests over HTTPS
- No credentials transmitted over HTTP

---

## 📱 Responsive Design

### Mobile (< 768px)

**Card:**
- Margin: 1rem (16px)
- Padding: 2rem (32px)
- Max width: calc(100vw - 2rem)

**Typography:**
- Title: 1.5rem → 1.25rem
- Inputs: Font size 16px (prevents iOS zoom)

**Layout:**
- Footer links: Stack vertically
- Button: Full width

### Tablet (768px - 1024px)

**Card:**
- Max width: 450px
- Centered with auto margins

### Desktop (> 1024px)

**Card:**
- Max width: 450px
- Centered vertically and horizontally

---

## ♿ Accessibility Requirements

### Keyboard Navigation

**Requirements:**
- Tab order: Email → Password → Toggle → Submit → Links
- Enter key submits form
- Escape key clears focus
- Tab + Shift for reverse navigation

### Screen Reader Support

**Labels:**
- All inputs have associated `<label>` with `for` attribute
- Password toggle has `aria-label="Toggle password visibility"`
- Loading state announces "Signing in"
- Error messages read immediately via `aria-live="polite"`

### Visual Accessibility

**Requirements:**
- Minimum contrast ratio: 4.5:1 for text
- Focus indicators visible and clear
- Error states distinguishable without color alone
- Icon sizing: minimum 24x24px touch target

---

## 🧪 Testing Requirements

### Unit Tests

**Test Cases:**
1. Form renders with all fields
2. Email validation works correctly
3. Password visibility toggle functions
4. Submit button disabled when loading
5. Error messages display correctly
6. Navigation links work
7. Form submission calls API correctly
8. Success redirects to `/chat`
9. Failure shows error message

### Integration Tests

**Test Cases:**
1. Full login flow: input → submit → redirect
2. Invalid credentials show error
3. Network error handled gracefully
4. Already authenticated redirects
5. Token stored in Zustand after success

### E2E Tests

**Test Cases:**
1. User navigates to login page
2. User enters valid credentials
3. User clicks submit
4. User redirected to chat page
5. User can logout and login again

---

## 🎯 User Experience Goals

### Primary Goals

1. **Frictionless Login:** Minimize steps to access application
2. **Clear Feedback:** Users always know system state
3. **Error Recovery:** Helpful error messages guide users
4. **Visual Delight:** Professional, modern design inspires confidence

### Success Metrics

| Metric | Target |
|--------|--------|
| Login Success Rate | > 95% |
| Average Login Time | < 10 seconds |
| Error Recovery Rate | > 80% |
| User Satisfaction | > 4/5 |

---

## 🚀 Implementation Priority

### Phase 1: MVP (Required)

- [x] Basic email/password form
- [x] Authentication API integration
- [x] Success redirect
- [x] Error handling
- [ ] Gradient background with orbs
- [ ] Glass morphism card
- [ ] Password visibility toggle
- [ ] Input icons

### Phase 2: Enhanced UX

- [ ] Loading states with spinner
- [ ] Fade-in animations
- [ ] Better error messages
- [ ] Back to home link
- [ ] Toast notifications

### Phase 3: Advanced Features

- [ ] Remember me checkbox
- [ ] Forgot password link
- [ ] Sign up link
- [ ] Social login buttons (if backend supports)
- [ ] Email format validation (real-time)

---

## 🔗 Integration Points

### Backend API

**Endpoint:** `POST /auth/login`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 123,
    "email": "user@example.com"
  }
}
```

**Error Response (401):**
```json
{
  "detail": "Invalid email or password"
}
```

### Zustand Store

**Auth Store Interface:**
```typescript
interface AuthState {
  token: string | null;
  user: { id: number; email: string } | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}
```

### Routing

**Protected Route Logic:**
- If `isAuthenticated === false` → Redirect to `/login`
- If `isAuthenticated === true` → Allow access to `/chat`

---

## 📄 Component Code Reference

**File:** `frontend/src/app/login/page.tsx`

**Key Dependencies:**
- `lucide-react` - Icons (Mail, Lock, Eye, EyeOff, ArrowLeft)
- `next/navigation` - `useRouter` for redirect
- `@/stores/authStore` - Zustand auth state
- `@/lib/apiClient` - API functions

**State Variables:**
- `email: string` - Email input value
- `password: string` - Password input value
- `showPassword: boolean` - Password visibility state
- `isLoading: boolean` - Loading during API call
- `error: string` - Error message display

---

## 🎨 CSS Variables Reference

```css
/* Colors */
--primary-500: #667eea;
--primary-600: #5a67d8;
--primary-700: #4c51bf;

--gray-50: #f9fafb;
--gray-200: #e5e7eb;
--gray-400: #9ca3af;
--gray-600: #4b5563;
--gray-700: #374151;
--gray-900: #111827;

/* Spacing */
--space-2: 0.5rem;
--space-3: 0.75rem;
--space-4: 1rem;
--space-6: 1.5rem;
--space-8: 2rem;
--space-12: 3rem;

/* Border Radius */
--radius-md: 0.375rem;
--radius-lg: 0.5rem;
--radius-xl: 1.5rem;

/* Typography */
--text-sm: 0.875rem;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-2xl: 1.5rem;
--text-3xl: 1.875rem;

/* Transitions */
--transition-fast: 150ms ease;
--transition-base: 200ms ease;

/* Gradient */
--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

---

## 📊 Performance Requirements

### Load Time

**Targets:**
- Initial paint: < 1s
- Time to interactive: < 2s
- Total page size: < 500KB

**Optimizations:**
- Lazy load animations
- Minimize CSS bundle
- Use Next.js Image optimization (if logo/images added)

### Animation Performance

**Requirements:**
- 60fps animations (use `transform` and `opacity` only)
- Hardware acceleration with `will-change`
- Reduced motion support via `prefers-reduced-motion`

---

## 🔄 State Management

### Form State

**Managed in component:**
- Input values (email, password)
- Validation errors
- Loading state
- Show/hide password

**Not persisted:**
- Password never stored
- Email cleared after successful login

### Authentication State

**Managed in Zustand:**
- JWT token (persisted to localStorage)
- User object (id, email)
- isAuthenticated boolean

**Persistence:**
- Token persists across page reloads
- Cleared on logout or 401 response

---

## 🚨 Error Scenarios

### Network Errors

**Scenario:** API request fails due to network issue

**Response:**
- Error message: "Unable to connect. Please check your internet connection."
- Retry button or manual retry
- Loading state cleared

### Invalid Credentials

**Scenario:** User enters wrong email or password

**Response:**
- Error message: "Invalid email or password. Please try again."
- Form inputs remain populated (except password)
- Focus returns to password field

### Server Error

**Scenario:** Backend returns 500 error

**Response:**
- Error message: "Something went wrong. Please try again later."
- Log error details to console
- Offer reload or support contact

---

## 📚 Related Specifications

- [chatkit-integration.md](./chatkit-integration.md) - Chat interface spec
- [../features/chatbot.md](../features/chatbot.md) - Chatbot features
- [../../CLAUDE.md](../../CLAUDE.md) - Project constitution

---

## 📝 Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-12-26 | 1.0 | Initial specification created | Claude |

---

## ✅ Implementation Checklist

### Visual Design
- [ ] Implement gradient background
- [ ] Add animated orbs
- [ ] Create glass morphism card
- [ ] Add logo/icon to header
- [ ] Apply Inter font family
- [ ] Add fade-in animation

### Form Components
- [ ] Email input with icon
- [ ] Password input with icon
- [ ] Password visibility toggle
- [ ] Submit button with gradient
- [ ] Error message component
- [ ] Loading spinner

### Functionality
- [ ] Form validation
- [ ] API integration
- [ ] Success redirect
- [ ] Error handling
- [ ] Loading states
- [ ] Token storage

### Navigation
- [ ] Back to home link
- [ ] Sign up link (optional)
- [ ] Protected route logic

### Responsive Design
- [ ] Mobile styles (< 768px)
- [ ] Tablet styles (768-1024px)
- [ ] Desktop styles (> 1024px)

### Accessibility
- [ ] Keyboard navigation
- [ ] Screen reader labels
- [ ] Focus indicators
- [ ] ARIA attributes

### Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests
- [ ] Accessibility audit

---

**Status:** Draft - Ready for Implementation
**Last Updated:** 2025-12-26
**Priority:** High (Phase 1 - MVP Enhancement)
