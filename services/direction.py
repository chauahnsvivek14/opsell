def classify_market(open_price, current_price, vix_open, vix_now, straddle_open, straddle_now):
    
    # Price movement %
    price_move_pct = ((current_price - open_price) / open_price) * 100
    
    # VIX change
    vix_change = vix_now - vix_open
    
    # Premium decay %
    premium_change_pct = ((straddle_now - straddle_open) / straddle_open) * 100

    # --- Classification Logic ---
    
    # OPTION SELLER DAY
    if abs(price_move_pct) < 0.4 and vix_change < -0.5 and premium_change_pct < -20:
        return "🟢 OPTION SELLER DAY (Range + Decay)"
    
    # OPTION BUYER DAY
    elif abs(price_move_pct) > 0.7 and vix_change > 0.5 and premium_change_pct > -10:
        return "🔴 OPTION BUYER DAY (Trending / Expansion)"
    
    # MIXED DAY
    else:
        return "🟡 MIXED / TRAP DAY (Avoid aggressive trades)"


# Example usage:
result = classify_market(
    open_price=23945.45,
    current_price=24040.25,
    vix_open=19.3,
    vix_now=18.97,
    straddle_open=241.35,
    straddle_now=235.85
)

print(result)
