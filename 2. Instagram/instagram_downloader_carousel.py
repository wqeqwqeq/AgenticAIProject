#!/usr/bin/env python3
"""
Instagram Picture Downloader with Carousel Support

This version clicks into individual posts to extract all carousel images,
potentially downloading much more than the 43 grid limit.

Usage:
    python instagram_downloader_carousel.py --username grapeot --count 100 --show-browser
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
    """Save browser cookies to file"""
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
    """Load browser cookies from file"""
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
    """Handle Instagram login process"""
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


async def extract_carousel_images(page, post_url):
    """
    Click into a post and extract all carousel images
    
    Args:
        page: Playwright page object
        post_url: URL of the post to extract from
    
    Returns:
        list: List of image URLs from the carousel
    """
    carousel_images = []
    
    try:
        print(f"   🔍 Opening post: {post_url}")
        
        # Open the post in the same page
        await page.goto(post_url, wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(3000)  # Wait for images to load
        
        # Look for carousel indicators (dots) or next/prev buttons
        carousel_indicators = await page.query_selector_all('div[role="button"][aria-label*="Next"], button[aria-label*="Next"]')
        
        # Try to find all images in the current post view
        image_selectors = [
            'article img[src*="instagram"]',
            'img[src*="cdninstagram"]',
            'img[src*="scontent"]',
            'div[role="button"] img'
        ]
        
        images_found = set()
        
        # Extract current visible images
        for selector in image_selectors:
            try:
                post_images = await page.query_selector_all(selector)
                for img in post_images:
                    try:
                        src = await img.get_attribute('src')
                        if src and ('instagram' in src or 'cdninstagram' in src or 'scontent' in src):
                            # Skip small thumbnails
                            skip_patterns = ['profile_pic', '150x150', '320x320', 's150x150', 's320x320']
                            should_skip = any(pattern in src for pattern in skip_patterns)
                            
                            if not should_skip:
                                images_found.add(src)
                    except:
                        continue
            except:
                continue
        
        print(f"   📸 Found {len(images_found)} images in first view")
        
        # If there are carousel indicators, try clicking through them
        if carousel_indicators:
            print(f"   🎠 Detected carousel with {len(carousel_indicators)} navigation elements")
            
            # Click through the carousel to find more images
            max_clicks = 10  # Prevent infinite loops
            clicks = 0
            
            while clicks < max_clicks:
                try:
                    # Try to find and click next button
                    next_button = await page.query_selector('button[aria-label*="Next"], div[role="button"][aria-label*="Next"]')
                    if next_button:
                        await next_button.click()
                        await page.wait_for_timeout(2000)  # Wait for new image to load
                        
                        # Extract images from new view
                        for selector in image_selectors:
                            try:
                                post_images = await page.query_selector_all(selector)
                                for img in post_images:
                                    try:
                                        src = await img.get_attribute('src')
                                        if src and ('instagram' in src or 'cdninstagram' in src or 'scontent' in src):
                                            skip_patterns = ['profile_pic', '150x150', '320x320', 's150x150', 's320x320']
                                            should_skip = any(pattern in src for pattern in skip_patterns)
                                            
                                            if not should_skip:
                                                images_found.add(src)
                                    except:
                                        continue
                            except:
                                continue
                        
                        clicks += 1
                    else:
                        break  # No more next button
                        
                except Exception as e:
                    print(f"   ⚠️  Error navigating carousel: {str(e)}")
                    break
        
        carousel_images = list(images_found)
        print(f"   ✅ Total carousel images: {len(carousel_images)}")
        
    except Exception as e:
        print(f"   ❌ Error extracting carousel: {str(e)}")
    
    return carousel_images


async def scrape_instagram_with_carousel(username, count=5, output_dir="downloads", headless=True, login_first=False, use_cookies=True):
    """
    Scrape Instagram with carousel support for more images
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
            
            # Scroll to load posts
            print("📜 Scrolling to load posts...")
            for i in range(5):  # Less scrolling since we'll extract more per post
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(3000)
            
            # Find all post links
            print("🔗 Finding post links...")
            post_links = await page.query_selector_all('a[href*="/p/"]')
            print(f"   Found {len(post_links)} posts")
            
            if not post_links:
                print("❌ No posts found on this profile")
                return False, 0
            
            # Extract URLs from post links
            post_urls = []
            for link in post_links:
                try:
                    href = await link.get_attribute('href')
                    if href and '/p/' in href:
                        if not href.startswith('http'):
                            href = f"https://www.instagram.com{href}"
                        post_urls.append(href)
                except:
                    continue
            
            print(f"🎯 Processing {len(post_urls)} post URLs...")
            
            # Process each post to extract carousel images
            all_images = []
            processed_posts = 0
            
            for i, post_url in enumerate(post_urls):
                if len(all_images) >= count:
                    print(f"   ✅ Reached target of {count} images, stopping")
                    break
                
                print(f"📱 Processing post {i+1}/{len(post_urls)}")
                carousel_images = await extract_carousel_images(page, post_url)
                
                all_images.extend(carousel_images)
                processed_posts += 1
                
                print(f"   Running total: {len(all_images)} images from {processed_posts} posts")
                
                # Go back to profile for next post
                await page.goto(profile_url, wait_until='domcontentloaded', timeout=30000)
                await page.wait_for_timeout(2000)
            
            print(f"🎉 Collected {len(all_images)} total images from {processed_posts} posts")
            
            # Limit to requested count
            download_images = all_images[:count]
            
            # Download images
            print(f"⬇️  Starting download of {len(download_images)} images...")
            
            downloaded = 0
            async with aiohttp.ClientSession() as session:
                for i, img_url in enumerate(download_images):
                    try:
                        # Generate filename
                        timestamp = int(time.time())
                        filename = f"{username}_carousel_{timestamp}_{i+1}.jpg"
                        filepath = user_dir / filename
                        
                        print(f"📥 Downloading image {i+1}/{len(download_images)}: {filename}")
                        
                        # Download image
                        success = await download_image(session, img_url, filepath)
                        if success:
                            downloaded += 1
                            print(f"✅ Downloaded: {filename}")
                        
                        # Add delay between downloads
                        if i < len(download_images) - 1:
                            delay = 1.5
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
    
    # Check if username or URL is provided
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
    
    print(f"🚀 Instagram Carousel Picture Downloader")
    print(f"👤 Target: {username}")
    print(f"📊 Count: {args.count}")
    print(f"👀 Headless: {'No' if args.show_browser else 'Yes'}")
    print(f"🔐 Login: {'Yes' if args.login else 'Auto'}")
    print(f"🍪 Cookies: {'Disabled' if args.no_cookies else 'Enabled'}")
    print(f"📁 Output: {args.output_dir}")
    print("-" * 60)
    
    # Download images
    success, downloaded = await scrape_instagram_with_carousel(
        username=username,
        count=args.count,
        output_dir=args.output_dir,
        headless=not args.show_browser,
        login_first=args.login,
        use_cookies=not args.no_cookies
    )
    
    # Results
    print("-" * 60)
    if success and downloaded > 0:
        print(f"🎉 Successfully downloaded {downloaded} images (including carousel images)!")
        print(f"📁 Check: {args.output_dir}/{username}/")
        return True
    else:
        print("💥 Download failed!")
        return False


def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description="Instagram Picture Downloader with Carousel Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --username grapeot --count 100 --show-browser
  %(prog)s --url https://www.instagram.com/grapeot/ --count 200 --login
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument('--username', '-u', type=str, 
                           help='Instagram username')
    input_group.add_argument('--url', type=str,
                           help='Instagram profile URL')
    
    # Download options
    parser.add_argument('--count', '-c', type=int, default=50,
                       help='Number of images to download (default: 50)')
    parser.add_argument('--output-dir', '-o', type=str, default='downloads',
                       help='Output directory (default: downloads)')
    parser.add_argument('--show-browser', action='store_true',
                       help='Show browser window (useful for debugging)')
    parser.add_argument('--login', action='store_true',
                       help='Login to Instagram first (recommended for better access)')
    parser.add_argument('--no-cookies', action='store_true',
                       help='Disable cookie saving/loading (always login)')
    
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