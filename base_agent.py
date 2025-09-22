"""
Base OpenAI Agent structure for Job Hunter application.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai package not installed. Install it to use full functionality.")

try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    print("Warning: pydantic package not installed. Install it to use full functionality.")

from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if PYDANTIC_AVAILABLE:
    class AgentResponse(BaseModel):
        """Standardized response model for all agents."""
        success: bool = Field(description="Whether the agent operation was successful")
        data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
        message: str = Field(description="Human-readable message about the operation")
        errors: Optional[List[str]] = Field(default=None, description="List of errors if any")
else:
    class AgentResponse:
        """Fallback response model when Pydantic is not available."""
        def __init__(self, success: bool, message: str, data: Optional[Dict[str, Any]] = None, errors: Optional[List[str]] = None):
            self.success = success
            self.message = message
            self.data = data
            self.errors = errors

class BaseAgent(ABC):
    """
    Base class for all OpenAI-powered agents in the Job Hunter application.
    Provides common functionality for OpenAI integration, logging, and error handling.
    """
    
    def __init__(self, name: str, system_prompt: str):
        """
        Initialize the base agent.
        
        Args:
            name: Name of the agent
            system_prompt: System prompt that defines the agent's role and behavior
        """
        self.name = name
        self.system_prompt = system_prompt
        
        if OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        else:
            self.client = None
            
        self.model = Config.OPENAI_MODEL
        self.temperature = Config.AGENT_TEMPERATURE
        self.max_tokens = Config.AGENT_MAX_TOKENS
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        # Only validate configuration if OpenAI is available
        if OPENAI_AVAILABLE:
            try:
                Config.validate_config()
            except ValueError as e:
                self.logger.warning(f"Configuration warning: {e}")
                
        self.logger.info(f"Initialized {name} agent")
    
    def _make_openai_request(
        self, 
        messages: List[Dict[str, str]], 
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Union[str, Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the OpenAI API with standardized error handling.
        
        Args:
            messages: List of messages for the conversation
            functions: Optional list of function definitions
            function_call: Optional function call specification
            
        Returns:
            Dictionary containing the API response
            
        Raises:
            Exception: If the API request fails
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            if functions:
                kwargs["functions"] = functions
            if function_call:
                kwargs["function_call"] = function_call
                
            response = self.client.chat.completions.create(**kwargs)
            return response.model_dump()
            
        except Exception as e:
            self.logger.error(f"OpenAI API request failed: {str(e)}")
            raise
    
    def _prepare_messages(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """
        Prepare messages for OpenAI API call.
        
        Args:
            user_input: The user's input or request
            context: Optional context information
            
        Returns:
            List of formatted messages
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if context:
            context_str = f"Context: {context}\n\n"
            messages.append({"role": "user", "content": context_str + user_input})
        else:
            messages.append({"role": "user", "content": user_input})
            
        return messages
    
    def _handle_response(self, response: Dict[str, Any]) -> AgentResponse:
        """
        Handle and standardize the OpenAI API response.
        
        Args:
            response: Raw API response
            
        Returns:
            Standardized AgentResponse
        """
        try:
            choice = response["choices"][0]
            message = choice["message"]
            
            # Check if it's a function call
            if message.get("function_call"):
                return self._handle_function_call(message["function_call"])
            else:
                content = message.get("content", "")
                return AgentResponse(
                    success=True,
                    data={"content": content},
                    message="Request processed successfully"
                )
                
        except Exception as e:
            self.logger.error(f"Error handling response: {str(e)}")
            return AgentResponse(
                success=False,
                message="Error processing response",
                errors=[str(e)]
            )
    
    def _handle_function_call(self, function_call: Dict[str, Any]) -> AgentResponse:
        """
        Handle function calls from OpenAI API.
        
        Args:
            function_call: Function call information from API
            
        Returns:
            AgentResponse with function call results
        """
        function_name = function_call.get("name")
        function_args = function_call.get("arguments", "{}")
        
        try:
            import json
            args = json.loads(function_args)
            result = self.execute_function(function_name, args)
            
            return AgentResponse(
                success=True,
                data={"function_result": result, "function_name": function_name},
                message=f"Function {function_name} executed successfully"
            )
            
        except Exception as e:
            self.logger.error(f"Function call execution failed: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Function {function_name} execution failed",
                errors=[str(e)]
            )
    
    @abstractmethod
    def execute_function(self, function_name: str, args: Dict[str, Any]) -> Any:
        """
        Execute a function called by the OpenAI API.
        Must be implemented by subclasses.
        
        Args:
            function_name: Name of the function to execute
            args: Arguments for the function
            
        Returns:
            Result of the function execution
        """
        pass
    
    @abstractmethod
    def process_request(self, request: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Process a request using the agent's capabilities.
        Must be implemented by subclasses.
        
        Args:
            request: The request to process
            context: Optional context information
            
        Returns:
            AgentResponse with the results
        """
        pass
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": self.name,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }