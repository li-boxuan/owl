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
            url=os.getenv("MODEL_BASE_URL"),
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
    def find_key_by_tag_name(elements_dict, target_tag_name):
        for key, value in elements_dict.items():
            if value.get('tag_name') == target_tag_name:
                return key
        raise ValueError(f"No element with tag name {target_tag_name} found")

    for dependency in dependencies:
        if dependency == "owncloud":
            web_toolkit.browser.visit_page("http://the-agent-company.com:8092")
            elements = web_toolkit.browser.get_interactive_elements()
            time.sleep(1)
            web_toolkit.browser.fill_input_id(find_key_by_tag_name(elements, "input, type=text"), "theagentcompany")
            time.sleep(1)
            web_toolkit.browser.fill_input_id(find_key_by_tag_name(elements, "input, type=password"), "theagentcompany")
            time.sleep(1)
            assert web_toolkit.browser.get_url().startswith("http://the-agent-company.com:8092/index.php/apps/files")
            print("login to owncloud successfully")
            web_toolkit.browser.get_screenshot()
        elif dependency == "rocketchat":
            web_toolkit.browser.visit_page("http://the-agent-company.com:3000")
            elements = web_toolkit.browser.get_interactive_elements()
            time.sleep(1)
            web_toolkit.browser.fill_input_id(find_key_by_tag_name(elements, "input, type=text"), "theagentcompany")
            time.sleep(1)
            web_toolkit.browser.fill_input_id(find_key_by_tag_name(elements, "input, type=password"), "theagentcompany")
            time.sleep(1)
            assert web_toolkit.browser.get_url() == "http://the-agent-company.com:3000/home"
            print("login to rocketchat successfully")
            web_toolkit.browser.get_screenshot()
        elif dependency == "gitlab":
            web_toolkit.browser.visit_page("http://the-agent-company.com:8929")
            elements = web_toolkit.browser.get_interactive_elements()
            time.sleep(1)
            web_toolkit.browser.fill_input_id(find_key_by_tag_name(elements, "input, type=text"), "root@local")
            time.sleep(1)
            web_toolkit.browser.fill_input_id(find_key_by_tag_name(elements, "input, type=password"), "theagentcompany")
            time.sleep(1)
            assert web_toolkit.browser.get_url() == "http://the-agent-company.com:8929/"
            print("login to gitlab successfully")
            web_toolkit.browser.get_screenshot()
        elif dependency == "plane":
            web_toolkit.browser.visit_page("http://the-agent-company.com:8091")
            elements = web_toolkit.browser.get_interactive_elements()
            time.sleep(5)
            web_toolkit.browser.get_screenshot()
            web_toolkit.browser.fill_input_id(find_key_by_tag_name(elements, "input, type=email"), "agent@company.com")
            time.sleep(30)
            elements = web_toolkit.browser.get_interactive_elements()
            web_toolkit.browser.get_screenshot()
            print(f'elements: {elements}')
            web_toolkit.browser.scroll_to_top()
            time.sleep(30)
            try:
                find_key_by_tag_name(elements, "input, type=password")
            except Exception as e:
                print(f'Password input not found, try clicking on continue button')
                button_id = find_key_by_tag_name(elements, "button")
                print(f'button_id: {button_id}')
                web_toolkit.browser.click_id(button_id)
                time.sleep(5)
                web_toolkit.browser.get_screenshot()
                elements = web_toolkit.browser.get_interactive_elements()
                print(f'elements: {elements}')
            try:
                find_key_by_tag_name(elements, "input, type=password")
            except Exception as e:
                print(f'Password input not found, try pressing enter')
                web_toolkit.browser.page.keyboard.press("Enter")
                time.sleep(5)
                web_toolkit.browser.get_screenshot()
                elements = web_toolkit.browser.get_interactive_elements()
                print(f'elements: {elements}')
            web_toolkit.browser.fill_input_id(find_key_by_tag_name(elements, "input, type=password"), "theagentcompany")
            time.sleep(5)
            assert web_toolkit.browser.get_url() == "http://the-agent-company.com:8091/tac/"
            print("login to plane successfully")
            web_toolkit.browser.get_screenshot()


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

    if not dependencies:
        dependencies = []

    if 'gitlab' in dependencies:
        instruction += "IMPORTANT: You are already signed in to Gitlab, but here are the sign-in credentials for your reference - Gitlab username is 'root' and password is 'theagentcompany'\n"

    
    # Construct the society
    society, web_toolkit = construct_society(instruction)
    web_toolkit.browser.init()

    # Login to the websites
    try:
        pre_login(web_toolkit, dependencies)
    except Exception as e:
        print(f'Error logging in to the websites: {e}')
        raise e

    # Run the society
    _, chat_history, token_count = run_society(society)

    print('#### Finished task ####')

    # save chat history and token count to ./output/chat_history.json and ./output/token_count.json
    os.makedirs('./output', exist_ok=True)
    with open('./output/chat_history.json', 'w') as f:
        json.dump(chat_history, f)
    with open('./output/token_count.json', 'w') as f:
        json.dump(token_count, f)

    # gracefully close the browser
    web_toolkit.browser.browser.close()
    web_toolkit.browser.playwright.stop()


if __name__ == "__main__":
    main()
