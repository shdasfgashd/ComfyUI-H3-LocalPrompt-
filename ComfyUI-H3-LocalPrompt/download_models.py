"""Run with ComfyUI's Python. Internet needed ONLY for initial download."""
import argparse
from pathlib import Path
from huggingface_hub import snapshot_download
p=argparse.ArgumentParser()
p.add_argument('--comfy-root', required=True)
p.add_argument('--audio', action='store_true')
a=p.parse_args()
base=Path(a.comfy_root).resolve()/'models'/'LLM'
snapshot_download('Qwen/Qwen3-VL-4B-Instruct',local_dir=str(base/'Qwen3-VL-4B-Instruct'))
if a.audio:
 snapshot_download('Systran/faster-whisper-small',local_dir=str(base/'faster-whisper-small'))
print('Downloaded complete model directories to',base)
