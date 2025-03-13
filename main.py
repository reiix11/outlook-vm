from colorama   import Fore, init

import aiohttp
import asyncio

import sys
import os
import re

init(autoreset=True)

valid = 0
taken = 0
check = 0

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

def print_progress():
    sys.stdout.write(f"\rChecked: {check} | {Fore.GREEN}Valid: {valid}{Fore.RESET} | {Fore.RED}Taken: {taken}{Fore.RESET}")
    sys.stdout.flush()

async def get_cookies(session):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Host": "login.live.com",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "Sec-GPC": "1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:119.0) Gecko/20100101 Firefox/119.0"
    }
    
    async with session.get("https://login.live.com/", headers=headers) as response:
        text = await response.text()
        flow_token = re.search(r'name="PPFT".*?value="([^"]*)"', text).group(1)
        uaid = text.split("uaid=")[1].split('"')[0]
        return flow_token, uaid

async def check_email(session, email, flow_token, uaid):
    headers = {
        "Accept": "application/json",
        "Content-type": "application/json; charset=utf-8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Host": "login.live.com",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "Sec-GPC": "1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:119.0) Gecko/20100101 Firefox/119.0"
    }
    
    payload = {
        "checkPhones": True,
        "country": "",
        "federationFlags": 3,
        "flowToken": flow_token,
        "uaid": uaid,
        "username": email,
        "isSignup": False
    }
    
    async with session.post("https://login.live.com/GetCredentialType.srf", json=payload, headers=headers) as response:
        return await response.json()

async def process_email(session, email, semaphore):
    global taken, valid, check
    async with semaphore:
        flow_token, uaid = await get_cookies(session)
        res = await check_email(session, email, flow_token, uaid)
        check += 1
        if res.get("IfExistsResult") == 0:
            valid += 1
            with open("valid.txt", "a") as f:
                f.write(f"{email}\n")
        else:
            taken += 1
        
        print_progress()

async def main():
    clear()
    threads = int(input(f"[{Fore.CYAN}>{Fore.RESET}] Enter Threads {Fore.LIGHTBLACK_EX}(50 recommended){Fore.RESET}: "))
    clear()
    semaphore = asyncio.Semaphore(threads)

    async with aiohttp.ClientSession() as session:
        with open("emails.txt", "r") as f:
            emails = f.read().splitlines()

        tasks = [process_email(session, email, semaphore) for email in emails]
        await asyncio.gather(*tasks)
    
    print("\nDone.")

if __name__ == "__main__":
    try:
        clear()
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt")
        sys.exit(0)
