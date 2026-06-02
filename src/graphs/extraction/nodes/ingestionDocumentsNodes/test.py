# 1. Get Text
import json

from ingestPPTX import (
    parse_text_from_pptx,
    attach_full_images,
    extract_flowchart_elements_with_docling,
    analyze_slide_visuals_with_local_vlm,
)

pptx_path = r"C:\NUS WORK\Y3S2\Synapxe\AgenticGROSS-JHAttempt\demo_docs\Requirements-ForTesting.pptx"


print(f"--- Starting pipeline for: {pptx_path} ---\n")

print("[1/4] Extracting Markdown text using Docling...")
slides = parse_text_from_pptx(pptx_path)
print("--- 1. SLIDES (After parse_text_from_pptx) ---")
print(json.dumps(slides[:2], indent=2))

print("[2/4] Rendering full slide images...")
attach_full_images(slides, pptx_path, output_dir="tmp/full_slides")
print("--- 2. SLIDES (After attach_full_images) ---")
print(json.dumps(slides[:2], indent=2))

print("[3/4] Extracting visual elements using Docling...")
extract_flowchart_elements_with_docling(slides, pptx_path, output_dir="tmp/visual_elements")
print("--- 3. SLIDES (After extract_flowchart_elements_with_docling) ---")
print(json.dumps(slides[:2], indent=2))

print("[4/4] Enriching visual descriptions with local VLM (Ollama)...")
analyze_slide_visuals_with_local_vlm(slides)
print("--- 4. SLIDES (After analyze_slide_visuals_with_local_vlm) ---")
print(json.dumps(slides[:2], indent=2))
