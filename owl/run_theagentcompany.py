import os
import json
from typing import List
import yaml
import time

from camel.models import ModelFactory
from camel.toolkits import (
    CodeExecutionToolkit,
    DocumentProcessingToolkit,
    ExcelToolkit,
    ImageAnalysisToolkit,
    WebToolkit,
)
from camel.types import ModelPlatformType

from owl.camel.toolkits.audio_analysis_toolkit import AudioAnalysisToolkit
from owl.camel.toolkits.search_toolkit import SearchToolkit
from owl.camel.toolkits.video_analysis_toolkit import VideoAnalysisToolkit
from utils import OwlRolePlaying, run_society


def construct_society(question: str) -> OwlRolePlaying:
    r"""Construct a society of agents based on the given question.
    
    Args:
        question (str): The task or question to be addressed by the society.
        
    Returns:
        OwlRolePlaying: A configured society of agents ready to address the question.
    """
    
    model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
            model_type=os.getenv("MODEL_TYPE"),
            api_key=os.getenv("API_KEY"),
            url="https://cmu.litellm.ai",
            model_config_dict={"temperature": 0},
        ) 
    
    # the following tools are not necessarily needed for the task, but they are included
    # here because they are the set of tools for GAIA evaluation by OWL
    web_toolkit = WebToolkit(
        headless=True,  # Set to True for headless mode (e.g., on remote servers)
        web_agent_model=model,
        planning_agent_model=model,
    )
    tools = [
        *web_toolkit.get_tools(),
        *DocumentProcessingToolkit().get_tools(),
        *VideoAnalysisToolkit(model=model).get_tools(),  # This requires OpenAI Key
        *AudioAnalysisToolkit().get_tools(),  # This requires OpenAI Key
        *CodeExecutionToolkit(sandbox="subprocess", verbose=True).get_tools(),
        *ImageAnalysisToolkit(model=model).get_tools(),
        *SearchToolkit(model=model).get_tools(),
        *ExcelToolkit().get_tools(),
    ]
    
    # Configure agent roles and parameters
    user_agent_kwargs = {"model": model}
    assistant_agent_kwargs = {"model": model, "tools": tools}
    
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
    
    return society, web_toolkit


def pre_login(web_toolkit: WebToolkit, dependencies: List[str]):
    r"""Pre-login to the websites.
    
    Args:
        web_toolkit (WebToolkit): The web toolkit to use.
        dependencies (List[str]): The dependencies to use.
    """ 
    for dependency in dependencies:
        if dependency == "owncloud":
            web_toolkit.browser.visit_page("http://the-agent-company.com:8092")
            web_toolkit.browser.get_interactive_elements()
            time.sleep(1)
            web_toolkit.browser.fill_input_id(34, "theagentcompany")
            time.sleep(1)
            web_toolkit.browser.fill_input_id(35, "theagentcompany")
            time.sleep(1)
            print("login to owncloud successfully")
        elif dependency == "rocketchat":
            web_toolkit.browser.visit_page("http://the-agent-company.com:3000")
            web_toolkit.browser.get_interactive_elements()
            time.sleep(1)
            web_toolkit.browser.fill_input_id(30, "theagentcompany")
            time.sleep(1)
            web_toolkit.browser.fill_input_id(31, "theagentcompany")
            time.sleep(1)
            print("login to rocketchat successfully")
        elif dependency == "gitlab":
            web_toolkit.browser.visit_page("http://the-agent-company.com:8929")
            web_toolkit.browser.get_interactive_elements()
            time.sleep(1)
            web_toolkit.browser.fill_input_id(27, "root@local")
            time.sleep(1)
            web_toolkit.browser.fill_input_id(30, "theagentcompany")
            time.sleep(1)
            print("login to gitlab successfully")
        elif dependency == "plane":
            web_toolkit.browser.visit_page("http://the-agent-company.com:8091")
            web_toolkit.browser.get_interactive_elements()
            time.sleep(1)
            web_toolkit.browser.fill_input_id(20, "agent@company.com")
            time.sleep(1)
            web_toolkit.browser.get_interactive_elements()
            web_toolkit.browser.fill_input_id(27, "theagentcompany")
            print("login to plane successfully")


def main():
    instruction = 'Complete the task in /instruction/task.md' 

    instruction = 'Complete the following task:\n'
    with open('/instruction/task.md', 'r') as f:
        instruction += f.read()

    instruction += '\n\nIMPORTANT: If there are the-agent-company.com websites mentioned in the task description, NOTE that these websites are privately hosted.\n'
    instruction += (
        'IMPORTANT: If you want to close pop-ups, please press the escape key.\n'
    )
    instruction += 'IMPORTANT: You should NEVER ask for Human Help.\n'

    # load web dependencies
    dependencies = []
    with open('/utils/dependencies.yml', 'r') as f:
        dependencies = yaml.safe_load(f)
    print(f'dependencies: {dependencies}')

    # why can't we cache the login information? Unfortunately, OWL doesn't persist browser sessions
    # (every browser_simulation always starts from a clean state), so it has to login repeatedly.
    if dependencies:
        instruction += '\n\nIMPORTANT: You should use the following credentials to access the following services:\n'
    if 'owncloud' in dependencies:
        instruction += '\n\n' + 'ownCloud Username: theagentcompany, Password: theagentcompany'
    if 'rocketchat' in dependencies:
        instruction += '\n\n' + 'RocketChat Username: theagentcompany, Password: theagentcompany'
    if 'gitlab' in dependencies:
        instruction += '\n\n' + 'GitLab Username: root, Password: theagentcompany'
    if 'plane' in dependencies:
        instruction += '\n\n' + 'Plane Email: agent@company.com, Password: theagentcompany'
    
    # Construct the society
    society, web_toolkit = construct_society(instruction)
    web_toolkit.browser.init()

    # Login to the websites
    pre_login(web_toolkit, dependencies)

    # Run the society
    _, chat_history, token_count = run_society(society, round_limit=1)

    # save chat history and token count to /output/chat_history.json and /output/token_count.json
    with open('/output/chat_history.json', 'w') as f:
        json.dump(chat_history, f)
    with open('/output/token_count.json', 'w') as f:
        json.dump(token_count, f)


if __name__ == "__main__":
    main()
