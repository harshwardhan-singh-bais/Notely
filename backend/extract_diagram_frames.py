import os
import cv2
import torch
import clip
import json
from PIL import Image
from tqdm import tqdm

# CONFIG
FRAME_INTERVAL = 0.5  # seconds between frames to check (more frequent)
SIMILARITY_THRESHOLD = 0.22  # lower threshold for more sensitivity
PROMPTS = [
    "a diagram", 
    "a slide presentation", 
    "a chart or graph", 
    "text content on screen", 
    "a table with data",
    "a code snippet or programming",
    "a flowchart or process diagram",
    "a mathematical equation or formula",
    "an infographic or visual explanation",
    "a screenshot of an application",
    "educational content or tutorial",
    "a whiteboard or blackboard with writing"
]


def extract_relevant_frames(video_path, output_dir):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)
    os.makedirs(output_dir, exist_ok=True)

    # Prepare text prompts
    text_tokens = clip.tokenize(PROMPTS).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    # Open video
    vidcap = cv2.VideoCapture(video_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    frame_interval = int(fps * FRAME_INTERVAL)

    frame_idx = 0
    saved = 0
    pbar = tqdm(total=frame_count, desc="Analyzing frames")
    while True:
        ret, frame = vidcap.read()
        if not ret:
            break
        if frame_idx % frame_interval == 0:
            # Convert frame to PIL Image
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            image_input = preprocess(img).unsqueeze(0).to(device)
            with torch.no_grad():
                image_features = model.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)
                similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
                max_sim, idx = similarity[0].max(0)
                if max_sim.item() > SIMILARITY_THRESHOLD:
                    timestamp = frame_idx / fps
                    out_path = os.path.join(output_dir, f"frame_{frame_idx:06d}_t{timestamp:.1f}s.jpg")
                    img.save(out_path)
                    saved += 1
                    
                    # Save metadata about this frame
                    prompt_idx = idx.item()
                    confidence = max_sim.item()
                    metadata = {
                        'frame_idx': frame_idx,
                        'timestamp': timestamp,
                        'prompt_matched': PROMPTS[prompt_idx],
                        'confidence': confidence,
                        'filename': os.path.basename(out_path)
                    }
                    
                    # Save metadata to JSON file
                    metadata_path = os.path.join(output_dir, "frame_metadata.json")
                    if os.path.exists(metadata_path):
                        with open(metadata_path, "r") as f:
                            all_metadata = json.load(f)
                    else:
                        all_metadata = []
                    all_metadata.append(metadata)
                    with open(metadata_path, "w") as f:
                        json.dump(all_metadata, f, indent=2)
        frame_idx += 1
        pbar.update(1)
    pbar.close()
    vidcap.release()
    print(f"Saved {saved} relevant frames to {output_dir}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python extract_diagram_frames.py <video_path> <output_dir>")
        exit(1)
    extract_relevant_frames(sys.argv[1], sys.argv[2])
