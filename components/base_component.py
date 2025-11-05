"""
Base component abstract class for Streamlit components.
"""
from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class BaseComponent(ABC):
    """Abstract base class for all Streamlit dashboard components."""
    
    def __init__(self, data: Optional[pd.DataFrame] = None, **kwargs):
        """
        Initialize the component.
        
        Args:
            data: Optional DataFrame containing the data for this component
            **kwargs: Additional keyword arguments
        """
        self.data = data
        self.kwargs = kwargs
    
    @abstractmethod
    def render(self) -> None:
        """
        Render the component in Streamlit.
        This method should contain all Streamlit UI code for this component.
        """
        pass
    
    def set_data(self, data: pd.DataFrame) -> None:
        """
        Update the data for this component.
        
        Args:
            data: DataFrame containing the data
        """
        self.data = data
    
    def validate_data(self) -> bool:
        """
        Validate that the component has the required data.
        
        Returns:
            True if data is valid, False otherwise
        """
        return self.data is not None and not self.data.empty

