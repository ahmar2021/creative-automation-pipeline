import json
from utils.prompt_builder import build_prompt

def show_prompts():
    with open("briefs/hydralife_campaign.json") as f:
        brief = json.load(f)
    
    print("\n" + "="*80)
    print(f"CAMPAIGN: {brief['campaign_name']}")
    print("="*80)
    
    for i, product in enumerate(brief["products"], 1):
        print(f"\n{'─'*80}")
        print(f"PRODUCT {i}: {product['name']}")
        print(f"{'─'*80}")
        
        if product.get("asset"):
            print(f"\n✓ Using existing asset: {product['asset']}")
            print("  (No prompt needed - asset will be reused)")
        else:
            print("\n✓ Will generate new image with this prompt:\n")
            prompt = build_prompt(product, brief)
            print("┌" + "─"*78 + "┐")
            for line in prompt.strip().split('\n'):
                print(f"│ {line:<76} │")
            print("└" + "─"*78 + "┘")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    show_prompts()
