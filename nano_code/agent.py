"""Core coding agent logic."""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from .openai_client import OpenAIClient


class CodingAgent:
    """A simple coding agent for analyzing and generating code."""
    
    def __init__(self, use_openai: bool = True, api_key: Optional[str] = None):
        self.use_openai = use_openai
        self.openai_client = None
        
        if use_openai:
            try:
                self.openai_client = OpenAIClient(api_key)
            except ValueError as e:
                print(f"Warning: {e}")
                print("Falling back to basic mode without OpenAI.")
                self.use_openai = False
        
        self.supported_languages = {
            'python': self._analyze_python,
            'py': self._analyze_python,
            'javascript': self._analyze_generic,
            'js': self._analyze_generic,
            'java': self._analyze_generic,
            'cpp': self._analyze_generic,
            'c': self._analyze_generic,
        }
        
        self.code_templates = {
            'python': {
                'function': 'def {name}({params}):\n    """{description}"""\n    pass\n',
                'class': 'class {name}:\n    """{description}"""\n    \n    def __init__(self):\n        pass\n',
                'script': '#!/usr/bin/env python3\n"""{description}"""\n\ndef main():\n    pass\n\nif __name__ == "__main__":\n    main()\n'
            },
            'javascript': {
                'function': 'function {name}({params}) {{\n    // {description}\n    \n}}\n',
                'class': 'class {name} {{\n    // {description}\n    constructor() {{\n        \n    }}\n}}\n',
                'script': '// {description}\n\nfunction main() {{\n    \n}}\n\nmain();\n'
            }
        }
    
    def analyze_file(self, file_path: str) -> str:
        """Analyze a code file and provide insights."""
        path = Path(file_path)
        
        if not path.exists():
            return f"File {file_path} does not exist."
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            return f"Cannot read {file_path}: not a text file or encoding issue."
        
        # Use OpenAI for enhanced analysis if available
        if self.use_openai and self.openai_client:
            try:
                ai_analysis = self.openai_client.analyze_code(content, file_path)
                return ai_analysis
            except Exception as e:
                print(f"Warning: {e}")
                print("Falling back to basic analysis.")
                # Fall through to basic analysis
        
        # Fall back to basic analysis
        extension = path.suffix.lower().lstrip('.')
        analyzer = self.supported_languages.get(extension, self._analyze_generic)
        
        analysis = analyzer(content, file_path)
        
        return self._format_analysis(analysis, file_path)
    
    def _analyze_python(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze Python code specifically."""
        analysis = {
            'language': 'Python',
            'lines': len(content.splitlines()),
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity': 'low',
            'issues': []
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': len(node.args.args)
                    })
                elif isinstance(node, ast.ClassDef):
                    analysis['classes'].append({
                        'name': node.name,
                        'line': node.lineno
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis['imports'].append(node.module)
            
            # Simple complexity heuristic
            if len(analysis['functions']) > 10 or len(analysis['classes']) > 5:
                analysis['complexity'] = 'high'
            elif len(analysis['functions']) > 3 or len(analysis['classes']) > 1:
                analysis['complexity'] = 'medium'
                
        except SyntaxError as e:
            analysis['issues'].append(f"Syntax error: {e}")
        
        return analysis
    
    def _analyze_generic(self, content: str, file_path: str) -> Dict[str, Any]:
        """Generic code analysis for unsupported languages."""
        lines = content.splitlines()
        
        analysis = {
            'language': 'Generic',
            'lines': len(lines),
            'functions': [],
            'classes': [],
            'complexity': 'unknown',
            'issues': []
        }
        
        # Simple pattern matching for common constructs
        function_patterns = [
            r'function\s+(\w+)',  # JavaScript
            r'def\s+(\w+)',       # Python
            r'(\w+)\s*\([^)]*\)\s*{',  # C-style
        ]
        
        class_patterns = [
            r'class\s+(\w+)',
            r'struct\s+(\w+)',
        ]
        
        for i, line in enumerate(lines, 1):
            # Look for functions
            for pattern in function_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    analysis['functions'].append({
                        'name': match,
                        'line': i
                    })
            
            # Look for classes
            for pattern in class_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    analysis['classes'].append({
                        'name': match,
                        'line': i
                    })
        
        return analysis
    
    def _format_analysis(self, analysis: Dict[str, Any], file_path: str) -> str:
        """Format analysis results into readable text."""
        result = []
        result.append(f"📁 File: {file_path}")
        result.append(f"🔤 Language: {analysis['language']}")
        result.append(f"📏 Lines: {analysis['lines']}")
        
        if analysis['functions']:
            result.append(f"\n🔧 Functions ({len(analysis['functions'])}):")
            for func in analysis['functions'][:5]:  # Show first 5
                args_info = f" ({func['args']} args)" if 'args' in func else ""
                result.append(f"  • {func['name']} (line {func['line']}){args_info}")
            if len(analysis['functions']) > 5:
                result.append(f"  ... and {len(analysis['functions']) - 5} more")
        
        if analysis['classes']:
            result.append(f"\n🏗️  Classes ({len(analysis['classes'])}):")
            for cls in analysis['classes'][:5]:  # Show first 5
                result.append(f"  • {cls['name']} (line {cls['line']})")
            if len(analysis['classes']) > 5:
                result.append(f"  ... and {len(analysis['classes']) - 5} more")
        
        if analysis.get('imports'):
            result.append(f"\n📦 Imports ({len(analysis['imports'])}):")
            for imp in analysis['imports'][:5]:
                result.append(f"  • {imp}")
            if len(analysis['imports']) > 5:
                result.append(f"  ... and {len(analysis['imports']) - 5} more")
        
        if analysis['complexity'] != 'unknown':
            result.append(f"\n🔍 Complexity: {analysis['complexity']}")
        
        if analysis['issues']:
            result.append(f"\n⚠️  Issues:")
            for issue in analysis['issues']:
                result.append(f"  • {issue}")
        
        return '\n'.join(result)
    
    def generate_code(self, description: str, language: str = 'python') -> str:
        """Generate code based on description and language."""
        # Use OpenAI for code generation if available
        if self.use_openai and self.openai_client:
            try:
                return self.openai_client.generate_code(description, language)
            except Exception as e:
                print(f"Warning: {e}")
                print("Falling back to template-based generation.")
                # Fall through to template-based generation
        
        # Fall back to template-based generation
        language = language.lower()
        
        if language not in self.code_templates:
            return f"Sorry, I don't support code generation for {language} yet. Supported: {', '.join(self.code_templates.keys())}"
        
        templates = self.code_templates[language]
        
        # Simple heuristics to determine code type
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['class', 'object', 'struct']):
            template_type = 'class'
            name = self._extract_name(description, 'class')
        elif any(word in description_lower for word in ['function', 'method', 'def']):
            template_type = 'function'
            name = self._extract_name(description, 'function')
        else:
            template_type = 'script'
            name = 'main'
        
        template = templates[template_type]
        params = self._extract_parameters(description)
        
        return template.format(
            name=name,
            description=description,
            params=params
        )
    
    def _extract_name(self, description: str, code_type: str) -> str:
        """Extract a reasonable name from description."""
        words = re.findall(r'\b\w+\b', description.lower())
        
        # Filter out common words
        stop_words = {'a', 'an', 'the', 'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with'}
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        if meaningful_words:
            if code_type == 'class':
                return ''.join(word.capitalize() for word in meaningful_words[:2])
            else:
                return '_'.join(meaningful_words[:3])
        
        return f'my_{code_type}'
    
    def _extract_parameters(self, description: str) -> str:
        """Extract parameter suggestions from description."""
        # Simple parameter detection
        if 'parameter' in description.lower() or 'argument' in description.lower():
            return 'param1, param2'
        elif any(word in description.lower() for word in ['input', 'value', 'data']):
            return 'input_data'
        return ''
    
    def chat(self, user_input: str) -> str:
        """Handle chat interactions."""
        original_input = user_input.strip()
        user_input_lower = user_input.strip().lower()
        
        # Use OpenAI for intelligent chat if available
        if self.use_openai and self.openai_client:
            # Check for specific commands first
            if user_input_lower.startswith('analyze '):
                file_path = original_input[8:].strip()
                return self.analyze_file(file_path)
            elif user_input_lower.startswith('generate '):
                description = original_input[9:].strip()
                return self.generate_code(description)
            elif any(word in user_input_lower for word in ['help', 'commands']):
                return self._get_help()
            else:
                # Use OpenAI for general chat
                try:
                    return self.openai_client.chat_response(original_input)
                except Exception as e:
                    print(f"Warning: {e}")
                    print("Falling back to basic response.")
                    # Fall through to basic chat handling
        
        # Fall back to simple command recognition
        if user_input_lower.startswith('analyze '):
            file_path = original_input[8:].strip()
            return self.analyze_file(file_path)
        
        elif user_input_lower.startswith('generate '):
            description = original_input[9:].strip()
            return self.generate_code(description)
        
        elif any(word in user_input_lower for word in ['help', 'commands']):
            return self._get_help()
        
        elif any(word in user_input_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm your coding agent. I can analyze code files and generate code. Try 'help' for commands."
        
        else:
            # Default: treat as code generation request
            return f"I'll help you with that! Here's some code:\n\n{self.generate_code(original_input)}"
    
    def _get_help(self) -> str:
        """Return help text."""
        return """
Available commands:
• analyze <file_path> - Analyze a code file
• generate <description> - Generate code from description
• help - Show this help message

You can also just describe what you want, and I'll try to generate code for you!
        """.strip()