IngestPPTX 


IDEAs: 
Raw markdown + OCR vision of visual elements ==> Slide-wise organsitiaon of data ====> For base Extraction of info. 

Idea for How the OCR would work 
1. Render each slide into one image
2. Docling : extract various pictureItems and their coordinates (High res artifacts of these screenshots and other smartArt elements) 
  - Pros : Catering for screenshots of UIs in the app ()
  - Cons : Fragmented
  = Identify whether it is screenshot of UIs/flowchart entities OR just smartArt elements (ie. arrows) 
     - if entity: deduce the purpose etc. and connections
     - if arrows or captions : mark down what it connects (significance)
3. Hybrid : Pass both 1 and 2  
    - Tool calling esp during any phase of extraction to be able to "zoom in" to particular part of any slide? 
      -Associated PictureItems tagged to a slide, that will be labelled during the processing of VLM 


## Data structures 
Slides : List[Dict]
list index: slide number - 1
 In dict: 
 - slide_number : parse_text_from_pptx()
 - raw_text markdown : parse_text_from_pptx()
 - full_image : render_pptx_slide_to_images() does for all slides at once 
 - associated_visual_elements : [ object, .. ] where each is a class with the following attributes
    - elementType : (Always Entity using docling) 
    - description : (inferred by VLM; ie. for what functional/architectural purpose depending on type, connects to what) 
 
## What VLM does (Prompt Template to do analysis)
Input : Raw markdown + (Full image + individual elements)

Process :
1) Analysis of text (what this slide is about)
2) Analysis of full image (Phases and how it relates to text) 
3) Analysis of screenshot PictureItems 

output: Append to 'Slides' data structure 
Analysis

### Should this process of VLM be delayed until baseExtractionNodes when obtaining the baseline data? 

### VAlidation : Does it pick up on contents of a test slide as intended? 
Do I need to take text up? 