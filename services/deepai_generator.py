import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class DeepAIImageGenerator:
    def __init__(self, headless=False):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.url = "https://deepai.org/machine-learning-model/text2img"
    
    def generate_image(self, prompt, output_path):
        """Generate image from prompt and save to output_path"""
        print(f"Navigating to DeepAI...")
        self.driver.get(self.url)
        
        # Wait for textarea to be clickable (replaces sleep)
        print(f"Entering prompt: {prompt[:50]}...")
        textarea = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea"))
        )
        print(f"Found textarea")
        
        # Enter text
        textarea.click()
        textarea.clear()
        textarea.send_keys(prompt)
        
        # Trigger input event to enable button
        self.driver.execute_script("""
            var event = new Event('input', { bubbles: true });
            arguments[0].dispatchEvent(event);
        """, textarea)
        
        print("Text entered, waiting for button to enable...")
        time.sleep(3)
        
        # Wait for button and trigger submission
        print("Waiting for generate button...")
        
        # Find the form and submit it directly
        try:
            form = self.driver.find_element(By.TAG_NAME, "form")
            print("Found form, submitting...")
            self.driver.execute_script("arguments[0].submit();", form)
            print("Form submitted!")
        except:
            # Fallback: try button click
            button = None
            selectors = [
                (By.XPATH, "//button[contains(text(), 'Generate')]"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "button.generate-btn"),
                (By.ID, "generate-button"),
            ]
            
            for by, selector in selectors:
                try:
                    button = self.driver.find_element(by, selector)
                    print(f"Found button with: {selector}")
                    break
                except:
                    continue
            
            if not button:
                print("Could not find button or form")
                return None
            
            # Try pressing Enter on textarea instead
            print("Trying Enter key on textarea...")
            from selenium.webdriver.common.keys import Keys
            textarea.send_keys(Keys.RETURN)
            print("Enter pressed!")
        
        # Wait for image generation
        print("Waiting for image generation...")
        time.sleep(5)
        
        try:
            # Find all images and filter for the generated one
            all_images = self.driver.find_elements(By.TAG_NAME, "img")
            print(f"Found {len(all_images)} images on page")
            
            img_element = None
            for idx, img in enumerate(all_images):
                src = img.get_attribute("src")
                width = img.size.get('width', 0)
                height = img.size.get('height', 0)
                
                if width < 200 or height < 200:
                    continue
                
                # Skip loading images and logos
                if src and "loading" not in src.lower() and "data:image" not in src and "logo" not in src.lower() and "icon" not in src.lower():
                    print(f"Image {idx}: {src[:80]}... (size: {width}x{height})")
                    img_element = img
                    break
            
            if not img_element:
                print("Could not find generated image")
                return None
            
            img_url = img_element.get_attribute("src")
            print(f"Image URL: {img_url}")
            
            # Download the image
            response = requests.get(img_url)
            
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Image saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"✗ Error generating image: {e}")
            return None
    
    def close(self):
        """Close the browser"""
        self.driver.quit()

def main():
    generator = DeepAIImageGenerator(headless=False)
    
    try:
        prompt = "VitaSpark Energy - Natural vitamin energy drink for young professionals"
        output_path = "output/generated_image.jpg"
        generator.generate_image(prompt, output_path)
        
    finally:
        generator.close()

if __name__ == "__main__":
    main()
