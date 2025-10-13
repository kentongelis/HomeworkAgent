import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables from .env file
load_dotenv()

# At this point, OPENAI_API_KEY should be in the environment
api_key = os.getenv("OPENAI_API_KEY")

model = init_chat_model("gpt-4o-mini", model_provider="openai")
# messages = [
#     SystemMessage(content="Translate the following from English to Russian"),
#     HumanMessage(content="Hello"),
# ]

system_template = "Translate the following from English into {language}"

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

prompt = prompt_template.invoke({"language": "Russian", "text": "hi!"})

response = model.invoke(prompt)

print(response.content)
