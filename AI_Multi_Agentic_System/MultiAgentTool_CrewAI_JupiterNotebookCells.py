#!/usr/bin/env python
# coding: utf-8

# Title: AI Multi-Agent System for Automatic Code Review
# 
# Objective: This AI tool is used in CI/CD pipline for automatic evalutation of pull request reports. 
# 
# Procedure to run: The code should be run in Jupiter Notebook cells. The workflow consists of several parts that can be 
# secuentionally run. An example of pull request report is the file code_changes.txt. This file is contains the output of 
# of command:    diff--git a/app/user_auth.py b/app/user_auth.py
# 
#
# 
# ## Part 1 Set up your notebook
# 
# Begin by importing all necessary modules and configuring your environment variables to connect to the LLM APIs. 
# 
# If you're running the Jupiter Notebook on your own machine, you should install the following:
# 
# !pip install crewai[tools]==1.3.0
# Run the following cell to import all the modules you will need for this lab. 
#
# In[1]:


# Patch to disable SSL verification for Coursera
from patch import disable_ssl_verification
disable_ssl_verification()

from crewai import Agent, Task, Crew
import dill
import unittests


# Next, set up the environment variables to connect to the APIs, and  create the LLM instance for Agents

# In[2]:


import os
os.environ["CREWAI_TESTING"] = "true"
from utils import get_openai_api_key

# set up the OpenAI API key 
os.environ["OPENAI_API_KEY"] = get_openai_api_key()
# set up the OpenAI model to use
os.environ["MODEL"] = 'gpt-4o-mini'


# Show the file `code_changes.txt`.

# In[3]:


# read and save the content
with open('code_changes.txt', 'r') as file:
    code_changes = file.read()
print(code_changes)



 
# ## Part 2 - Define the elements for the Crew
#
# Define three agents: 
# 
# - **Senior Developer**: A technical expert who examines code for style issues, potential bugs, and maintainability concerns, deciding which issues need to be addressed before approval. 
#      
# - **Security Engineer**: A security specialist who evaluates code changes for potential vulnerabilities, determining the risk level and whether security issues block approval. 
#      
# - **Tech Lead**: A decision-making leader who evaluates the findings from other agents, determines if a pull request can be automatically approved or needs human review, and provides final recommendations. 
# 
# 
# ### 2.1 Providing tools to agents
# This is needed to allow agents to connect to the external world. 
# 
# Grant the **Security Engineer** access to the **[OWASP](https://owasp.org)** webpage.
# 
# 
# Create an instance of each of the following tools:
# 1. [**`SerperDevTool`**](https://docs.crewai.com/en/tools/search-research/serperdevtool). 
# Use this tools to search within the OWASP webpage and retrieve the most relevant URLs for current problem. It is necessary to set the `search_url` to the OWASP URL. 
# 
# 2. [**`ScrapeWebsiteTool`**](https://docs.crewai.com/en/tools/web-scraping/scrapewebsitetool). This tool retrieves all the information from each of the identified websites. 
# 
# `SerperDevTool` works similarly to the `ExaSearchTool`. It is designed to perform a semantic search for a specified query from a text’s content across the internet. 
# It uses the serper.dev API to fetch and display the most relevant search results based on the query provided by the user. 

# In[5]:


# import the required tools
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
# get the Serper API key
from utils import get_serper_api_key
serper_api_key = get_serper_api_key()

# create the instance of the SerperDevTool. Set the search_url to "https://owasp.org"
serper_search_tool = SerperDevTool(search_url="https://owasp.org", base_url=os.getenv("DLAI_SERPER_BASE_URL"))

# create the instance of the ScrapeWebsiteTool, does not need any arguments
scrape_website_tool = ScrapeWebsiteTool()

# In[6]:


# test the tools
unittests.test_tools(serper_search_tool, scrape_website_tool)

# 
# ### 2.2 Define the agents
# 
# Define each agent. Specify four arguments 
# - `role`: Their job title or function, 
# - `goal`: What they aim to achieve
# - `backstory`: Their experience and expertise (helps the LLM understand how to roleplay the agent)
# - `verbose`: Whether to show detailed output (useful for learning and debugging)
# 
# Additionally, for the **Security Engineer** agent, there is a need to assign the tools using the `tools` argument. 
# 
# 

# In[7]:


