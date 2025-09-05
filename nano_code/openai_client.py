"""OpenAI client configuration and utilities."""

import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)


class OpenAIClient:
    """Wrapper for OpenAI API client."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client with API key."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-5-mini"  # Default model
    
    def chat_completion(self, messages: list, max_tokens: int = 1000) -> str:
        """Get chat completion from OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    def generate_code(self, description: str, language: str = "python") -> str:
        """Generate code using OpenAI."""
        prompt = f"""Generate {language} code for the following description:

{description}

Requirements:
- Write clean, well-documented code
- Include docstrings/comments where appropriate  
- Follow best practices for {language}
- Return only the code, no additional explanation

Code:"""
        
        messages = [
            {"role": "system", "content": "You are an expert programmer. Generate clean, production-ready code."},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat_completion(messages, max_tokens=1500)
    
    def analyze_code(self, code: str, file_path: str = "") -> str:
        """Analyze code using OpenAI."""
        prompt = f"""Analyze the following code{f' from {file_path}' if file_path else ''}:

```
{code}
```

Provide analysis including:
- Code structure and organization
- Potential issues or bugs
- Suggestions for improvement
- Code quality assessment
- Performance considerations

Analysis:"""
        
        messages = [
            {"role": "system", "content": "You are an expert code reviewer. Provide detailed, constructive analysis."},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat_completion(messages, max_tokens=1000)
    
    def chat_response(self, user_input: str, context: str = "") -> str:
        """Generate chat response using OpenAI."""
        system_prompt = """You are a helpful coding assistant. You can:
- Help with coding questions and problems
- Explain code concepts
- Debug issues
- Suggest improvements
- Generate code snippets

Be concise but helpful. Focus on practical solutions."""

        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
        
        messages.append({"role": "user", "content": user_input})
        
        return self.chat_completion(messages)