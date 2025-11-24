# 🏑 START HERE - ZHC Heating Scheduler

**Welcome!** This is your complete Home Assistant integration for automating the Zandvoortsche Hockey Club heating system.

## 🎯 What You Have

A **production-ready** Home Assistant custom integration that:
- ✅ Scrapes training schedules from https://www.zandvoortschehockeyclub.nl/trainingsschema
- ✅ Scrapes match schedules from https://www.zandvoortschehockeyclub.nl/wedstrijdschema
- ✅ Automatically heats the building before events
- ✅ Includes smart pre-heat and cool-down
- ✅ Works with Plugwise SA thermostats
- ✅ Has a custom scraper for the LISA system used by ZHC
- ✅ Includes comprehensive tests and documentation

## 🚀 Quick Start (3 Steps)

### Step 1: Test the Scraper (5 minutes)

**This is the most important step!** The ZHC website uses JavaScript to load schedules, so we need to verify the scraper works:

```bash
cd /path/to/zhc-heating-scheduler
python test_zhc_scraper.py
```

**What to expect:**

✅ **Best case**: You see events listed
```
Found 25 events from ZHC (next 14 days)
📅 Training events: 18  
🏑 Match events: 7
```
→ **Great!** Skip to Step 2.

⚠️ **Likely case**: No events found
```
WARNING: No events found!
```
→ **Don't worry!** This means you need to find the API endpoint. Follow the instructions in the test output, or see [ZHC_SETUP_GUIDE.md](ZHC_SETUP_GUIDE.md) section "If No Events Are Found".

**Quick fix**: 
1. Open https://www.zandvoortschehockeyclub.nl/trainingsschema in Chrome/Firefox
2. Press F12 → Network tab
3. Reload the page
4. Look for API calls (XHR/Fetch)
5. Find the one loading schedule data
6. Note the URL and update `zhc_custom_scraper.py` (line ~56)

### Step 2: Integrate the Scraper (2 minutes)

If the test found events, integrate it:

**Edit `coordinator.py`:**
```python
# Line 12: Add this import
from .zhc_custom_scraper import ZHCCustomScraper

# Line ~50: Replace the scraper initialization with:
self.scraper = ZHCCustomScraper(
    training_url=schedule_url,
    match_url="https://www.zandvoortschehockeyclub.nl/wedstrijdschema",
    session=self._session
)
```

Full instructions: [INTEGRATING_ZHC_SCRAPER.md](INTEGRATING_ZHC_SCRAPER.md)

### Step 3: Install in Home Assistant (5 minutes)

```bash
# Copy to Home Assistant
cp -r custom_components/zhc_heating_scheduler ~/.homeassistant/custom_components/

# Restart Home Assistant
```

Then:
1. Go to Settings → Devices & Services
2. Add Integration → "ZHC Heating Scheduler"
3. Configure:
   - URL: `https://www.zandvoortschehockeyclub.nl/trainingsschema`
   - Climate: Your Plugwise entity
   - Enable **dry run mode** ✅
4. Click Submit

**Verify it works:**
```yaml
# Developer Tools → Services
service: zhc_heating_scheduler.refresh_schedule
```

Check logs for: "Found X events"

## 📚 Documentation

| Document | When to Use |
|----------|-------------|
| **[ZHC_IMPLEMENTATION_SUMMARY.md](ZHC_IMPLEMENTATION_SUMMARY.md)** | Overview of what was built and why |
| **[ZHC_SETUP_GUIDE.md](ZHC_SETUP_GUIDE.md)** | Complete setup guide with troubleshooting |
| **[INTEGRATING_ZHC_SCRAPER.md](INTEGRATING_ZHC_SCRAPER.md)** | Technical integration details |
| **[README.md](README.md)** | Full integration documentation |
| **[QUICK_START.md](QUICK_START.md)** | General quick start guide |
| **test_zhc_scraper.py** | Test script - **Run this first!** |

## ⚡ TL;DR - Absolutely Minimum Steps

```bash
# 1. Test
python test_zhc_scraper.py

# 2. If events found, edit coordinator.py (see Step 2 above)

# 3. Install
cp -r custom_components/zhc_heating_scheduler ~/.homeassistant/custom_components/

# 4. Restart Home Assistant

# 5. Add integration via UI
```

## 🔍 What If It Doesn't Work?

### Problem: Test script finds no events

**Solution**: You need to find the API endpoint the website uses.

**How**:
1. Open ZHC schedule page in browser
2. F12 → Network tab → Reload
3. Find XHR/Fetch request with schedule data
4. Update `zhc_custom_scraper.py` with that URL

**Detailed guide**: [ZHC_SETUP_GUIDE.md](ZHC_SETUP_GUIDE.md) → "If No Events Are Found"

### Problem: Integration won't load

**Solution**: Check Home Assistant logs for errors

**Common issues**:
- Import error → Verify `zhc_custom_scraper.py` is in the right folder
- Syntax error → Check modifications to `coordinator.py`

### Problem: Events found but wrong times

**Solution**: Check timezone and date format

**Fix**: Update date parsing in scraper to use Dutch format

## 🏗️ Project Structure

```
zhc-heating-scheduler/
├── custom_components/zhc_heating_scheduler/  # The integration
│   ├── zhc_custom_scraper.py    # ⭐ Custom ZHC scraper
│   ├── coordinator.py            # Needs modification (Step 2)
│   └── ... (other integration files)
├── test_zhc_scraper.py          # ⭐ TEST THIS FIRST!
├── ZHC_SETUP_GUIDE.md           # ⭐ Complete ZHC guide
├── INTEGRATING_ZHC_SCRAPER.md   # Integration instructions
└── START_HERE.md                # ⭐ This file
```

## 🎓 Understanding the Flow

```
ZHC Website
    ↓ (JavaScript/API)
Custom ZHC Scraper (test_zhc_scraper.py)
    ↓ (Events)
Scheduler (calculates heating times)
    ↓ (Heating windows)
Coordinator (controls thermostat)
    ↓
Plugwise SA Thermostat
    ↓
🔥 Warm clubhouse!
```

## ✅ Success Checklist

- [ ] Run `test_zhc_scraper.py` 
- [ ] See events in test output (or find API endpoint)
- [ ] Edit `coordinator.py` to use ZHC scraper
- [ ] Copy to Home Assistant
- [ ] Add integration via UI
- [ ] See schedule in sensors
- [ ] Verify heating control in dry run mode
- [ ] Disable dry run, go live!
- [ ] Create dashboard card
- [ ] Set up notifications (optional)

## 🆘 Need Help?

1. **Read**: [ZHC_SETUP_GUIDE.md](ZHC_SETUP_GUIDE.md) has detailed troubleshooting
2. **Test**: Run `test_zhc_scraper.py` and follow its output
3. **Check**: Browser DevTools Network tab for API endpoints
4. **Ask**: Create GitHub issue with test output and logs

## 🎯 Your Next Action

```bash
python test_zhc_scraper.py
```

**That's it!** The test script will guide you through the next steps.

---

**Good luck with your ZHC heating automation!** 🏑🔥

P.S. Don't forget to start with **dry run mode enabled** when first testing!