# Create the senior developer agent
senior_developer = Agent(
    role="Senior Developer",
    goal="Evaluate code changes to identify style issues, potential bugs, and maintainability concerns, deciding which issues need to be addressed before approval.",
    backstory=(
        "You are a seasoned senior software developer with years of experience. "
        "You specialize in examining code for style issues, potential bugs, and maintainability concerns. "
        "You have a sharp eye for detail and excel at distinguishing between critical problems that "
        "require immediate fixing and minor issues that can be overlooked."
    ),
            
    # set verbose suggested
    verbose=True,
)

# In[8]:


# test the senior developer agent
unittests.test_senior_developer_agent(senior_developer)


# **Security Engineer agent**.
# 
# Create an agent specialized in security analysis by:
# 
# - Setting a `role` that reflects expertise in code security evaluation.
# - Defining a `goal` focused on identifying vulnerabilities and determining risk levels.
# - Writing a `backstory` that emphasizes decision-making about security issues.
# - Assigning already created tools 
# 
# Make sure the agent understands it should judge the severity of security concerns. 

# In[9]:


# Create the security engineer agent
security_engineer = Agent(
    role="Security Engineer",
    goal="Evaluate code changes for potential vulnerabilities, determining the risk level and whether the security issues block approval",
    backstory=( 
        "You are an expert security specialist focused on protecting software systems. "
        "You meticulously evaluate code changes for security vulnerabilities, assess risk levels, "
        "and judge the severity of any security concerns to decide whether they should block code approval."        
    ),
            
    # set verbose 
    verbose=True,
    # assign the tools
    tools=[serper_search_tool, scrape_website_tool],
)

# In[10]:


# test the security engineer agent
unittests.test_security_engineer_agent(security_engineer)


# **Tech Lead agent**.
# 
# Create an agent specialized in review coordination by:
# 
# - Setting a `role` that reflects expertise in managing code review processes.
# - Defining a `goal` focused on determining approval paths for code changes.
# - Writing a `backstory` that emphasizes decision-making about review workflows.
# 
# Make sure the agent understands it should make final judgments about approval or escalation.

# In[11]:


# Create the tech lead agent
tech_lead = Agent(
    role="Tech Lead",
    goal="Evaluate findings from other agents, determine if a pull request can be automatically approved or needs human review, and provide final recommendations",
    backstory=(
            "You are a decisive tech lead managing the code review process. "
            "You evaluate findings from other agents, oversee the review workflow, and make final judgments on whether a pull request can be automatically approved, needs fixes, or must be escalated to a human reviewer."            
        ),
        
    verbose=True,
)

# In[12]:


# test the tech lead agent
unittests.test_tech_lead_agent(tech_lead)


# 
# ### 2.3 Define the Tasks for each Agent
# 
# Now that the agents are set, we need to define the tasks each of them will perform. 
# 
# - **Quality Analysis Task**: Evaluate code changes for style, bugs, and maintainability, deciding which issues must be fixed before approval. 
#      
# - **Security Review Task**: Examine code for security vulnerabilities, determining risk levels and whether security issues should block approval. 
#      
# - **Review Decision Task**: Analyze the quality and security findings to decide if changes can be automatically approved, need specific fixes, or require human review. 
# 
# #### General guidelines for creating Tasks:
# When creating a task, we need to define these key parameters:
# 
# - `description`: A clear explanation of what the task involves
# - `expected_output`: The format and content the task should produce
# - `agent`: Which agent will perform this task
# - `context` (optional): Define what tasks' output, including multiple, should be used as context for another task. See [docs](https://docs.crewai.com/en/concepts/tasks#referring-to-other-tasks). 
# ### Create Quality Analysis Task
# 
# **Quality Analysis task**.
# 
# Tast for code quality evaluation by:
# - Writing a `description` with steps instructing the agent to review code, identify potential bugs or issues, and decide if the issues are critical or minor.
#     - The task should read the code changes from the provided `code_changes`.
# - Specify the `expected_output` - `JSON` with keys:
#     - `critical_issues`: array of issues that must be fixed
#     - `minor_issues`: array of suggested improvements
#     - `reasoning`: explanation of decisions
# - Assign the task to the **Senior Developer** agent.

# In[13]:


# Create the quality analysis task
analyze_code_quality = Task(
    description=( 
        "Review the provided code changes and analyze them for style issues, potential bugs, "
        "and maintainability concerns. Determine whether each identified issue is critical "
        "(must be fixed before approval) or minor (suggested improvements). "
        "Code changes:\n{code_changes}"
    ),
    
    expected_output=(
        "A JSON object containing exactly these keys: "
        "'critical_issues' (an array of issues that must be fixed), "
        "'minor_issues' (an array of suggested improvements), and "
        "'reasoning' (an explanation of the decisions made)."
    ),
    
    name="Analyze Code Quality", 
    agent=senior_developer
)

