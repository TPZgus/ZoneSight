import shutil
import os

files_to_copy = [
    ('hyperparams.yaml', 'hyperparams.yaml'),
    ('embedding_model.ckpt', 'embedding_model.ckpt'),
    ('mean_var_norm_emb.ckpt', 'mean_var_norm_emb.ckpt'),
    ('classifier.ckpt', 'classifier.ckpt'),
    ('label_encoder.txt', 'label_encoder.ckpt')
]

src_base = r'C:\Users\gusni\.cache\huggingface\hub\models--speechbrain--spkrec-ecapa-voxceleb\snapshots\eac27266f68caa806381260bd44ace38b136c76a'
dst_base = r'C:\Users\gusni\.cache\torch\pyannote\speechbrain'

for src_file, dst_file in files_to_copy:
    src = os.path.join(src_base, src_file)
    dst = os.path.join(dst_base, dst_file)
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"File {src_file} copied successfully as {dst_file}")
    except Exception as e:
        print(f"An error occurred while copying {src_file}: {e}")

print("All files copied. Please try running the diarization test again.")