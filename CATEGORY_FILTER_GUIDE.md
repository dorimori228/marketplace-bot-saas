# Category Filter & Relist Guide

## Overview

The bot UI now includes a powerful **category-based filtering and relisting system** that allows you to organize and relist your listings based on their categories.

## Features

### 🎯 Category Filter

Located in the "Relist Existing Listings" section, you can now:

1. **Filter by Category**: Select a category from the dropdown to view only listings in that category
2. **View All**: Select "All Categories" to see all your listings
3. **Real-time Stats**: See how many listings are in each category

### 📊 Category Statistics

The stats bar shows you:
- **All Categories View**: Total listing count + breakdown by category
  - Example: `📊 15 total listings | Other Garden decor: 10 | Other Rugs & carpets: 5`
  
- **Filtered View**: Number of listings in the selected category
  - Example: `📊 Showing 10 of 15 listings in category: Other Garden decor`

### ✅ Category-Aware Selection

When you filter by category:
- **Select All** button selects all listings in the current category
- **Selected count** shows which category your selections are from
- **Relist button** updates to show the category context

## How to Use

### Relisting by Category

1. **Select an Account**
   - Choose your account from the dropdown in the left section
   - Your listings will load automatically

2. **Filter by Category**
   - In the "Relist Existing Listings" section, select a category from the dropdown
   - Options:
     - `All Categories` - Shows all listings
     - `Other Garden decor` - Artificial Grass & Decking listings
     - `Other Rugs & carpets` - Carpet listings

3. **View Filtered Listings**
   - The list will update to show only listings in the selected category
   - Each listing displays its category with a 📁 icon
   - Stats bar shows how many listings are being displayed

4. **Select Listings to Relist**
   - **Option 1**: Manually check boxes next to listings you want
   - **Option 2**: Click "☑️ Select All" to select all listings in the current category
   - **Option 3**: Click "☐ Deselect All" to clear your selections

5. **Relist Selected**
   - Click the "🔄 Relist Selected" button
   - If filtering by category, the button shows: "🔄 Relist Selected (Category Name)"
   - The bot will process all selected listings in sequence

### Example Workflows

#### Workflow 1: Relist All Artificial Grass Listings

```
1. Select Account: "MyAccount"
2. Filter by Category: "Other Garden decor"
   → Stats show: "📊 Showing 10 of 15 listings in category: Other Garden decor"
3. Click "☑️ Select All"
   → Status: "Selected all 10 listings in category: Other Garden decor"
4. Click "🔄 Relist Selected (Other Garden decor)"
   → Bot processes all 10 listings
```

#### Workflow 2: Relist Specific Carpet Listings

```
1. Select Account: "MyAccount"
2. Filter by Category: "Other Rugs & carpets"
   → Stats show: "📊 Showing 5 of 15 listings in category: Other Rugs & carpets"
3. Manually select 3 specific listings
   → Count shows: "3 listings selected (Other Rugs & carpets)"
4. Click "🔄 Relist Selected (Other Rugs & carpets)"
   → Bot processes the 3 selected listings
```

#### Workflow 3: Review All Listings, Relist by Category

```
1. Select Account: "MyAccount"
2. Keep filter on: "All Categories"
   → Stats show: "📊 15 total listings | Other Garden decor: 10 | Other Rugs & carpets: 5"
3. Review all listings, note which categories need relisting
4. Change filter to: "Other Garden decor"
5. Select all and relist
6. Change filter to: "Other Rugs & carpets"
7. Select all and relist
```

## Visual Indicators

### Listing Display

Each listing now shows:
```
[Checkbox] [Image Preview]
  Title: Premium Artificial Grass 4m x 2m
  Price: £150
  📁 Other Garden decor
  Created: 1/5/2025 | Status: active
  [Edit ✏️] [Delete 🗑️]
```

### Stats Bar Examples

**All Categories:**
```
📊 15 total listings | Other Garden decor: 10 | Other Rugs & carpets: 5
```

**Filtered by Category:**
```
📊 Showing 10 of 15 listings in category: Other Garden decor
```

### Selection Counter

**No Filter:**
```
5 listings selected
```

**With Category Filter:**
```
5 listings selected (Other Garden decor)
```

### Relist Button

**No Filter:**
```
🔄 Relist Selected
```

**With Category Filter:**
```
🔄 Relist Selected (Other Garden decor)
```

## Benefits

### Organization
- ✅ Easily find listings by type (artificial grass vs carpets)
- ✅ See at a glance how many listings you have in each category
- ✅ Keep your inventory organized

### Efficiency
- ✅ Relist all items of one type with 2 clicks
- ✅ Focus on specific product categories
- ✅ Avoid accidentally relisting wrong products

### Control
- ✅ Clear visual feedback on what you're about to relist
- ✅ Category context shown in buttons and counters
- ✅ Prevents mistakes when managing multiple product types

## Tips & Best Practices

### 1. Use Category Filter for Bulk Operations
- When you want to relist all artificial grass listings, filter by "Other Garden decor"
- When you want to relist all carpet listings, filter by "Other Rugs & carpets"

### 2. Review Before Relisting
- Check the stats bar to confirm the number of listings in each category
- Verify the selection counter shows the correct count and category
- Review a few listings to ensure they're the right ones

### 3. Maintain Consistent Categories
- Always set the correct category when creating new listings
- This makes filtering and managing listings much easier
- The bot remembers your last selected category for convenience

### 4. Sequential Relisting
- The bot processes listings one at a time
- You'll see progress updates in the console
- Don't close the browser until all listings are processed

### 5. Organize Your Strategy
- Relist artificial grass listings on certain days
- Relist carpet listings on other days
- Use category filtering to implement this schedule easily

## Keyboard Shortcuts

While there are no dedicated keyboard shortcuts, you can:
- Press `Tab` to navigate between filter dropdown and checkboxes
- Press `Space` to toggle checkboxes
- Press `Enter` when focused on "Relist Selected" button

## Troubleshooting

### Filter Not Working
- **Issue**: Listings don't change when selecting category
- **Solution**: Refresh the page and try again

### Wrong Listings Showing
- **Issue**: Listings appear in wrong category
- **Solution**: Check the category assigned when the listing was created

### Stats Not Updating
- **Issue**: Stats bar shows old numbers
- **Solution**: Select a different account and select it again to reload

### No Listings in Category
- **Issue**: "No listings found in category" message
- **Solution**: This means you have no listings in that category. Switch to "All Categories" to see all your listings.

### Selection Cleared When Changing Filter
- **Issue**: Checkboxes unchecked when changing category
- **Solution**: This is intentional behavior to prevent accidentally relisting wrong items. Make selections after filtering.

## Future Enhancements

Potential future features:
- 🔮 Custom categories
- 🔮 Multi-category selection
- 🔮 Category-based templates
- 🔮 Category statistics dashboard
- 🔮 Scheduled category-based relisting

## Support

If you encounter any issues with the category filter:
1. Check the browser console for error messages
2. Verify listings have categories assigned
3. Refresh the page to reset the filter
4. Review this guide for proper usage

---

**Last Updated**: January 2025

