# 🎤 DEMO SCRIPT (2 minutes)

## Slide 1: The Problem (15 sec)
> "Every year, billions in personal items go unprotected.
> When something breaks, the claims process takes weeks.
> We built an app that does it in **seconds**."

## Slide 2: The Solution (15 sec)
> "Our app lets you protect any item instantly,
> file a claim by snapping your receipt,
> and get approved with AI-powered OCR — **all in real-time**."

---

## LIVE DEMO (90 sec)

### Act 1: Protect (20 sec)
*[Show phone - Uninsured Screen]*
> "I have an unprotected iPhone worth $999.
> One tap — and I'm covered."
*[Tap "Protect My Item" → screen transitions to Protected]*

### Act 2: File Claim (20 sec)
*[Show phone - Protected Screen]*
> "Let's say my screen cracked. I have a repair receipt."
*[Tap "Submit Claim" → screen shows Processing]*

### Act 3: Real-Time Processing (20 sec)
*[P4 fires curl webhook from laptop]*
> "Watch this — our backend receives the receipt,
> runs OCR to extract the total,
> verifies coverage, and calculates the payout."
*[Processing animation plays → WebSocket pushes update]*

### Act 4: Approved! (15 sec)
*[Phone auto-navigates to Approved screen]*
> "Approved! $382.50 payout — 85% coverage,
> processed in under 5 seconds.
> No paperwork. No waiting. Just instant protection."

### Closing (15 sec)
> "We built this in 24 hours with FastAPI, React Native,
> MongoDB Atlas, WebSockets for real-time updates,
> and Tesseract OCR. Thank you!"

---

## TECH STACK SUMMARY (if asked)
- **Backend**: FastAPI + 3 REST routes + WebSocket
- **Database**: MongoDB Atlas (1 collection)
- **Mobile**: React Native (Expo) — 4 screens
- **AI**: Tesseract OCR + regex parsing
- **Deploy**: Railway (auto-deploy from GitHub)
- **Real-time**: WebSocket push notifications