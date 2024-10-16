import sys
import os

# Assuming the common folder is one level up
parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(parent_dir)
print(parent_dir)

from common.azure_openai_imports import *



class PaypalHelpAgentAMessage(BaseModel):
    body: LLMMessage


@type_subscription(topic_type="paypal_help_topic")
class PaypalHelpAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient):
        super().__init__("A Paypal Help Agent")        
        self._model_client = model_client
        self._system_message = SystemMessage(
        """
        You are a Paypal Help Agent. You can help users with their Paypal related queries. 
        You need to respond only to queries related to Paypal and nothing else. 
        If the question is not related to Paypal, state that you only respond to Paypal related queries and cannot answer this question.        

        """)
        self._chat_history : List[LLMMessage]  = [self._system_message]

    @message_handler
    async def respond_to_user_question(self, message: PaypalHelpAgentAMessage, context: MessageContext) -> str:
        self._chat_history.append(message.body)
        completion = await self._model_client.create(self._chat_history)
        self._chat_history.extend([AssistantMessage(content=f"{completion.content}", source="PaypalHelpAgent")])
        return completion.content

runtime = SingleThreadedAgentRuntime()

async def register_agents(runtime):

    await PaypalHelpAgent.register(
        runtime, 
        "PaypalHelpAgent",
        lambda: PaypalHelpAgent(get_model_client())
    )


#asyncio.run(register_agents(runtime))

async def run_agents():
    runtime.start()
    agent_response = await runtime.send_message(PaypalHelpAgentAMessage(body=UserMessage(content="What are payment reversals and how to avoid them", source="user")), recipient=AgentId(type="PaypalHelpAgent", key="paypal_user1")) 
    print(agent_response)
#    agent_response = await runtime.send_message(PaypalHelpAgentAMessage(body=UserMessage(content="Plan a 3 day road trip to zion national park", source="user")), recipient=AgentId(type="PaypalHelpAgent", key="paypal_user1")) 
#    print(agent_response)
#    agent_response = await runtime.send_message(PaypalHelpAgentAMessage(body=UserMessage(content="how to report Fraud", source="user")), recipient=AgentId(type="PaypalHelpAgent", key="paypal_user1")) 
#    print(agent_response)
#
#asyncio.run(run_agents())