#!/bin/bash
# ============================================
# P4 - Demo Webhook Script
# Fires during live demo to trigger claim flow
# ============================================

# Configuration - UPDATE THESE
BASE_URL="https://your-app.up.railway.app"
USER_ID="demo_user_001"

echo "🚀 Insurance App - Live Demo Webhook"
echo "======================================"
echo "Server: $BASE_URL"
echo ""

# ── Step 1: Health Check ────────────────────
echo "1️⃣  Checking server health..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

# ── Step 2: Create a Claim ──────────────────
echo "2️⃣  Creating insurance claim..."
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/claims" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"item_name\": \"iPhone 15 Pro\",
    \"item_value\": 999.99,
    \"description\": \"Brand new phone - hackathon demo\"
  }")

echo "$CREATE_RESPONSE" | python3 -m json.tool

# Extract claim ID
CLAIM_ID=$(echo "$CREATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['claim']['id'])" 2>/dev/null)

if [ -z "$CLAIM_ID" ]; then
  echo "❌ Failed to create claim"
  exit 1
fi

echo ""
echo "📋 Claim ID: $CLAIM_ID"
echo ""

# ── Step 3: Wait for dramatic effect ────────
echo "3️⃣  Waiting 3 seconds (check mobile screen)..."
sleep 3

# ── Step 4: Submit claim with receipt ────────
echo "4️⃣  Submitting claim with receipt..."
SUBMIT_RESPONSE=$(curl -s -X POST "$BASE_URL/claims/$CLAIM_ID/submit" \
  -F "receipt_total=450.00")

echo "$SUBMIT_RESPONSE" | python3 -m json.tool
echo ""

# ── Step 5: Verify final status ─────────────
echo "5️⃣  Verifying claim status..."
sleep 1
curl -s "$BASE_URL/claims/$CLAIM_ID" | python3 -m json.tool
echo ""

echo "======================================"
echo "✅ Demo complete!"
echo "💰 Payout: \$382.50 (85% of \$450)"
echo "======================================"