from playwright.sync_api import sync_playwright
import time

# Read tokens from auth.txt
def load_tokens():
    with open("tokens.txt", "r") as file:
        return [line.strip() for line in file.readlines() if line.strip()]

# Function to get coin balance
def get_coin_balance(page):
    try:
        balance_text = page.text_content("span._amount_1wzqv_81")
        balance = int(balance_text.replace(",", ""))
        print(f"[💰] Coin Balance: {balance}")
        return balance
    except:
        print("[❌] Failed to fetch coin balance.")
        return 0

# Function to get remaining taps
def get_remaining_taps(page):
    try:
        energy_bar = page.query_selector("div._progress_15n79_16")
        if energy_bar:
            style_attr = energy_bar.get_attribute("style")
            if "width" in style_attr:
                energy_percent = float(style_attr.split("width: ")[1].split("%")[0])
                remaining_taps = int((energy_percent / 100) * 1000)  # Convert percent to taps (total 1000 taps)
                return remaining_taps
    except:
        print("[❌] Failed to fetch remaining taps.")
    return 0  # If it fails, return 0 to prevent infinite clicking

# Function to automate tapping
def auto_tap(page):
    tap_area_selector = "div._tapArea_njdmz_15"
    print("[🎯] Starting tapping at 25 taps per second...")
    
    while True:
        remaining_taps = get_remaining_taps(page)
        if remaining_taps < 200:  # Stop if remaining taps are below 200
            print("[⚠️] Remaining taps below 200! Stopping taps.")
            break

        start_time = time.time()
        click_count = 0
        
        while time.time() - start_time < 1:  # Clicks per second
            page.click(tap_area_selector)
            click_count += 1
            if click_count >= 25:
                break

# Function to process one token at a time
def process_token(token):
    with sync_playwright() as p:
        print("[🚀] Launching Chromium...")

        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--disable-extensions"]
        )  
        context = browser.new_context()
        page = context.new_page()

        # Open the game website
        url = "https://telegram.geagle.online"
        page.goto(url)
        print("[✅] Website loaded!")

        # Inject token into local storage as session_token (masked for security)
        masked_token = token[:4] + "..." + token[-4:]  # Show only first and last 4 characters
        page.evaluate(f"localStorage.setItem('session_token', '{token}');")
        print(f"[🔑] Token injected as session_token: {masked_token}")

        # Reload the page to apply authentication
        page.reload()
        print("[🔄] Page reloaded with token!")

        # Fetch Coin Balance
        get_coin_balance(page)

        # Perform tapping while remaining taps > 200
        auto_tap(page)

        # Refresh the browser before closing
        page.reload()
        print("[🔄] Page refreshed before closing!")

        # Close browser
        browser.close()
        print("[🚪] Browser closed!\n")

# Main function to run for all tokens
def main():
    while True:  # Infinite loop
        tokens = load_tokens()
        if not tokens:
            print("[❌] No tokens found in auth.txt! Exiting.")
            break

        for token in tokens:
            process_token(token)  # Process each token

        print("[⏳] Resting for 1 minute before next cycle...")
        time.sleep(60)  # Wait 1 minute before restarting the cycle

# Run the script
if name == "main":
    main()
