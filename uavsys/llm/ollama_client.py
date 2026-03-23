import ollama
from ollama import Client
from ..config import Config
from ..utils.richlog import RichLog, console

class OllamaClient:
    def __init__(self, config: Config):
        self.host = config.OLLAMA_HOST
        self.chat_model = config.CHAT_MODEL
        self.embed_model = config.EMBED_MODEL
        self.client = Client(host=self.host)

    async def chat(self, messages: list[dict], temperature: float = 0.0, **kwargs) -> str:
        """
        Chats with the model and streams output to the Rich console.
        Returns the full response string.
        """
        
        full_response = ""
        try:
            # We use the synchronous client in async wrapper, or use asyncio.to_thread?
            # ollama-python has an AsyncClient since 0.1.6, let's use it if possible.
            # But the user snippet used `chat` (sync). 
            # Let's try AsyncClient.
            
            from ollama import AsyncClient
            aclient = AsyncClient(host=self.host)
            
            # Options
            options = {
                "temperature": temperature,
                "seed": 0
            }

            stream = await aclient.chat(
                model=self.chat_model,
                messages=messages,
                options=options,
                stream=True,
                **kwargs
            )
            
            
            async for chunk in stream:
                content = chunk['message']['content']
                full_response += content
            
            return full_response

        except Exception as e:
            RichLog.error("Ollama", f"Chat failed: {e}")
            raise

    async def embed(self, texts: list[str]) -> list[list[float]]:
        try:
             # ollama.embed returns {'embeddings': [[...], ...]}
             from ollama import AsyncClient
             aclient = AsyncClient(host=self.host)
             
             resp = await aclient.embed(model=self.embed_model, input=texts)
             return resp['embeddings']
        except Exception as e:
            RichLog.error("Ollama", f"Embedding failed: {e}")
            raise
