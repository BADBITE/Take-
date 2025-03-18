import os
import random
import requests
import asyncio
from playwright.async_api import Playwright, async_playwright
from colorama import Fore, Style, init

# Initialize the colorama library
init(autoreset=True)

def read_file_to_list(filename):
    """Read the content from a text file and return it as a list."""
    with open(filename, 'r') as file:
        return [line.strip().strip('"') for line in file if line.strip()]  # Remove quotes

# Read tokens and user agents from files
tokens = read_file_to_list('tokens.txt')
user_agents = read_file_to_list('user_agents.txt')

def print_futuristic_banner():
    print(Fore.CYAN + "🚀 Welcome to the Futuristic Bot! 🚀" + Style.RESET_ALL)

def print_token_divider(number):
    print(f"\n{Fore.BLUE}{Style.BRIGHT}♫ {'Token'.ljust(15)} [{Fore.GREEN}#{number}{Fore.BLUE}] {'♫'.rjust(35)}")

async def run(playwright, user_agent, token, token_number, headless):
    browser = await playwright.chromium.launch(headless=headless)
    context = await browser.new_context(
        viewport={"width": 375, "height": 667},
        has_touch=True,
        is_mobile=True,
    )

    try:
        page = await context.new_page()
        await page.goto(
            f"https://telegram.geagle.online/wallet/?auth={token}",
            timeout=60000,
            wait_until="networkidle"
        )
        await page.wait_for_timeout(3000)
        await page.goto("https://telegram.geagle.online/", wait_until="domcontentloaded")

        await page.locator("._button_gp2y8_39 > svg > path").first.click(
            timeout=20000,
            delay=random.randint(200, 800)
        )
        await page.wait_for_timeout(3000)

        total_clicks = 0

        while total_clicks < 500:
            clicks = [(random.randint(40, 320), random.randint(333, 530)) for _ in range(3)]

            for x, y in clicks:
                await page.mouse.click(x, y, click_count=2)
                total_clicks += 1

            if total_clicks >= 500:
                break

            if total_clicks % 100 == 0 and total_clicks > 0:
                wait_time = random.randint(2000, 3000)
                print(f"Waiting for {wait_time / 1000} seconds...")
                await page.wait_for_timeout(wait_time)

        print(f"Successfully reached {total_clicks} clicks!")

        for i in range(3):
            headers = {
                'authority': 'gold-eagle-api.fly.dev',
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US;q=0.8,en;q=0.7',
                'authorization': f'Bearer {token}',
                'origin': 'https://telegram.geagle.online',
                'referer': 'https://telegram.geagle.online/',
                'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': user_agent,
            }

            response = requests.get('https://gold-eagle-api.fly.dev/user/me/progress', headers=headers)

            if response.status_code == 200:
                cleaned_data = response.json()
                cleaned_data.pop('max_energy', None)
                cleaned_data.pop('not_registered_events_count', None)

                print(f"\n⚡️ Request #{i+1} Status: SUCCESS ✅")
                print(f"»» TOKEN #{token_number} ««")
                print(f"🆔 ID: {cleaned_data.get('id', '')}")
                print(f"🔋 Energy: {cleaned_data.get('energy', 0)}")
                print(f"🚀 XP: {cleaned_data.get('experience', 0)}")
                print("────────────────────────────────────────────────────")
            else:
                print(f"\n🔥 Request #{i+1} Status: FAILED 🚨")
                print(f"📛 Error Code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await context.close()
        await browser.close()

async def run_with_sem(sem, user_agent, token, token_number, headless):
    async with sem:
        async with async_playwright() as playwright:
            await run(playwright, user_agent, token, token_number, headless)

async def main():
    print_futuristic_banner()
    headless_input = input("Would you like to run the browser in headless mode? (yes/no): ").strip().lower()
    headless = headless_input in ['yes']

    token_counter = 1
    sem = asyncio.Semaphore(1)  # Set the number of concurrent operations (4 here)

    while True:
        tasks = []
        for idx, token in enumerate(tokens):
            print_token_divider(token_counter)
            user_agent = user_agents[idx % len(user_agents)]
            tasks.append(run_with_sem(sem, user_agent, token, token_counter, headless))
            token_counter += 1

        await asyncio.gather(*tasks)  # Run all tasks concurrently

        print("🌀 System Recharging... (Next cycle in 5 minutes) ⏳")
        await asyncio.sleep(10)  # Wait for 5 minutes

if __name__ == "__main__":
    asyncio.run(main())
