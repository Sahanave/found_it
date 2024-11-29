# Building Generative AI Applications
## Prerequisite
Download [Visual Studio Code](https://code.visualstudio.com/) compatible with your operating system.

To use ElevenLabs, we need API key. Go to ElevenLabs and create an account. It's free! 🎉. And in the upper right corner click on your profile picture > profile. Next click on the eye icon and copy/save your API key.

To use LLMs, we need API key(s). During demo we are using Azure OpenAI and AWS Bedrock models. Both require a separate subscription of a cloud provider. You can use OpenAI API or any other LLM provider, just remember to update the blocks in langflow.

## Local development
### Python related
We are using poetry to manage packages, and conda to manage python virtual environments

Follow this guide to install [conda](https://conda.io/docs/user-guide/install/)

Once you have conda installed, we can create a new venv on conda using
```bash
conda env create -f environment.yaml
```
**Remember to keep the conda's environment.yml file clean, we keep dependencies on poetry.** If we need to upgrade python or poetry version - upgrade those in the `environment.yml` and recreate the environment.

We store the project python configuration in `pyproject.toml`
Especially python version
```yaml
[tool.poetry.dependencies]
python = "^3.12"
```

Run below command to install all dependencies
```bash
poetry install
```

Make sure the right python interpreter is selected

```bash
conda activate your_env_name
which python
poetry run which python
poetry shell
which python
```

### Install dependencies
```bash
poetry install
```

## Running in Docker
To run langflow you need to have three containers minimum:
* langflow
* postgres
* streamlit-app

**streamlit-app** is a custom application, hence you will need to build it first.
```bash
cd app/
docker build -t streamlit-app .
```

First two container uses `.env` file, that can be copied from `.env.template`, and should be filled accordingly.

Run then the below command

```bash
docker compose up -d
```

## Langflow

### Installing packages
Connect to the langflow container
```
docker exec -it app_langflow /bin/bash
```
Now run
```
which python
which pip3
```
If your answer is like below, we need to reinstall pip
```
/app/.venv/bin/python
/usr/local/bin/pip3
```
You need to make sure there is a right pip
```
source activate /app/.venv/bin/activate
python -m ensurepip --upgrade
which pip3
```
Now we should get 
```
/app/.venv/bin/pip3
```
Now you can install packages, for example to run tavily search
```
pip3 install tavily-python
```

## Ollama

We need to mamually pull models we would like to use on ollama, so once the container is up we can run
```
docker exec -it app_ollama /bin/bash
```
and now we can pull the models
```
ollama pull gemma2:2b
ollama pull nomic-embed-text
```
More about ollama models is on [their website](https://ollama.com/library/)