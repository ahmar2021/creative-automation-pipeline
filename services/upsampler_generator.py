import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

ASPECT_RATIO_MAP = {
    "1x1": "Square (1:1)",
    "9x16": "Portrait (9:16)",
    "16x9": "Landscape (16:9)",
}

# CLI flag -> model button text prefix
MODEL_MAP = {
    "zimage": "Z-Image Turbo",
    "wan": "Wan 2.2 14B",
    "qwen": "Qwen Image",
    "flux9b": "Flux 2 Klein 9B",
    "flux4b": "Flux 2 Klein 4B",
}

DEFAULT_MODEL = "zimage"


class UpsamplerImageGenerator:
    def __init__(self, model=None, headless=False):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.url = "https://upsampler.com/free-image-generator-no-signup"
        self.model = model or DEFAULT_MODEL

    def _select_model(self):
        target = MODEL_MAP.get(self.model)
        if not target:
            return
        # Click the model button to open dialog
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            if btn.text.strip() in MODEL_MAP.values():
                self.driver.execute_script("arguments[0].click();", btn)
                break
        time.sleep(1)
        # Click the target model in the dialog
        dialog_btns = self.driver.find_elements(By.CSS_SELECTOR, "[role='dialog'] button")
        for btn in dialog_btns:
            if btn.text.strip().startswith(target):
                btn.click()
                time.sleep(0.5)
                return

    def _select_aspect_ratio(self, ratio):
        label = ASPECT_RATIO_MAP.get(ratio)
        if not label:
            return
        ar_btn = self.driver.find_element(By.ID, "aspect-ratio")
        self.driver.execute_script("arguments[0].click();", ar_btn)
        time.sleep(0.5)
        for opt in self.driver.find_elements(By.CSS_SELECTOR, "[role='option']"):
            if opt.text == label:
                opt.click()
                return
        self.driver.execute_script("document.body.click();")

    def generate_image(self, prompt, output_path, shape=None):
        self.driver.get(self.url)
        time.sleep(5)

        self._select_model()
        if shape:
            self._select_aspect_ratio(shape)
            time.sleep(0.5)

        prompt_input = self.driver.find_element(By.ID, "prompt-input")
        prompt_input.clear()
        prompt_input.send_keys(prompt)

        # Click generate
        for btn in self.driver.find_elements(By.TAG_NAME, "button"):
            if "Generate Image" in btn.text:
                self.driver.execute_script("arguments[0].click();", btn)
                break

        # Poll for generated image (up to 30s)
        img_url = None
        for _ in range(15):
            time.sleep(2)
            # Check for rate limit or error messages
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            if "exceeded" in page_text.lower() and "gpu" in page_text.lower():
                print("  ✗ Rate limited: could not generate images")
                return None
            for img in self.driver.find_elements(By.TAG_NAME, "img"):
                src = img.get_attribute("src") or ""
                alt = img.get_attribute("alt") or ""
                w = img.size.get("width", 0)
                if w >= 200 and ("generated" in alt.lower() or src.startswith("data:image") or src.startswith("blob:")):
                    img_url = src
                    break
                if w >= 200 and "upsampler" not in src and "favicon" not in src and not src.endswith(".svg"):
                    img_url = src
                    break
            if img_url:
                break

        if not img_url:
            print("  ✗ Could not find generated image")
            return None

        try:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            if img_url.startswith("data:image"):
                import base64
                _, data = img_url.split(",", 1)
                with open(output_path, "wb") as f:
                    f.write(base64.b64decode(data))
            else:
                resp = requests.get(img_url)
                with open(output_path, "wb") as f:
                    f.write(resp.content)
            return output_path
        except Exception as e:
            print(f"  ✗ Error saving image: {e}")
            return None

    def close(self):
        self.driver.quit()


def main():
    import sys
    model = DEFAULT_MODEL
    for arg in sys.argv[1:]:
        if arg.startswith("--") and arg[2:] in MODEL_MAP:
            model = arg[2:]
    generator = UpsamplerImageGenerator(model=model, headless=False)
    try:
        print(f"Using model: {MODEL_MAP[model]}")
        result = generator.generate_image(
            "luxury lipstick product photo, elegant packaging, studio lighting",
            "output/upsampler_test.jpg",
            shape="1x1"
        )
        if result:
            print(f"✓ Image saved to: {result}")
        else:
            print("✗ Generation failed")
    finally:
        generator.close()


if __name__ == "__main__":
    main()
