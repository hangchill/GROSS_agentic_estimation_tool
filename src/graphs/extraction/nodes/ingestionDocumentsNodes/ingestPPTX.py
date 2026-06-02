from __future__ import annotations
import tempfile
from typing import Dict, Any, List, Optional
import io
import os
import subprocess
import sys

import base64
import json

# from pptx import Presentation
from PIL import Image
from docling.document_converter import DocumentConverter, PowerpointFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.document import PictureItem, TextItem
import re

from openai import OpenAI

def parse_text_from_pptx(pptx_path: str) -> List[Dict[str, Any]]:
    """Text extraction from pptx using docling.

    Returns Slides: List[Dict] where each entry (index = slide_number - 1) contains:
      - slide_number (1-based)
      - raw_text (markdown)
      - full_image (path or None)
      - associated_visual_elements (List[Dict] each with exactly {description, image_path})
    """
    ### python-pptx is manual, docling better 

    # Initialize the converter and parse the PPTX
    converter = DocumentConverter()
    result = converter.convert(pptx_path)
    doc = result.document
    
    slides: List[Dict[str, Any]] = []
    
    # Docling page numbers are 1-indexed, so we iterate from 1 to num_pages
    for page_no in range(1, doc.num_pages() + 1):
        # Extract formatted markdown text for the specific slide
        # docling handles tables, lists, and standard text blocks intelligently
        page_text = doc.export_to_markdown(page_no=page_no)
        
        slides.append({
            "slide_number": page_no,
            "raw_text": page_text.strip(),
            "full_image": None,
            "associated_visual_elements": [],
        })
        
    return slides


## Information in the ppt: 
### SmartArt arrows and textboxes constitute the flowcharts 
### Screenshots of functionalities pages in app constitute the phases of flowcharts  

# vlm used to analyse visual elements: minicpm-v, llama3.2-vision, llava:7b , qwen3-35b
## 1. Render slide into one image


## 2. Docling : 
## For each slide: Extract list of objects present ie. smartArt text, arrows and pictures ONLY
# 1. Image extraction enable 
# 2. Extract smartArt text for arrows and captions 
# 3. app screenshhots as PictureItem Objects 
# 4. Caputre bounding boxes (metadata for various flowchart elements)


