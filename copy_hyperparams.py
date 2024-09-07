import shutil
import os

src = r'C:\Users\gusni\.cache\huggingface\hub\models--speechbrain--spkrec-ecapa-voxceleb\snapshots\eac27266f68caa806381260bd44ace38b136c76a\hyperparams.yaml'
dst = r'C:\Users\gusni\.cache\torch\pyannote\speechbrain\hyperparams.yaml'

try:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print("File copied successfully")
except Exception as e:
    print(f"An error occurred: {e}")