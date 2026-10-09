# Run ollama on GH01

## Install

Grab 



## Run

PATH="/srv/nvme1/dobos/opt/bin:$PATH" LD_LIBRARY_PATH="/srv/nvme1/dobos/opt/lib/ollama:$LD_LIBRARY_PATH" OLLAMA_MODELS=/srv/nvme1/dobos/ollama ollama serve

PATH="/srv/nvme1/dobos/opt/bin:$PATH" LD_LIBRARY_PATH="/srv/nvme1/dobos/opt/lib/ollama:$LD_LIBRARY_PATH" OLLAMA_MODELS=/srv/nvme1/dobos/ollama ollama pull qwen3-coder:30b
PATH="/srv/nvme1/dobos/opt/bin:$PATH" LD_LIBRARY_PATH="/srv/nvme1/dobos/opt/lib/ollama:$LD_LIBRARY_PATH" OLLAMA_MODELS=/srv/nvme1/dobos/ollama ollama run qwen3-coder:30b


```
OLLAMA_LOAD_TIMEOUT
```