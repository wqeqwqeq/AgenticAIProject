#!/usr/bin/env python3
"""
Instagram Picture Downloader with Playwright

This script uses Playwright to simulate a real browser and download Instagram pictures.
This approach is more likely to succeed against Instagram's anti-bot measures.

Usage:
    python instagram_downloader_playwright.py --username grapeot --count 5
    python instagram_downloader_playwright.py --url https://www.instagram.com/grapeot/ --count 10
"""

import argparse
import asyncio
import os
import sys
import time
import aiohttp
from pathlib import Path
from urllib.parse import urlparse, urljoin
from playwright.async_api import async_playwright
import json
from datetime import datetime, timedelta


def extract_username_from_url(url):
    """Extract Instagram username from URL"""
    if url.startswith('https://www.instagram.com/'):
        path = urlparse(url).path
        username = path.strip('/').split('/')[0]
        return username
    return url


async def save_cookies(context, cookie_file="instagram_cookies.json"):
    """
    Save browser cookies to file
    
    Args:
        context: Playwright browser context
        cookie_file: Path to save cookies
    
    Returns:
        bool: Success status
    """
    try:
        cookies = await context.cookies()
        cookie_data = {
            'cookies': cookies,
            'saved_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        with open(cookie_file, 'w') as f:
            json.dump(cookie_data, f, indent=2)
        
        print(f"🍪 Cookies saved to {cookie_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to save cookies: {str(e)}")
        return False


async def load_cookies(context, cookie_file="instagram_cookies.json"):
    """
    Load browser cookies from file
    
    Args:
        context: Playwright browser context
        cookie_file: Path to load cookies from
    
    Returns:
        bool: Success status
    """
    try:
        if not os.path.exists(cookie_file):
            print(f"📄 No cookie file found at {cookie_file}")
            return False
        
        with open(cookie_file, 'r') as f:
            cookie_data = json.load(f)
        
        # Check if cookies are expired
        expires_at = datetime.fromisoformat(cookie_data['expires_at'])
        if datetime.now() > expires_at:
            print(f"⏰ Cookies expired, removing old cookie file")
            os.remove(cookie_file)
            return False
        
        # Load cookies into context
        await context.add_cookies(cookie_data['cookies'])
        
        saved_at = datetime.fromisoformat(cookie_data['saved_at'])
        print(f"🍪 Loaded cookies from {saved_at.strftime('%Y-%m-%d %H:%M')}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to load cookies: {str(e)}")
        return False


def clear_cookies(cookie_file="instagram_cookies.json"):
    """
    Clear saved cookies
    
    Args:
        cookie_file: Path to cookie file
    
    Returns:
        bool: Success status
    """
    try:
        if os.path.exists(cookie_file):
            os.remove(cookie_file)
            print(f"🧹 Cleared cookies from {cookie_file}")
            return True
        else:
            print(f"📄 No cookie file found at {cookie_file}")
            return False
    except Exception as e:
        print(f"❌ Failed to clear cookies: {str(e)}")
        return False


async def download_image(session, url, filepath):
    """Download image from URL using aiohttp"""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                with open(filepath, 'wb') as f:
                    f.write(content)
                return True
    except Exception as e:
        print(f"❌ Failed to download {url}: {str(e)}")
    return False


async def login_to_instagram(page, context, save_cookies_after=True):
    """
    Handle Instagram login process
    
    Args:
        page: Playwright page object
        context: Playwright browser context
        save_cookies_after: Whether to save cookies after successful login
    
    Returns:
        bool: True if login successful, False otherwise
    """
    try:
        print("🔐 Starting Instagram login process...")
        
        # Navigate to Instagram login page
        await page.goto("https://www.instagram.com/accounts/login/", wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(3000)
        
        print("📝 Please log in to your Instagram account in the browser window that opened.")
        print("⏳ Waiting for you to complete the login process...")
        print("   - Enter your username and password")
        print("   - Complete any 2FA if required")
        print("   - Wait for the main Instagram page to load")
        print("   - You'll see a success message when login is detected")
        
        # Wait for login to complete by checking for the main page elements
        login_timeout = 300000  # 5 minutes timeout for manual login
        
        try:
            # Wait for either the home page or profile elements to appear
            await page.wait_for_selector(
                'svg[aria-label="Home"], a[href="/"], nav[role="navigation"]', 
                timeout=login_timeout
            )
            
            # Additional check - make sure we're not still on login page
            current_url = page.url
            if 'login' not in current_url.lower():
                print("✅ Login successful! Detected main Instagram page.")
                await page.wait_for_timeout(2000)  # Wait a bit more for page to stabilize
                
                # Save cookies after successful login
                if save_cookies_after:
                    await save_cookies(context)
                
                return True
            else:
                print("❌ Still on login page. Please complete the login process.")
                return False
                
        except Exception as e:
            print(f"⏰ Login timeout after 5 minutes. Please try again.")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return False


async def scrape_instagram_with_playwright(username, count=5, output_dir="downloads", headless=True, login_first=False, use_cookies=True):
    """
    Use Playwright to scrape Instagram profile pictures
    
    Args:
        username (str): Instagram username
        count (int): Number of posts to download
        output_dir (str): Directory to save downloads
        headless (bool): Run browser in headless mode
    
    Returns:
        tuple: (success, downloaded_count)
    """
    
    # Create output directory
    user_dir = Path(output_dir) / username
    user_dir.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        print("🚀 Launching browser...")
        
        # Launch browser with realistic settings
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security', 
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create context with realistic user agent
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        try:
            # Try to load saved cookies first
            cookies_loaded = False
            if use_cookies:
                cookies_loaded = await load_cookies(context)
            
            # Handle login if requested or if cookies failed to load
            needs_login = login_first or (use_cookies and not cookies_loaded)
            
            if needs_login:
                if cookies_loaded:
                    print("🔄 Cookies loaded but login was explicitly requested")
                login_success = await login_to_instagram(page, context, save_cookies_after=use_cookies)
                if not login_success:
                    print("❌ Login failed or was cancelled. Cannot proceed.")
                    return False, 0
                print("🎉 Login completed! Proceeding with download...")
            elif cookies_loaded:
                print("🍪 Using saved cookies, skipping login!")
            
            print(f"🔍 Navigating to Instagram profile: {username}")
            
            # Navigate to Instagram profile
            profile_url = f"https://www.instagram.com/{username}/"
            print(f"   Loading profile URL: {profile_url}")
            await page.goto(profile_url, wait_until='domcontentloaded', timeout=60000)
            print("   Profile page loaded, waiting for content...")
            await page.wait_for_timeout(5000)
            
            # Try to force "Show All Posts" mode if available
            try:
                # Look for any "Show more" or "View all" buttons
                show_more_buttons = await page.query_selector_all('button:has-text("Show"), button:has-text("More"), button:has-text("View"), a:has-text("Show"), a:has-text("More")')
                for button in show_more_buttons:
                    try:
                        button_text = await button.text_content()
                        if button_text and any(word in button_text.lower() for word in ['show', 'more', 'view', 'all']):
                            print(f"   🔘 Found potential button: {button_text}")
                            await button.click()
                            await page.wait_for_timeout(3000)
                            break
                    except:
                        continue
            except:
                pass  # Give more time for dynamic content
            
            # Wait for page to load
            await page.wait_for_timeout(3000)
            
            # Check if profile exists
            if "Sorry, this page isn't available" in await page.content():
                print(f"❌ Profile '{username}' does not exist or is not accessible")
                return False, 0
            
            # Check if login is required
            if "Log in" in await page.content() and "Sign up" in await page.content():
                print("⚠️  Instagram is requesting login. Trying to continue anyway...")
            
            print("📊 Analyzing profile...")
            
            # Try to get profile info
            try:
                # Look for profile stats
                posts_element = await page.query_selector('a[href*="/p/"] span, span:has-text("posts")')
                if posts_element:
                    posts_text = await posts_element.text_content()
                    print(f"📸 Found profile with posts")
            except:
                pass
            
            # AGGRESSIVE SCROLLING to force Instagram to load ALL content
            print(f"📜 Aggressive scrolling to load posts for {count} images...")
            
            scroll_count = max(20, count // 3)  # Much more aggressive scrolling
            last_valid_count = 0
            stagnant_scrolls = 0
            
            print(f"   Will perform up to {scroll_count} scrolls...")
            
            for i in range(scroll_count):
                print(f"   Scroll {i+1}/{scroll_count}")
                
                # Multiple scroll techniques
                if i % 3 == 0:
                    # Method 1: Scroll to bottom
                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                elif i % 3 == 1:
                    # Method 2: Incremental scroll
                    await page.evaluate('window.scrollBy(0, window.innerHeight)')
                else:
                    # Method 3: Scroll to specific element if possible
                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight - 100)')
                
                # Vary wait times
                wait_time = 2000 if i < 10 else 4000  # Longer waits for later scrolls
                await page.wait_for_timeout(wait_time)
                
                # Try to trigger more loading by moving mouse and interacting
                if i % 5 == 0:
                    try:
                        # Try to hover over elements to trigger loading
                        await page.mouse.move(683, 400)  # Center of viewport
                        await page.wait_for_timeout(500)
                    except:
                        pass
                
                # Check progress every 2 scrolls
                if i % 2 == 0:
                    # Get all images and count valid ones
                    all_img_elements = await page.query_selector_all('img')
                    valid_temp_count = 0
                    unique_urls = set()
                    
                    for img in all_img_elements:
                        try:
                            src = await img.get_attribute('src')
                            if src and ('instagram' in src or 'fbcdn' in src or 'scontent' in src):
                                # Skip profile pictures and small images
                                skip_patterns = ['profile_pic', '150x150', '320x320', 's150x150', 's320x320', 's640x640']
                                should_skip = any(pattern in src for pattern in skip_patterns)
                                
                                if not should_skip and src not in unique_urls:
                                    unique_urls.add(src)
                                    valid_temp_count += 1
                        except:
                            continue
                    
                    print(f"   Found {valid_temp_count} unique valid images so far (total img elements: {len(all_img_elements)})")
                    
                    # Check if we're making progress
                    if valid_temp_count == last_valid_count:
                        stagnant_scrolls += 1
                    else:
                        stagnant_scrolls = 0
                        last_valid_count = valid_temp_count
                    
                    # Stop conditions
                    if valid_temp_count >= count * 1.5:
                        print(f"   ✅ Found enough images ({valid_temp_count}), stopping scroll")
                        break
                    elif stagnant_scrolls >= 6:  # No progress for 6 checks (12 scrolls)
                        print(f"   ⚠️  No new images for {stagnant_scrolls * 2} scrolls, Instagram may have reached end")
                        break
                
                # Force page interaction to prevent Instagram from stopping loading
                if i % 7 == 0:
                    try:
                        await page.keyboard.press('Space')
                        await page.wait_for_timeout(100)
                        await page.keyboard.press('ArrowUp')
                        await page.wait_for_timeout(100)
                    except:
                        pass
            
            # Find all image elements
            print("🔍 Finding image elements...")
            
            # Try different strategies to find all Instagram images
            print("🔍 Strategy 1: Looking for images in posts...")
            
            # First try to find all post containers
            post_links = await page.query_selector_all('a[href*="/p/"]')
            print(f"   Found {len(post_links)} post links")
            
            # Then find images within those posts
            post_images = []
            for link in post_links:
                try:
                    imgs_in_post = await link.query_selector_all('img')
                    post_images.extend(imgs_in_post)
                except:
                    continue
            
            print(f"   Found {len(post_images)} images in posts")
            
            print("🔍 Strategy 2: Looking for all Instagram domain images...")
            # Look for various image selectors that Instagram uses
            image_selectors = [
                'img[src*="instagram"]',
                'img[src*="cdninstagram"]', 
                'img[src*="fbcdn"]',
                'img[src*="scontent"]',  # Facebook content delivery
                'article img',
                'div[role="button"] img',
                'a[role="link"] img',
                'img[alt*="Photo"]',  # Sometimes Instagram uses alt text
                'img[alt*="photo"]',
                'img[loading="lazy"]'  # Lazy loaded images
            ]
            
            all_images = []
            for selector in image_selectors:
                try:
                    images = await page.query_selector_all(selector)
                    all_images.extend(images)
                    print(f"   Selector '{selector}': {len(images)} images")
                except:
                    continue
            
            # Combine post images with general images
            combined_images = list(set(post_images + all_images))
            print(f"🖼️  Combined total: {len(combined_images)} potential images")
            
            # Extract image URLs with improved filtering and debugging
            image_urls = []
            skipped_urls = []
            for img in combined_images:
                try:
                    src = await img.get_attribute('src')
                    if src and ('instagram' in src or 'fbcdn' in src):
                        # Skip profile pictures and small images (more comprehensive filtering)
                        skip_patterns = ['profile_pic', '150x150', '320x320', 's150x150', 's320x320']
                        should_skip = any(pattern in src for pattern in skip_patterns)
                        
                        if not should_skip and src not in image_urls:
                            image_urls.append(src)
                        elif should_skip:
                            skipped_urls.append(src)
                except:
                    continue
            
            print(f"🎯 Found {len(image_urls)} valid image URLs")
            print(f"⏭️  Skipped {len(skipped_urls)} thumbnail/profile images")
            
            if len(image_urls) < count:
                print(f"⚠️  Only found {len(image_urls)} images but requested {count}")
                print(f"   This might be the total number of posts available on this profile's main grid")
                print(f"   Instagram typically shows 12-36 posts per page load")
            
            if not image_urls:
                print("❌ No images found. Instagram may be blocking access.")
                return False, 0
            
            # Limit to requested count
            image_urls = image_urls[:count]
            
            # Download images
            print(f"⬇️  Starting download of {len(image_urls)} images...")
            
            downloaded = 0
            async with aiohttp.ClientSession() as session:
                for i, img_url in enumerate(image_urls):
                    try:
                        # Generate filename
                        timestamp = int(time.time())
                        filename = f"{username}_{timestamp}_{i+1}.jpg"
                        filepath = user_dir / filename
                        
                        print(f"📥 Downloading image {i+1}/{len(image_urls)}: {filename}")
                        
                        # Download image
                        success = await download_image(session, img_url, filepath)
                        if success:
                            downloaded += 1
                            print(f"✅ Downloaded: {filename}")
                        
                        # Add delay between downloads (1-2 seconds)
                        if i < len(image_urls) - 1:
                            delay = 1.5  # 1.5 second delay
                            print(f"   ⏳ Waiting {delay}s before next download...")
                            await asyncio.sleep(delay)
                            
                    except Exception as e:
                        print(f"⚠️  Failed to download image {i+1}: {str(e)}")
                        continue
            
            print(f"🎉 Successfully downloaded {downloaded} images to '{user_dir}'")
            return True, downloaded
            
        except Exception as e:
            print(f"❌ Error during scraping: {str(e)}")
            return False, 0
            
        finally:
            await browser.close()


async def main_async(args):
    """Async main function"""
    
    # Handle cookie management commands
    if args.clear_cookies:
        clear_cookies()
        return True
    
    # Check if username or URL is provided (unless clear-cookies command)
    if not args.username and not args.url:
        print("❌ Error: Either --username or --url is required")
        return False
    
    # Extract username
    if args.url:
        username = extract_username_from_url(args.url)
        if not username:
            print("❌ Error: Could not extract username from URL")
            return False
    else:
        username = args.username
    
    print(f"🚀 Instagram Picture Downloader (Playwright)")
    print(f"👤 Target: {username}")
    print(f"📊 Count: {args.count}")
    print(f"👀 Headless: {'No' if args.show_browser else 'Yes'}")
    print(f"🔐 Login: {'Yes' if args.login else 'Auto'}")
    print(f"🍪 Cookies: {'Disabled' if args.no_cookies else 'Enabled'}")
    print(f"📁 Output: {args.output_dir}")
    print("-" * 50)
    
    # Download images
    success, downloaded = await scrape_instagram_with_playwright(
        username=username,
        count=args.count,
        output_dir=args.output_dir,
        headless=not args.show_browser,
        login_first=args.login,
        use_cookies=not args.no_cookies
    )
    
    # Results
    print("-" * 50)
    if success and downloaded > 0:
        print(f"🎉 Successfully downloaded {downloaded} images!")
        print(f"📁 Check: {args.output_dir}/{username}/")
        return True
    elif success and downloaded == 0:
        print("⚠️  Operation completed but no images were downloaded")
        return False
    else:
        print("💥 Download failed!")
        print("\n💡 Troubleshooting tips:")
        print("- Try with --show-browser to see what's happening")
        print("- Check if the profile exists and is public")
        print("- Instagram may be blocking automated access")
        print("- Try again later or with a different profile")
        return False


def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description="Instagram Picture Downloader using Playwright",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --username grapeot --count 5
  %(prog)s --url https://www.instagram.com/grapeot/ --count 50 --show-browser
  %(prog)s --username grapeot --login --show-browser --count 50
  %(prog)s --clear-cookies  # Clear saved login cookies
  %(prog)s --username grapeot --no-cookies --login  # Force login without cookies
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument('--username', '-u', type=str, 
                           help='Instagram username')
    input_group.add_argument('--url', type=str,
                           help='Instagram profile URL')
    
    # Download options
    parser.add_argument('--count', '-c', type=int, default=5,
                       help='Number of images to download (default: 5)')
    parser.add_argument('--output-dir', '-o', type=str, default='downloads',
                       help='Output directory (default: downloads)')
    parser.add_argument('--show-browser', action='store_true',
                       help='Show browser window (useful for debugging)')
    parser.add_argument('--login', action='store_true',
                       help='Login to Instagram first (recommended for better access)')
    parser.add_argument('--no-cookies', action='store_true',
                       help='Disable cookie saving/loading (always login)')
    parser.add_argument('--clear-cookies', action='store_true',
                       help='Clear saved cookies and exit')
    parser.add_argument('--carousel', action='store_true',
                       help='Enable carousel mode (click into posts to get multiple images per post)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run async main
    try:
        success = asyncio.run(main_async(args))
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()