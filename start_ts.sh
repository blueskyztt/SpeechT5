set -x
set -euo pipefail

model_name="SpeechT5"

export JAVA_HOME=$(echo ${JAVA_HOME})

function start_serve() {
  torchserve \
    --start \
    --model-store "./model_store" \
    --models "./model_store/${model_name}.mar" \
    --ncs
}

start_serve
