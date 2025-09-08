"""OpenAI client configuration and utilities."""

import os
from typing import Optional, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

class OpenAIClient:
    """Wrapper for OpenAI API client."""
  
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client with API key."""
        self.n_calls = 0
        self.cost = 0.0
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-5"  # Default model
        self.config = {
            "model": self.model,
        }
    
    def _query(self, messages: list[dict[str, str]], max_tokens: int = 10000, **kwargs):
        try:
            return self.client.responses.create(
                model=self.model,
                input=messages,
                max_output_tokens=max_tokens,
            )
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")   
       
    def cost_calculator(self, response: dict):
        input_token = response.usage.input_tokens
        output_token = response.usage.output_tokens

        if (self.model == "gpt-5"):
            input_cost = input_token * 0.00000125
            output_cost = output_token * 0.00001
        elif (self.model == "gpt-5-mini"):
            input_cost = input_token * 0.00000025
            output_cost = output_token * 0.000002
        elif (self.model == "gpt-5-nano"):
            input_cost = input_token * 0.00000005
            output_cost = output_token * 0.0000004
        else:
            raise Exception(f"Model {self.model} not supported")
        return input_cost + output_cost
    
        
    def query(self, messages: list[dict[str, str]], **kwargs) -> dict:
       
        response = self._query(messages, **kwargs)
        self.n_calls += 1
        self.cost += self.cost_calculator(response)
        
        return {
            "content": response.output_text or "", 
        } 
   
    def get_template_vars(self) -> dict[str, Any]:
        return {"n_model_calls": self.n_calls, "model_cost": self.cost, "model": self.model}
    