# In[14]:


# test the quality analysis task
unittests.test_analyze_code_quality_task(analyze_code_quality)


# 
# **Security Review task**.
# 
# Tast for security evaluation:
# - Description - with steps instructing the agent to examine code for vulnerabilities, identify security issues, determine risk levels, and decide if issues should block approval.
#     - The task should read the code changes from the provided `code_changes`.
# - Specify the `expected_output - `JSON` with keys:
#     - `security_vulnerabilities`: array of identified issues with risk levels
#     - `blocking`: boolean indicating if security issues should block approval
#     - `highest_risk`: the most severe risk level found
#     - `security_recommendations`: specific fixes for vulnerabilities
# - Assigning the task to the **Security Engineer** agent.

# In[15]:


# Create the security review task
review_security = Task(
    description=( 
        "Examine the provided code changes for security vulnerabilities, identify security issues, "
        "determine their risk levels, and decide if the issues should block approval. "
        "Code changes:\n{code_changes}\n"        
        # Add instructions for tool use to the task
        "Use the SerperDevTool to find the most relevant security best practices from OWASP"
        "and pass the URLs to the ScrapeWebsiteTool to get detailed information."
    ),
    
    expected_output=( 
        "A JSON object containing exactly these keys: "
        "'security_vulnerabilities' (an array of identified issues with risk levels), "
        "'blocking' (a boolean indicating if security issues should block approval), "
        "'highest_risk' (the most severe risk level found), and "
        "'security_recommendations' (specific fixes for vulnerabilities)."
    ),
    
    agent=security_engineer,
    name="Review Security",
)


# In[16]:


# test the review security task
unittests.test_review_security_task(review_security)

# 
# **Review Decision task**.
# 
# Description - steps instructing the agent to determine if the Pull Request can be approved, decide on next steps, explain the decision.
#     - The task should read the code changes from the provided `code_changes`.
# - Specify that the `expected_output` should be a short report that includes the final decision, required changes (if any), approval comments (if approving), escalation reasoning (if escalating), and additional recommendations.
# - Assign the task to the **Tech Lead** agent.
# - Assign `context` to the agent. The Review Decision task needs the output of both of the previous tasks to make the decision, so we need to pass both tasks as context.

# In[17]:


# Create the review decision task
make_review_decision = Task(
    description=( 
        "Analyze the findings from the quality analysis and security review tasks along with the original code changes "
        "to determine if the pull request can be approved, decide on next steps, and explain the decision clearly. "
        "Code changes:\n{code_changes}"        
    ),
   
    expected_output=(
        "A short report that includes the final decision, required changes (if any), "
        "approval comments (if approving), escalation reasoning (if escalating), "
        "and additional recommendations."
    ), 
    
    agent=tech_lead,
    # add the two previous tasks as context
    context=[analyze_code_quality, review_security],
    name="Review Decision",
)


# In[18]:


# test the review decision task
unittests.test_make_review_decision_task(make_review_decision)


# 
# ## Part 3 - Define and kick off the Crew
#
# Now that agents and tasks are set, we need to put it all together and create the Crew. 

# In[19]:


# Create the pull request review crew
crew = Crew(
    # add the list of agents
    agents=[senior_developer, security_engineer, tech_lead],
    # add the list of tasks    
    tasks=[analyze_code_quality, review_security, make_review_decision],
)


# In[20]:


# test the crew
unittests.test_crew(crew)


# Next, define all the inputs to kickoff the crew. Run the cell below to define the `inputs` dictionary with the `code_changes`, which you will then pass as context to the Crew.

# In[22]:


# define the inputs dictionary for the crew
inputs = {
    "code_changes": code_changes,
}


# ### Kickoff the Crew

# In[23]:

# kickoff the crew
result = crew.kickoff(inputs=inputs)


# Now check out the final report.

# In[24]:


from IPython.display import Markdown
Markdown(result.tasks_output[2].raw) 


# Run the cell below to save the results.

# In[25]:


with open("results.dill", "wb") as f:
    dill.dump(result, f)


# In[ ]:


from utils import get_dict_keys

# check the result of the first task

# Get the raw output
raw_output = result.tasks_output[0].raw

get_dict_keys(raw_output)


# Now check the second task (Review Security).

# In[ ]:


# check the result of the first task

# Get the raw output
raw_output = result.tasks_output[1].raw

# See if it can be parsed as a dictionary, and get the keys
get_dict_keys(raw_output)


