# OWL-required dependency
apt-get update
apt-get install libgl1-mesa-glx -y

# Clone github repo
git clone https://github.com/li-boxuan/owl.git

# Change directory into project directory
cd owl

python -m venv owl_env
source owl_env/bin/activate

python -m pip install -r requirements.txt
playwright install
playwright install-deps

export MODEL_TYPE="neulab/gpt-4o-2024-08-06"
export MODEL_BASE_URL="https://cmu.litellm.ai"
export ENV_MODEL_TYPE="openai/neulab/claude-3-5-sonnet-20241022"

# Initialize TAC task environment
SERVER_HOSTNAME=localhost \
LITELLM_API_KEY=${ENV_API_KEY} \
LITELLM_BASE_URL=${MODEL_BASE_URL} \
LITELLM_MODEL=${ENV_MODEL_TYPE} \
bash /utils/init.sh


# run TAC task
python owl/run_theagentcompany.py

# run TAC evaluation
LITELLM_API_KEY=${ENV_API_KEY} \
LITELLM_BASE_URL=${MODEL_BASE_URL} \
LITELLM_MODEL=${ENV_MODEL_TYPE} \
DECRYPTION_KEY='theagentcompany is all you need' \
python_default /utils/eval.py --trajectory_path ./output/chat_history.json --result_path ./output/eval_result.json