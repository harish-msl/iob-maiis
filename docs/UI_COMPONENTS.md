# UI Components Documentation

**IOB MAIIS - UI Component Library**  
**Date**: 2025-01-17  
**Status**: ✅ COMPLETE

---

## 📋 Overview

This document covers all UI components available in the IOB MAIIS application. These components are built using Radix UI primitives and styled with Tailwind CSS.

---

## 🎨 Available Components

### Core Components (Already Implemented)

1. **Button** - `src/components/ui/button.tsx`
2. **Card** - `src/components/ui/card.tsx`
3. **Input** - `src/components/ui/input.tsx`
4. **Label** - `src/components/ui/label.tsx`
5. **Avatar** - `src/components/ui/avatar.tsx`
6. **Badge** - `src/components/ui/badge.tsx`
7. **Separator** - `src/components/ui/separator.tsx`
8. **Dropdown Menu** - `src/components/ui/dropdown-menu.tsx`

### New Components (Just Added)

9. **Dialog** - `src/components/ui/dialog.tsx` ✅ NEW
10. **Select** - `src/components/ui/select.tsx` ✅ NEW
11. **Tabs** - `src/components/ui/tabs.tsx` ✅ NEW
12. **Skeleton** - `src/components/ui/skeleton.tsx` ✅ NEW
13. **Table** - `src/components/ui/table.tsx` ✅ NEW

---

## 📚 Component Usage

### 1. Dialog Component

**Purpose**: Modal dialogs for forms, confirmations, and alerts

**Basic Usage**:
```tsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

<Dialog>
  <DialogTrigger asChild>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Are you sure?</DialogTitle>
      <DialogDescription>
        This action cannot be undone.
      </DialogDescription>
    </DialogHeader>
    {/* Dialog content */}
  </DialogContent>
</Dialog>
```

**With Form**:
```tsx
<Dialog>
  <DialogTrigger asChild>
    <Button>Transfer Money</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Transfer Funds</DialogTitle>
      <DialogDescription>
        Enter transfer details below
      </DialogDescription>
    </DialogHeader>
    <form>
      <div className="grid gap-4 py-4">
        <Input placeholder="Amount" type="number" />
        <Input placeholder="Recipient" />
      </div>
      <DialogFooter>
        <Button type="submit">Transfer</Button>
      </DialogFooter>
    </form>
  </DialogContent>
</Dialog>
```

---

### 2. Select Component

**Purpose**: Dropdown select menus for choosing options

**Basic Usage**:
```tsx
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

<Select>
  <SelectTrigger className="w-[180px]">
    <SelectValue placeholder="Select account" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="checking">Checking</SelectItem>
    <SelectItem value="savings">Savings</SelectItem>
    <SelectItem value="credit">Credit Card</SelectItem>
  </SelectContent>
</Select>
```

**With Groups**:
```tsx
import { SelectGroup, SelectLabel } from "@/components/ui/select"

<Select>
  <SelectTrigger>
    <SelectValue placeholder="Select category" />
  </SelectTrigger>
  <SelectContent>
    <SelectGroup>
      <SelectLabel>Expenses</SelectLabel>
      <SelectItem value="shopping">Shopping</SelectItem>
      <SelectItem value="dining">Dining</SelectItem>
    </SelectGroup>
    <SelectGroup>
      <SelectLabel>Income</SelectLabel>
      <SelectItem value="salary">Salary</SelectItem>
      <SelectItem value="freelance">Freelance</SelectItem>
    </SelectGroup>
  </SelectContent>
</Select>
```

**Form Integration**:
```tsx
import { Controller } from "react-hook-form"

<Controller
  name="accountType"
  control={control}
  render={({ field }) => (
    <Select onValueChange={field.onChange} defaultValue={field.value}>
      <SelectTrigger>
        <SelectValue placeholder="Select type" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="checking">Checking</SelectItem>
        <SelectItem value="savings">Savings</SelectItem>
      </SelectContent>
    </Select>
  )}
/>
```

---

### 3. Tabs Component

**Purpose**: Organize content into tabbed interfaces

**Basic Usage**:
```tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

<Tabs defaultValue="overview">
  <TabsList>
    <TabsTrigger value="overview">Overview</TabsTrigger>
    <TabsTrigger value="transactions">Transactions</TabsTrigger>
    <TabsTrigger value="analytics">Analytics</TabsTrigger>
  </TabsList>
  <TabsContent value="overview">
    <Card>Overview content</Card>
  </TabsContent>
  <TabsContent value="transactions">
    <TransactionTable />
  </TabsContent>
  <TabsContent value="analytics">
    <AnalyticsCharts />
  </TabsContent>
</Tabs>
```

