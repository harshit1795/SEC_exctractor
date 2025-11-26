# 🚀 Phase 3 Migration Plan - Next.js Frontend

**Goal**: Migrate all Streamlit features to Next.js with 100% functional parity

---

## 📊 Streamlit App Structure Analysis

### **Main Pages** (4)
1. **Dashboard** - Financial analysis with 8 tabs
2. **Financial Health Monitoring** - Health scores with 2 tabs
3. **Nexus** - Social features with 4 tabs
4. **Settings** - User preferences

### **Dashboard Tabs** (8)
1. Metrics Trend Analysis - Time series charts
2. Snapshot & Changes - Period comparisons
3. Earning Summary - EPS trends
4. Price Chart - Stock price with technical indicators
5. Disclosures - SEC filings (10-K/10-Q)
6. Macroeconomic Data - FRED indicators
7. FinQ 360 - Custom multi-metric charts
8. FinQ Bot - AI chat interface

### **Nexus Tabs** (4)
1. Feed - Social feed
2. My Profile - User profile
3. User Directory - Browse users
4. Friends - Friend management

---

## 🏗️ Next.js Project Structure

```
finq-frontend/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home/Login
│   ├── dashboard/
│   │   ├── page.tsx            # Dashboard main
│   │   └── [ticker]/
│   │       └── page.tsx        # Ticker-specific view
│   ├── health/
│   │   └── page.tsx            # Financial Health Monitoring
│   ├── nexus/
│   │   ├── page.tsx            # Nexus main (Feed)
│   │   ├── profile/
│   │   │   └── page.tsx        # My Profile
│   │   ├── directory/
│   │   │   └── page.tsx        # User Directory
│   │   └── friends/
│   │       └── page.tsx        # Friends
│   └── settings/
│       └── page.tsx            # Settings
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx          # Navigation sidebar
│   │   └── Header.tsx           # Top header
│   ├── dashboard/
│   │   ├── TickerSelector.tsx
│   │   ├── CompanyHeader.tsx
│   │   ├── TrendTab.tsx
│   │   ├── SnapshotTab.tsx
│   │   ├── EarningsTab.tsx
│   │   ├── PriceChartTab.tsx
│   │   ├── DisclosuresTab.tsx
│   │   ├── FredTab.tsx
│   │   ├── FinQ360Tab.tsx
│   │   └── ChatbotTab.tsx
│   ├── nexus/
│   │   ├── Feed.tsx
│   │   ├── PostCard.tsx
│   │   ├── Profile.tsx
│   │   ├── Directory.tsx
│   │   └── Friends.tsx
│   ├── charts/
│   │   ├── LineChart.tsx
│   │   ├── BarChart.tsx
│   │   ├── PriceChart.tsx
│   │   └── MultiMetricChart.tsx
│   └── shared/
│       ├── AuthGuard.tsx
│       ├── Loading.tsx
│       └── ErrorBoundary.tsx
├── lib/
│   ├── firebase.ts              # Firebase config
│   ├── api.ts                   # API client
│   ├── utils.ts                 # Utilities
│   └── hooks/
│       ├── useAuth.ts
│       ├── useTickerData.ts
│       └── useChat.ts
├── types/
│   └── index.ts                 # TypeScript types
└── public/
    └── FInQLogo.png
```

---

## 📋 Migration Checklist

### **Phase 3.1: Foundation** (Week 1)
- [x] Next.js project setup
- [ ] Firebase Authentication integration
- [ ] API client setup
- [ ] Layout components (Sidebar, Header)
- [ ] Routing structure
- [ ] Auth guard

### **Phase 3.2: Dashboard Core** (Week 2)
- [ ] Ticker selector with search
- [ ] Company header with logo
- [ ] Category filter
- [ ] Tab navigation
- [ ] Data fetching hooks

### **Phase 3.3: Dashboard Tabs** (Week 3-4)
- [ ] Metrics Trend Analysis tab
- [ ] Snapshot & Changes tab
- [ ] Earning Summary tab
- [ ] Price Chart tab (with indicators)
- [ ] Disclosures tab
- [ ] Macroeconomic Data tab
- [ ] FinQ 360 tab
- [ ] FinQ Bot tab

### **Phase 3.4: Other Pages** (Week 5)
- [ ] Financial Health Monitoring
- [ ] Nexus Community (all tabs)
- [ ] Settings page

### **Phase 3.5: Polish** (Week 6)
- [ ] Responsive design
- [ ] Loading states
- [ ] Error handling
- [ ] User preferences
- [ ] Testing

---

## 🎯 Key Features to Migrate

### **Dashboard Features**
1. **Ticker Selection**
   - Search by company name or ticker
   - Dropdown with filtered results
   - Default to AAPL

2. **Company Header**
   - Logo from Parqet API
   - Company name, sector, industry
   - Sticky header

3. **Tab Navigation**
   - 8 tabs with icons
   - Active state
   - Tab content switching

4. **Charts**
   - Altair → Recharts migration
   - Interactive charts
   - Zoom, pan, tooltips
   - Multiple chart types (Line, Bar)

5. **Data Tables**
   - Sortable tables
   - Pagination
   - Formatting (human-readable numbers)

6. **Filters**
   - Date range pickers
   - Aggregation options (Monthly, Quarterly, Yearly)
   - Metric selection (multiselect)
   - Chart type selection

### **Nexus Features**
1. **Feed**
   - Post creation
   - Like/unlike
   - Comments
   - Real-time updates (WebSocket)

2. **Profile**
   - Edit profile
   - Avatar upload
   - Display name, bio

3. **Directory**
   - User search
   - Profile cards
   - Friend request button

4. **Friends**
   - Incoming/outgoing requests
   - Accept/reject
   - Friends list

### **Settings Features**
1. **API Keys**
   - Gemini API key
   - FRED API key
   - Polygon API key
   - Save preferences

---

## 🔧 Technology Stack

### **Frontend**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Recharts (charts)
- React Query (data fetching)
- Firebase Auth

### **Charts**
- Recharts (replacing Altair)
- Custom chart components

### **State Management**
- React Query (server state)
- React Context (auth, user prefs)
- Local state (UI state)

### **API Integration**
- Axios for HTTP
- WebSocket for real-time
- React Query hooks

---

## 📝 Implementation Order

1. **Setup & Auth** (Day 1-2)
   - Project structure
   - Firebase integration
   - Auth flow
   - Layout components

2. **Dashboard Foundation** (Day 3-4)
   - Ticker selector
   - Company header
   - Tab navigation
   - Data fetching

3. **Dashboard Tabs** (Day 5-10)
   - Start with simpler tabs
   - Progress to complex ones
   - Test each tab

4. **Other Pages** (Day 11-12)
   - Health Monitoring
   - Nexus
   - Settings

5. **Polish & Test** (Day 13-14)
   - Responsive design
   - Error handling
   - User testing

---

## ✅ Success Criteria

- [ ] All 4 main pages working
- [ ] All 8 dashboard tabs functional
- [ ] All 4 nexus tabs working
- [ ] Charts match Streamlit functionality
- [ ] Data matches Streamlit output
- [ ] Responsive on mobile
- [ ] Fast loading times
- [ ] Error handling in place

---

**Starting migration now!** 🚀

