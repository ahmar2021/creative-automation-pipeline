import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Maps aspect ratios to DeepAI shape IDs (1-5):
# 1=wide landscape, 2=mild landscape, 3=square, 4=mild portrait, 5=tall portrait
SHAPE_MAP = {
    "1x1": 3,
    "9x16": 5,
    "16x9": 1,
}

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
    
    def _select_shape(self, shape_id):
        """Select shape by calling selectShape(N) via JS. shape_id is 1-5."""
        try:
            # Open shape options panel first
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "modelEditButton"))
            ).click()
            time.sleep(1)
            self.driver.execute_script(f"selectShape({shape_id})")
            time.sleep(1)
        except Exception as e:
            print(f"  ✗ Could not select shape {shape_id}: {e}")

    def generate_image(self, prompt, output_path, shape=None):
        """Generate image from prompt and save to output_path"""
        self.driver.get(self.url)
        
        # Select shape before entering prompt if specified
        if shape:
            self._select_shape(shape)
        
        # Wait for textarea to be clickable
        textarea = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea"))
        )
        
        # Enter text
        textarea.click()
        textarea.clear()
        textarea.send_keys(prompt)
        
        # Trigger input event to enable button
        self.driver.execute_script("""
            var event = new Event('input', { bubbles: true });
            arguments[0].dispatchEvent(event);
        """, textarea)
        
        time.sleep(3)
        
        # Click the submit button
        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "modelSubmitButton"))
            )
            self.driver.execute_script("arguments[0].click();", btn)
        except Exception as e:
            print(f"  ✗ Could not submit: {e}")
            return None
        
        # Wait for generated image (poll for up to 30s)
        img_url = None
        for _ in range(15):
            time.sleep(2)
            # Check for error message
            try:
                err = self.driver.find_element(By.CSS_SELECTOR, ".try-it-result-error")
                if err.is_displayed() and err.text.strip():
                    print(f"  ✗ DeepAI error: {err.text.strip()}")
                    return None
            except:
                pass
            # Look for a generated image from api.deepai.org
            srcs = self.driver.execute_script("""
                var imgs = document.querySelectorAll('img');
                for (var i = 0; i < imgs.length; i++) {
                    if (imgs[i].src.includes('api.deepai.org') && imgs[i].src.includes('/output')) {
                        return imgs[i].src;
                    }
                }
                return null;
            """)
            if srcs:
                img_url = srcs
                break
        
        if not img_url:
            print("  ✗ Could not find generated image")
            return None
        
        try:
            # Download the image
            response = requests.get(img_url)
            
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return output_path
            
        except Exception as e:
            print(f"  ✗ Error generating image: {e}")
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
