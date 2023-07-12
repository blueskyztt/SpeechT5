set -x
set -euo pipefail

download_model_spe_dir="./speecht5"
model_spe_hub_name="microsoft/speecht5_tts"

download_model_hif_dir="./hifigan"
model_hif_hub_name="microsoft/speecht5_hifigan"


function download_model_spe() {
  python ./Download_model.py \
    --model_name ${model_spe_hub_name} \
    --local_dir ./${download_model_spe_dir}
}

#hifigan
function download_model_hif() {
  python ./Download_model.py \
    --model_name ${model_hif_hub_name} \
    --local_dir ./${download_model_hif_dir}
}



download_model_spe

download_model_hif