def render_pptx_slides_to_images(pptx_path: str, output_dir: str) -> Dict[int, str]:
    """
    Renders each slide in a PPTX to a full image using LibreOffice and PyMuPDF.
    Cross-platform compatible (Windows, macOS, Linux).
    Returns a dictionary mapping slide_number (1-indexed) to the full slide image path.
    """
    os.makedirs(output_dir, exist_ok=True)
    full_slide_paths = {}

    # 1. Determine the path to the LibreOffice executable based on the OS
    if os.name == 'nt':  # Windows
        # Standard default installation path for Windows
        soffice_path = r"C:\Program Files\LibreOffice\program\soffice.exe"
    elif sys.platform == "darwin":  # macOS
        soffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    else:  # Linux
        # Usually available globally in PATH on Linux
        soffice_path = "soffice"

    # We use a temporary directory for the intermediate PDF so it cleans up automatically
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # 2. Convert PPTX to PDF using LibreOffice Headless
        try:
            subprocess.run(
                [
                    soffice_path,
                    "--headless",
                    "--nologo",
                    "--nofirststartwizard",
                    "--convert-to", "pdf",
                    "--outdir", temp_dir,
                    os.path.abspath(pptx_path)
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            raise RuntimeError(
                f"LibreOffice not found at {soffice_path}. "
                "Ensure it is installed or update the soffice_path variable."
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"LibreOffice PDF conversion failed: {e}")

        # Construct the expected path of the generated PDF
        base_name = os.path.splitext(os.path.basename(pptx_path))[0]
        pdf_path = os.path.join(temp_dir, f"{base_name}.pdf")

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"LibreOffice succeeded but PDF was not found at {pdf_path}")

        # 3. Render the intermediate PDF pages to PNGs using PyMuPDF
        pdf_doc = fitz.open(pdf_path)
        
        for page_idx in range(len(pdf_doc)):
            page_no = page_idx + 1
            page = pdf_doc.load_page(page_idx)
            
            # Matrix to increase the resolution of the output image. 
            # Zoom factor of 2.0 roughly equals 144 DPI (great for VLM OCR)
            mat = fitz.Matrix(2.0, 2.0)
            
            # Extract image as a pixmap (alpha=False ensures a solid white background)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            image_filename = f"full_slide_{page_no}.png"
            image_path = os.path.join(output_dir, image_filename)
            
            # Save to disk
            pix.save(image_path)
            full_slide_paths[page_no] = image_path
            
        pdf_doc.close()

    return full_slide_paths

def attach_full_images(slides: List[Dict[str, Any]], pptx_path: str, output_dir: str) -> None:
    """Mutates Slides in-place to attach full-slide rendered image paths."""
    full_slide_paths = render_pptx_slides_to_images(pptx_path=pptx_path, output_dir=output_dir)
    for slide in slides:
        slide_number = slide.get("slide_number")
        if isinstance(slide_number, int):
            slide["full_image"] = full_slide_paths.get(slide_number)


def extract_flowchart_elements_with_docling(slides: List[Dict[str, Any]], pptx_path: str, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    # Initialize the Converter using the native PowerPoint format option
    converter = DocumentConverter(
        format_options={
            InputFormat.PPTX: PowerpointFormatOption()
        }
    )

    result = converter.convert(pptx_path)
    doc = result.document

    def get_slide_entry(slide_number: int) -> Optional[Dict[str, Any]]:
        if slide_number < 1 or slide_number > len(slides):
            return None
        entry = slides[slide_number - 1]
        if entry.get("slide_number") == slide_number:
            return entry
        for candidate in slides:
            if candidate.get("slide_number") == slide_number:
                return candidate
        return None

    # 2. Iterate globally through ALL elements in the document
    for item, level in doc.iterate_items():
        # Safety check: skip items that don't have provenance (location) data
        if not item.prov:
            continue
            
        slide_number = item.prov[0].page_no
        slide_entry = get_slide_entry(slide_number)
        if not slide_entry:
            continue

        associated_elements = slide_entry.get("associated_visual_elements")
        if not isinstance(associated_elements, list):
            slide_entry["associated_visual_elements"] = []
            associated_elements = slide_entry["associated_visual_elements"]

        # Extract Text (SmartArt text / textboxes)
        if isinstance(item, TextItem):
            if item.text and item.text.strip():
                associated_elements.append({
                    "description": item.text.strip(),
                    "image_path": None,
                })

        # Extract Pictures (screenshots/icons as images)
        elif isinstance(item, PictureItem):
            bbox = item.prov[0].bbox
            image_obj = item.get_image(doc)
            
            if image_obj:
                safe_l = int(bbox.l) if bbox else "unknown"
                image_filename = f"slide_{slide_number}_visual_{safe_l}.png"
                image_path = os.path.join(output_dir, image_filename)
                image_obj.save(image_path)

                if hasattr(item, "text") and isinstance(item.text, str) and item.text.strip():
                    description = item.text.strip()
                else:
                    description = image_filename

                associated_elements.append({
                    "description": description,
                    "image_path": image_path,
                })

## Handover information for VLMs analysis 
# vlm used to analyse : minicpm-v, llama3.2-vision, llava:7b , qwen3-35b
# no need vlm now, we doing the analysis in the various nodes

def ensure_ollama_model_exists(model_name: str):
    """
    Checks if the requested model exists in the local Ollama registry.
    If missing, it attempts to build it from a local Modelfile or pull it natively.
    """
    print(f"\n[System Check] Verifying Ollama model '{model_name}'...")
    
    try:
        # 1. Ask Ollama what models it currently has installed
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        
        # We add a colon and space to ensure we don't accidentally match a partial name
        if model_name in result.stdout:
            print(f" '{model_name}' is already installed and ready.")
            return

    except FileNotFoundError:
        raise RuntimeError("Ollama is not installed or not running. Please install Ollama first.")
    except subprocess.CalledProcessError:
        raise RuntimeError("Could not communicate with Ollama. Is the background app running?")

    # 2. If we reach here, the model is missing. Let's try to make it.
    print(f" '{model_name}' not found locally.")

    if os.path.exists(r"C:\NUS WORK\Y3S2\Synapxe\gross-estimation-project\Models\Modelfile"):
        print(f" Found 'Modelfile' in directory. Building '{model_name}' now (this may take a minute)...")
        try:
            # We don't capture output here so you can watch the build progress in your terminal
            subprocess.run(["ollama", "create", model_name, "-f", r"C:\NUS WORK\Y3S2\Synapxe\gross-estimation-project\Models\Modelfile"], check=True)
            print(f"Successfully built '{model_name}' from local Modelfile.")
        except subprocess.CalledProcessError:
            raise RuntimeError(f"Failed to build '{model_name}' from Modelfile. Check your GGUF file paths.")
            
    else:
        print(f" No Modelfile found. Attempting to pull '{model_name}' from the Ollama cloud...")
        try:
            subprocess.run(["ollama", "pull", model_name], check=True)
            print(f"Successfully downloaded '{model_name}'.")
        except subprocess.CalledProcessError:
            raise RuntimeError(f"Failed to pull '{model_name}'. Check your internet connection or the model name.")


def encode_image_to_base64_with_resize(image_path: str, max_size=(800, 800)) -> str:
    """Resizes and compresses an image before base64 encoding to save VLM context limits."""
    with Image.open(image_path) as img:
        # Convert transparent PNGs to solid RGB so JPEG compression works
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            
        # thumbnail dynamically resizes the image while keeping the correct aspect ratio
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to a temporary memory buffer as a compressed JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    

def analyze_slide_visuals_with_local_vlm(
    slides: List[Dict[str, Any]],
    model_name: str = "llama3.2-vision",
) -> None:
    """Mutates Slides in-place by enriching image element descriptions using a local VLM."""

    ensure_ollama_model_exists(model_name)

    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    )

    system_prompt = """
Role: You are an expert systems analyst.
Context: You are given the slide's markdown text, a full-slide image (if available), and several crop images extracted from the slide.
Goal: Describe what each crop image contains, using the full slide + text as context.

Output a strict JSON object with this exact schema:
{
  "elements": [
    {
      "crop_index": "1-based index of the crop images in the same order provided",
      "description": "Concise description of what the crop shows"
    }
  ]
}
"""

    for slide in slides:
        associated_elements = slide.get("associated_visual_elements")
        if not isinstance(associated_elements, list):
            continue

        image_elements = [
            e for e in associated_elements
            if isinstance(e, dict) and isinstance(e.get("image_path"), str) and e.get("image_path")
        ]
        if not image_elements:
            continue

        user_content: List[Dict[str, Any]] = [
            {"type": "text", "text": "Describe each crop image. Keep output JSON only."},
            {"type": "text", "text": f"SLIDE MARKDOWN TEXT:\n{slide.get('raw_text', '')}"},
        ]

        full_image_path = slide.get("full_image")
        if isinstance(full_image_path, str) and os.path.exists(full_image_path):
            try:
                full_b64 = encode_image_to_base64_with_resize(full_image_path)
                user_content.append({"type": "text", "text": "FULL SLIDE IMAGE:"})
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{full_b64}"},
                })
            except Exception:
                pass

        for idx, element in enumerate(image_elements, start=1):
            img_path = element.get("image_path")
            if not isinstance(img_path, str) or not os.path.exists(img_path):
                continue
            try:
                crop_b64 = encode_image_to_base64_with_resize(img_path)
                user_content.append({"type": "text", "text": f"CROP {idx}:"})
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{crop_b64}"},
                })
            except Exception:
                continue

        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            raw_output = response.choices[0].message.content or ""
            clean_json = re.sub(r'```json\n|\n```|```', '', raw_output).strip()
            vlm_output = json.loads(clean_json)

            elements = vlm_output.get("elements")
            if not isinstance(elements, list):
                continue

            for entry in elements:
                if not isinstance(entry, dict):
                    continue
                crop_index = entry.get("crop_index")
                description = entry.get("description")
                try:
                    crop_i = int(crop_index)
                except Exception:
                    continue
                if crop_i < 1 or crop_i > len(image_elements):
                    continue
                if isinstance(description, str) and description.strip():
                    image_elements[crop_i - 1]["description"] = description.strip()

        except Exception:
            continue



# def compile_pptx_slides(
#     pptx_path: str,
#     full_images_dir: str = "tmp/pptx_full_slides",
#     elements_dir: str = "tmp/pptx_visual_elements",
#     model_name: str = "llama3.2-vision",
# ) -> List[Dict[str, Any]]:
#     """End-to-end helper to build Slides data structure (README schema)."""
#     slides = parse_text_from_pptx(pptx_path)
#     attach_full_images(slides=slides, pptx_path=pptx_path, output_dir=full_images_dir)
#     extract_flowchart_elements_with_docling(slides=slides, pptx_path=pptx_path, output_dir=elements_dir)
#     analyze_slide_visuals_with_local_vlm(slides=slides, model_name=model_name)
#     return slides