**Voice Controls Example**:
```tsx
<Tabs defaultValue="record">
  <TabsList className="grid w-full grid-cols-2">
    <TabsTrigger value="record">Record</TabsTrigger>
    <TabsTrigger value="tts">Text-to-Speech</TabsTrigger>
  </TabsList>
  <TabsContent value="record">
    <VoiceRecorder />
  </TabsContent>
  <TabsContent value="tts">
    <TTSForm />
  </TabsContent>
</Tabs>
```

---

### 4. Skeleton Component

**Purpose**: Loading placeholders for content

**Basic Usage**:
```tsx
import { Skeleton } from "@/components/ui/skeleton"

// Simple skeleton
<Skeleton className="h-12 w-12 rounded-full" />
<Skeleton className="h-4 w-[250px]" />

// Card skeleton
<Card>
  <CardHeader>
    <Skeleton className="h-4 w-[200px]" />
    <Skeleton className="h-4 w-[150px]" />
  </CardHeader>
  <CardContent>
    <Skeleton className="h-[200px] w-full" />
  </CardContent>
</Card>
```

**Table Skeleton**:
```tsx
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Name</TableHead>
      <TableHead>Amount</TableHead>
      <TableHead>Date</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {Array.from({ length: 5 }).map((_, i) => (
      <TableRow key={i}>
        <TableCell>
          <Skeleton className="h-4 w-[150px]" />
        </TableCell>
        <TableCell>
          <Skeleton className="h-4 w-[100px]" />
        </TableCell>
        <TableCell>
          <Skeleton className="h-4 w-[120px]" />
        </TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

---

### 5. Table Component

**Purpose**: Display tabular data with sorting and filtering

**Basic Usage**:
```tsx
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Transaction</TableHead>
      <TableHead>Amount</TableHead>
      <TableHead>Date</TableHead>
      <TableHead>Status</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {transactions.map((tx) => (
      <TableRow key={tx.id}>
        <TableCell>{tx.description}</TableCell>
        <TableCell>${tx.amount}</TableCell>
        <TableCell>{tx.date}</TableCell>
        <TableCell>
          <Badge variant={tx.status === 'completed' ? 'success' : 'warning'}>
            {tx.status}
          </Badge>
        </TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

**With Caption and Footer**:
```tsx
<Table>
  <TableCaption>A list of your recent transactions</TableCaption>
  <TableHeader>
    <TableRow>
      <TableHead>Date</TableHead>
      <TableHead>Description</TableHead>
      <TableHead className="text-right">Amount</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {transactions.map((tx) => (
      <TableRow key={tx.id}>
        <TableCell>{tx.date}</TableCell>
        <TableCell>{tx.description}</TableCell>
        <TableCell className="text-right">${tx.amount}</TableCell>
      </TableRow>
    ))}
  </TableBody>
  <TableFooter>
    <TableRow>
      <TableCell colSpan={2}>Total</TableCell>
      <TableCell className="text-right">${total}</TableCell>
    </TableRow>
  </TableFooter>
</Table>
```

---

## 🎨 Styling Guidelines

### Color System

Components use the Tailwind color palette with semantic tokens:

```css
/* Background colors */
background: hsl(var(--background))
foreground: hsl(var(--foreground))
muted: hsl(var(--muted))
popover: hsl(var(--popover))

/* Interactive colors */
primary: hsl(var(--primary))
secondary: hsl(var(--secondary))
accent: hsl(var(--accent))
destructive: hsl(var(--destructive))

/* Border & Ring */
border: hsl(var(--border))
ring: hsl(var(--ring))
```

### Component Variants

Most components support variants via the `variant` prop:

```tsx
// Button variants
<Button variant="default">Default</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Cancel</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>

// Button sizes
<Button size="default">Default</Button>
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
<Button size="icon"><Icon /></Button>
```

---

## 🔧 Customization

### Extending Components

```tsx
// Custom variant
import { buttonVariants } from "@/components/ui/button"
import { cva } from "class-variance-authority"

const myButtonVariants = cva(
  buttonVariants.base,
  {
    variants: {
      ...buttonVariants.variants,
      custom: "bg-gradient-to-r from-purple-500 to-pink-500"
    }
  }
)
```

### Custom Styling

```tsx
// Using className
<Dialog>
  <DialogContent className="max-w-3xl">
    {/* Wide dialog */}
  </DialogContent>
</Dialog>

// Using inline styles
<Skeleton 
  className="h-20" 
  style={{ animationDuration: '1.5s' }}
/>
```

---

## ♿ Accessibility

All components follow WAI-ARIA guidelines:

- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: Proper ARIA labels and roles
- **Focus Management**: Visible focus indicators
- **Color Contrast**: WCAG AA compliant

### ARIA Examples

```tsx
// Dialog with proper ARIA
<Dialog>
  <DialogTrigger aria-label="Open settings">
    <Settings />
  </DialogTrigger>
  <DialogContent aria-describedby="dialog-description">
    <DialogTitle>Settings</DialogTitle>
    <DialogDescription id="dialog-description">
      Manage your account settings
    </DialogDescription>
  </DialogContent>
</Dialog>

// Select with proper labels
<Label htmlFor="account-select">Select Account</Label>
<Select>
  <SelectTrigger id="account-select" aria-label="Account selection">
    <SelectValue placeholder="Choose account" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="checking">Checking</SelectItem>
  </SelectContent>
</Select>
```

---

## 🧪 Testing Components

### Unit Test Example

```typescript
import { render, screen } from '@testing-library/react'
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog'

describe('Dialog', () => {
  it('should open on trigger click', async () => {
    const user = userEvent.setup()
    
    render(
      <Dialog>
        <DialogTrigger>Open</DialogTrigger>
        <DialogContent>Dialog content</DialogContent>
      </Dialog>
    )
    
    await user.click(screen.getByText('Open'))
    expect(screen.getByText('Dialog content')).toBeVisible()
  })
})
```

### E2E Test Example

```typescript
test('select should change value', async ({ page }) => {
  await page.click('[data-testid="account-select"]')
  await page.click('text=Savings')
  
  await expect(page.locator('[data-testid="account-select"]'))
    .toContainText('Savings')
})
```

---

## 📦 Component Exports

All components are exported from their respective files:

```typescript
// Dialog
export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogClose,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
}

// Select
export {
  Select,
  SelectGroup,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectLabel,
  SelectItem,
  SelectSeparator,
}

// Tabs
export {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
}

// Skeleton
export { Skeleton }

// Table
export {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableHead,
  TableRow,
  TableCell,
  TableCaption,
}
```

---

## 🔄 Migration Guide

### Updating Existing Components

If you have components using placeholder dialogs/selects:

**Before**:
```tsx
// Old modal implementation
<div className="modal">
  <div className="modal-content">
    {/* content */}
  </div>
</div>
```

**After**:
```tsx
// New Dialog component
<Dialog>
  <DialogTrigger asChild>
    <Button>Open</Button>
  </DialogTrigger>
  <DialogContent>
    {/* content */}
  </DialogContent>
</Dialog>
```

---

## 🚀 Performance Tips

1. **Use Skeleton for Loading States**: Better UX than spinners
2. **Lazy Load Heavy Components**: Use `React.lazy()` for large dialogs
3. **Memoize Table Rows**: Use `React.memo()` for large tables
4. **Virtual Scrolling**: For tables with 100+ rows, use virtual scrolling

```tsx
// Memoized table row
const TableRow = React.memo(({ transaction }) => (
  <tr>
    <td>{transaction.description}</td>
    <td>{transaction.amount}</td>
  </tr>
))
```

---

## 🐛 Common Issues

### Dialog Not Opening

**Issue**: Dialog doesn't open when trigger is clicked  
**Solution**: Ensure `DialogTrigger` has `asChild` prop if wrapping a component

```tsx
// ✅ Correct
<DialogTrigger asChild>
  <Button>Open</Button>
</DialogTrigger>

// ❌ Wrong
<DialogTrigger>
  <Button>Open</Button>
</DialogTrigger>
```

### Select Not Updating

**Issue**: Select value doesn't update in controlled form  
**Solution**: Use `onValueChange` instead of `onChange`

```tsx
// ✅ Correct
<Select onValueChange={setValue} value={value}>

// ❌ Wrong
<Select onChange={setValue} value={value}>
```

### Table Overflow

**Issue**: Table content overflows container  
**Solution**: Table component includes responsive wrapper by default

```tsx
// Already wrapped in overflow-auto div
<Table>
  {/* content */}
</Table>
```

---

## 📚 Additional Resources

- [Radix UI Documentation](https://radix-ui.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [WAI-ARIA Best Practices](https://www.w3.org/WAI/ARIA/apg/)

---

## ✅ Component Checklist

- [x] Button
- [x] Card
- [x] Input
- [x] Label
- [x] Avatar
- [x] Badge
- [x] Separator
- [x] Dropdown Menu
- [x] Dialog ✅ NEW
- [x] Select ✅ NEW
- [x] Tabs ✅ NEW
- [x] Skeleton ✅ NEW
- [x] Table ✅ NEW

**Status**: All core UI components implemented! 🎉

---

**Last Updated**: 2025-01-17  
**Version**: 1.0.0  
**Maintainer**: IOB MAIIS Team