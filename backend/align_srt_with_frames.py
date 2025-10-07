import os
import pysrt

def align_srt_with_frames(srt_path, frame_dir, output_path=None):
    """
    For each frame in frame_dir, find the SRT subtitle(s) that overlap with the frame's timestamp.
    Assumes frame filenames are like frame_123.jpg where 123 is the frame index (or timestamp in seconds).
    """
    subs = pysrt.open(srt_path)
    frame_files = [f for f in os.listdir(frame_dir) if f.endswith('.jpg')]
    frame_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    alignments = []
    for frame_file in frame_files:
        frame_idx = int(frame_file.split('_')[1].split('.')[0])
        # Assume 1 frame per second for simplicity
        frame_start = frame_idx
        frame_end = frame_idx + 1
        relevant_subs = [s for s in subs if s.start.seconds < frame_end and s.end.seconds >= frame_start]
        alignments.append({
            'frame': frame_file,
            'subtitles': [s.text for s in relevant_subs]
        })
    out_path = output_path or os.path.join(frame_dir, 'frame_subtitle_alignment.json')
    import json
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(alignments, f, ensure_ascii=False, indent=2)
    print(f"Frame-subtitle alignment saved to {out_path}")
    return alignments

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python align_srt_with_frames.py <srt_path> <frame_dir> [output_path]")
        exit(1)
    srt_path = sys.argv[1]
    frame_dir = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None
    align_srt_with_frames(srt_path, frame_dir, output_path)
