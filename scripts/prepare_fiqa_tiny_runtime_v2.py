"""One dependency-only compatibility revision; preserve failed v1 unchanged."""
import sys
import prepare_fiqa_tiny_runtime as runtime
runtime.OUT=runtime.ROOT/'outputs/fiqa_tiny_runtime_v2'
# Author's safetensors0.4.5 has no compatible CPython3.13 Windows binary.
# The chosen checkpoint is .pth and still uses torch's weights_only loader.
runtime.PACKAGES=dict(runtime.PACKAGES,safetensors='0.5.3')
if __name__=='__main__':{'download':runtime.download,'install':runtime.install}[sys.argv[1]]()
