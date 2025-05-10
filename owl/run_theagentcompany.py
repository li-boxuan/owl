import os
import json
import yaml

from camel.models import ModelFactory
from camel.toolkits import (
    CodeExecutionToolkit,
    DocumentProcessingToolkit,
    ExcelToolkit,
    ImageAnalysisToolkit,
    WebToolkit,
)
from camel.types import ModelPlatformType

from utils import OwlRolePlaying, run_society


def construct_society(question: str) -> OwlRolePlaying:
    r"""Construct a society of agents based on the given question.
    
    Args:
        question (str): The task or question to be addressed by the society.
        
    Returns:
        OwlRolePlaying: A configured society of agents ready to address the question.
    """
    
    # Create models for different components
    models = {
        "user": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
            model_type="neulab/claude-3-7-sonnet-20250219",
            api_key=os.getenv("API_KEY"),
            url="https://cmu.litellm.ai",
            model_config_dict={"temperature": 0},
        ),
        "assistant": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
            model_type="neulab/claude-3-7-sonnet-20250219",
            api_key=os.getenv("API_KEY"),
            url="https://cmu.litellm.ai",
            model_config_dict={"temperature": 0},
        ),
        "web": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
            model_type="neulab/claude-3-7-sonnet-20250219",
            api_key=os.getenv("API_KEY"),
            url="https://cmu.litellm.ai",
            model_config_dict={"temperature": 0},
        ),
        "planning": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
            model_type="neulab/claude-3-7-sonnet-20250219",
            api_key=os.getenv("API_KEY"),
            url="https://cmu.litellm.ai",
            model_config_dict={"temperature": 0},
        ),
        "image": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
            model_type="neulab/claude-3-7-sonnet-20250219",
            api_key=os.getenv("API_KEY"),
            url="https://cmu.litellm.ai",
            model_config_dict={"temperature": 0},
        ),
    }
    
    # Configure toolkits
    web_toolkit = WebToolkit(
            headless=True,
            web_agent_model=models["web"],
            planning_agent_model=models["planning"],
        )
    tools = [
        *web_toolkit.get_tools(),
        *CodeExecutionToolkit(sandbox="subprocess", verbose=True).get_tools(),
        *ImageAnalysisToolkit(model=models["image"]).get_tools(),
        *ExcelToolkit().get_tools(),
        *DocumentProcessingToolkit().get_tools(),
    ]
    
    # Configure agent roles and parameters
    user_agent_kwargs = {"model": models["user"]}
    assistant_agent_kwargs = {"model": models["assistant"], "tools": tools}
    
    # Configure task parameters
    task_kwargs = {
        "task_prompt": question,
        "with_task_specify": False,
    }
    
    # Create and return the society
    society = OwlRolePlaying(
        **task_kwargs,
        user_role_name="user",
        user_agent_kwargs=user_agent_kwargs,
        assistant_role_name="assistant",
        assistant_agent_kwargs=assistant_agent_kwargs,
    )
    
    return society


def main():
    instruction = 'Complete the task in /instruction/task.md' 

    # load web dependencies
    dependencies = []
    with open('/utils/dependencies.yml', 'r') as f:
        dependencies = yaml.load(f)
    print(f'dependencies: {dependencies}')

    # why can't we cache the login information? Unfortunately, OWL doesn't persist browser sessions
    # (every browser_simulation always starts from a clean state), so it has to login repeatedly.
    if 'owncloud' in dependencies:
        instruction += '\n\n' + 'owncloud: Username: theagentcompany, Password: theagentcompany'
    if 'rocketchat' in dependencies:
        instruction += '\n\n' + 'rocketchat: Username: theagentcompany, Password: theagentcompany'
    if 'gitlab' in dependencies:
        instruction += '\n\n' + 'gitlab: Username: root, Password: theagentcompany'
    if 'plane' in dependencies:
        instruction += '\n\n' + 'plane: Email: agent@company.com, Password: theagentcompany'
    
    # Construct the society
    society = construct_society(instruction)

    # Run the society
    _, chat_history, token_count = run_society(society)

    # save chat history and token count to /output/chat_history.json and /output/token_count.json
    with open('/output/chat_history.json', 'w') as f:
        json.dump(chat_history, f)
    with open('/output/token_count.json', 'w') as f:
        json.dump(token_count, f)


if __name__ == "__main__":
    main()
