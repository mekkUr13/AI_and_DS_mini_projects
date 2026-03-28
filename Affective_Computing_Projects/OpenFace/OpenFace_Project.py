import os
import glob
import subprocess
import json
import pandas as pd
from tqdm import tqdm

# --- PATHS ---
OPENFACE_EXE = r"" #Root path to the OpenFace executable (e.g., FaceLandmarkVidMulti.exe)
OPENFACE_ROOT = r"" #Root path to the OpenFace installation directory
UCF101_ROOT = r"" #Root path to the UCF101 dataset (where the videos are stored)
OUTPUT_ROOT = r"" #Root path to the output directory for OpenFace results

if __name__ == "__main__":
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    # 1. Gather Videos
    search_pattern = os.path.join(UCF101_ROOT, "**", "*_c01.*")
    videos = glob.glob(search_pattern, recursive=True)
    print(f"Found {len(videos)} videos. Running in batches to dramatically speed up extraction...")

    # 2. Run OpenFace in Batches
    CHUNK_SIZE = 40

    for i in tqdm(range(0, len(videos), CHUNK_SIZE), desc="OpenFace Batches", unit="batch"):
        batch = videos[i:i + CHUNK_SIZE]

        # Build command: FaceLandmarkVidMulti.exe -f vid1 -f vid2 ... -out_dir out -simalign
        cmd = [OPENFACE_EXE]
        for vid in batch:
            cmd.extend(["-f", vid])
        cmd.extend(["-out_dir", OUTPUT_ROOT, "-simalign"])

        # Suppress output to keep progress bar clean
        subprocess.run(cmd, cwd=OPENFACE_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("\nFeature extraction complete! Calculating statistics...")

    # 3. Calculate Statistics from the generated CSVs
    successful_vids, failed_vids, all_stats = [], [], []

    for vid_path in tqdm(videos, desc="Reading CSVs & Generating Report", unit="vid"):
        vid_id = os.path.splitext(os.path.basename(vid_path))[0]
        csv_path = os.path.join(OUTPUT_ROOT, f"{vid_id}.csv")

        stats = {
            "video_id": vid_id, "status": "failed", "num_faces": 0,
            "mean_conf_per_face": {}, "potential_false_positives": []
        }

        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                df.columns = df.columns.str.strip()

                if not df.empty and 'face_id' in df.columns:
                    stats["status"] = "success"
                    valid_faces = df[df['success'] == 1]
                    stats["num_faces"] = int(valid_faces['face_id'].nunique())

                    conf_means = valid_faces.groupby('face_id')['confidence'].mean().to_dict()
                    stats["mean_conf_per_face"] = {int(k): float(v) for k, v in conf_means.items()}

                    stats["potential_false_positives"] = [
                        int(f_id) for f_id, conf in conf_means.items() if conf < 0.60
                    ]
            except Exception:
                pass  # Unreadable or corrupted CSV counts as a fail

        all_stats.append(stats)
        if stats["status"] == "success":
            successful_vids.append(vid_id)
        else:
            failed_vids.append(vid_id)

    # 4. Save Final Output Format
    final_report = {
        "total_processed": len(videos), "total_successful": len(successful_vids),
        "total_failed": len(failed_vids), "successful_video_ids": successful_vids,
        "failed_video_ids": failed_vids, "video_statistics": all_stats
    }

    report_path = os.path.join(OUTPUT_ROOT, "openface_statistics_report.json")
    with open(report_path, "w") as f:
        json.dump(final_report, f, indent=4)

    print(f"\nDone! Stats saved to: {report_path}")