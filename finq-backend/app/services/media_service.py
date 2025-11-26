"""
Media Generation Service
Converts charts and data visualizations to images for sharing
"""
import logging
from typing import Optional, List
from io import BytesIO
import base64
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)


class MediaService:
    """Service for generating media from financial data"""
    
    def __init__(self, output_dir: str = "../media_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def generate_chart_image(
        self,
        data: pd.DataFrame,
        chart_type: str = "line",
        title: str = "Financial Chart",
        x_col: str = "Date",
        y_col: str = "Value",
        ticker: str = None
    ) -> Optional[str]:
        """
        Generate a chart image from DataFrame
        
        Args:
            data: DataFrame with data to chart
            chart_type: 'line', 'bar', or 'area'
            title: Chart title
            x_col: Column name for x-axis
            y_col: Column name for y-axis
            ticker: Ticker symbol (for filename)
        
        Returns:
            Base64 encoded image string or file path
        """
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            if chart_type == "line":
                ax.plot(data[x_col], data[y_col], linewidth=2, marker='o', markersize=4)
            elif chart_type == "bar":
                ax.bar(data[x_col], data[y_col])
            elif chart_type == "area":
                ax.fill_between(data[x_col], data[y_col], alpha=0.5)
            
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel(x_col, fontsize=12)
            ax.set_ylabel(y_col, fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Save to bytes
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            
            # Convert to base64
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Error generating chart image: {e}")
            plt.close('all')
            return None
    
    def generate_price_chart(
        self,
        price_data: pd.DataFrame,
        ticker: str,
        period: str = "1y"
    ) -> Optional[str]:
        """
        Generate stock price chart with volume
        
        Args:
            price_data: DataFrame with OHLCV data
            ticker: Stock ticker
            period: Time period
        
        Returns:
            Base64 encoded image string
        """
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                          gridspec_kw={'height_ratios': [3, 1]})
            
            # Price chart
            if 'Close' in price_data.columns:
                ax1.plot(price_data.index, price_data['Close'], 
                        linewidth=2, color='#667eea', label='Close Price')
                ax1.fill_between(price_data.index, price_data['Close'], 
                               alpha=0.3, color='#667eea')
            
            ax1.set_title(f'{ticker} Stock Price - {period}', 
                         fontsize=16, fontweight='bold', pad=20)
            ax1.set_ylabel('Price ($)', fontsize=12)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Volume chart
            if 'Volume' in price_data.columns:
                ax2.bar(price_data.index, price_data['Volume'], 
                       color='#764ba2', alpha=0.6)
            
            ax2.set_xlabel('Date', fontsize=12)
            ax2.set_ylabel('Volume', fontsize=12)
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save to bytes
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Error generating price chart: {e}")
            plt.close('all')
            return None
    
    def generate_summary_image(
        self,
        ticker: str,
        company_name: str,
        metrics: dict,
        insight_text: str = None
    ) -> Optional[str]:
        """
        Generate a summary card image with key metrics
        
        Args:
            ticker: Stock ticker
            company_name: Company name
            metrics: Dictionary of key metrics
            insight_text: Optional insight text
        
        Returns:
            Base64 encoded image string
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.axis('off')
            
            # Create text content
            text_content = f"""
{ticker} - {company_name}

Key Metrics:
"""
            for key, value in metrics.items():
                text_content += f"  • {key}: {value}\n"
            
            if insight_text:
                text_content += f"\nInsight:\n{insight_text[:200]}..."
            
            ax.text(0.1, 0.5, text_content, 
                   fontsize=12, verticalalignment='center',
                   family='monospace', wrap=True)
            
            ax.set_title(f'Financial Summary - {ticker}', 
                        fontsize=16, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Error generating summary image: {e}")
            plt.close('all')
            return None
    
    def save_image_to_file(
        self,
        image_base64: str,
        filename: str
    ) -> Optional[str]:
        """
        Save base64 image to file
        
        Args:
            image_base64: Base64 encoded image
            filename: Output filename
        
        Returns:
            File path if successful
        """
        try:
            # Remove data URL prefix if present
            if image_base64.startswith('data:image'):
                image_base64 = image_base64.split(',')[1]
            
            image_data = base64.b64decode(image_base64)
            file_path = self.output_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving image to file: {e}")
            return None

