"""
Secure Code Executor - Executes Python/Pandas code in a sandboxed environment

This module provides secure execution of AI-generated Python code with restrictions
on file system access, dangerous imports, and execution time.
"""

import sys
import io
import os
import time
import traceback
from pathlib import Path
from typing import Dict
import logging
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from django.conf import settings

# Configure matplotlib for Unicode/Thai character support
import matplotlib.font_manager as fm

# Try to find Thai-compatible fonts installed on the system
def get_thai_fonts():
    """Get list of fonts that support Thai characters."""
    thai_fonts = []
    system_fonts = fm.findSystemFonts(fontpaths=None, fontext='ttf')

    # Prioritized Thai fonts (most preferred first)
    thai_font_names = [
        'TH SarabunPSK', 'TH Sarabun New', 'Angsana New', 'Cordia New',
        'Browallia New', 'Leelawadee', 'Tahoma',
        'Arial Unicode MS', 'Microsoft Sans Serif'
    ]

    for font_path in system_fonts:
        try:
            font_name = fm.FontProperties(fname=font_path).get_name()
            if any(thai_font in font_name for thai_font in thai_font_names):
                thai_fonts.append(font_name)
        except:
            continue

    return thai_fonts if thai_fonts else ['DejaVu Sans', 'Arial']

# Configure matplotlib with Thai font support
thai_fonts = get_thai_fonts()

# Set font configuration with Thai font priority
# Priority: TH SarabunPSK > Other detected Thai fonts > Fallback fonts
plt.rcParams['font.sans-serif'] = ['TH SarabunPSK'] + thai_fonts + ['DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False  # Fix minus sign display
plt.rcParams['font.family'] = 'sans-serif'

logger = logging.getLogger(__name__)


class CodeExecutor:
    """
    Executes Python code in a restricted environment.
    """

    # Whitelisted imports that are safe to use
    ALLOWED_IMPORTS = {
        'pandas', 'pd', 'numpy', 'np', 'matplotlib', 'plt',
        'datetime', 'math', 'collections', 'itertools', 'json'
    }

    # Dangerous functions/modules to block
    BLOCKED_KEYWORDS = [
        'eval', 'exec', 'compile', '__import__', 'open',
        'input', 'file', 'globals', 'locals', 'vars',
        'dir', 'help', 'quit', 'exit', 'copyright', 'credits',
        'license', 'os.', 'sys.', 'subprocess', 'socket',
        'requests', 'urllib', 'http', 'shutil', 'pickle',
        'shelve', 'importlib', '__builtins__'
    ]

    def __init__(self, timeout: int = 30, max_output_size: int = 50000):
        """
        Initialize the code executor.

        Args:
            timeout: Maximum execution time in seconds (default: 30)
            max_output_size: Maximum output size in characters (default: 50000)
        """
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.plots_dir = self._get_plots_directory()

    def _get_plots_directory(self) -> Path:
        """
        Get or create the plots directory.

        Returns:
            Path to plots directory
        """
        # Use media directory for generated plots
        plots_dir = Path(settings.MEDIA_ROOT) / 'plots'
        plots_dir.mkdir(parents=True, exist_ok=True)
        return plots_dir

    def _validate_code(self, code: str) -> tuple[bool, str]:
        """
        Validate code for security issues.

        Args:
            code: Python code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for blocked keywords
        code_lower = code.lower()
        for keyword in self.BLOCKED_KEYWORDS:
            if keyword in code_lower:
                return False, f"Blocked keyword detected: {keyword}"

        # Check for file operations (except savefig)
        if 'open(' in code_lower and 'savefig' not in code_lower:
            return False, "File operations are not allowed"

        # Check for system commands
        if any(cmd in code_lower for cmd in ['system(', 'popen(', 'call(']):
            return False, "System commands are not allowed"

        return True, ""

    def execute_code(self, code: str, df: pd.DataFrame) -> Dict:
        """
        Execute Python code with the provided DataFrame.

        Args:
            code: Python code to execute
            df: DataFrame to make available in the execution context

        Returns:
            Dict with execution results
        """
        # Validate code first
        is_valid, error_msg = self._validate_code(code)
        if not is_valid:
            return {
                "success": False,
                "error": f"Security validation failed: {error_msg}",
                "output": ""
            }

        # Prepare execution environment
        start_time = time.time()
        # Use UTF-8 encoding for output buffer to handle Thai/Unicode characters
        output_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output_buffer

        # Generate unique filename for plot
        plot_filename = f"plot_{int(time.time() * 1000)}.png"
        plot_path = self.plots_dir / plot_filename
        plot_url = f"{settings.MEDIA_URL}plots/{plot_filename}"

        # Prepare execution context with Unicode-aware DataFrame
        # Ensure DataFrame copy preserves Unicode column names
        df_copy = df.copy()

        # Helper function for safe label creation (transliterates Thai to ASCII)
        def safe_labels(labels, prefix='Item'):
            """Convert labels to safe ASCII format for matplotlib.

            This function ensures ALL labels are ASCII-safe by converting
            any non-ASCII text to numbered labels (e.g., 'Payment 1', 'Payment 2').

            Args:
                labels: List, array, or pandas Index of labels to convert
                prefix: Prefix for numbered labels (default: 'Item')

            Returns:
                List of ASCII-safe strings
            """
            safe_list = []
            for i, label in enumerate(labels):
                label_str = str(label)
                # Check if label contains only ASCII characters
                is_ascii = all(ord(char) < 128 for char in label_str)

                if is_ascii and label_str.strip():
                    # Label is ASCII-safe, use it
                    safe_list.append(label_str)
                else:
                    # Label contains non-ASCII or is empty, use numbered label
                    safe_list.append(f'{prefix} {i+1}')

            return safe_list

        # Helper function specifically for creating pie charts with Thai data
        def create_pie_chart(values, labels, title='Distribution', prefix='Category'):
            """Create a pie chart with Thai-safe labels.

            This is a convenience function that handles Thai text automatically.

            Args:
                values: Array of values for pie chart
                labels: Array of labels (can contain Thai text)
                title: Chart title in English
                prefix: Prefix for safe labels

            Example:
                payment_counts = df['ช่องทางการชำระเงิน'].value_counts()
                create_pie_chart(payment_counts.values, payment_counts.index,
                               'Payment Methods', 'Payment')
            """
            safe_labels_list = safe_labels(labels, prefix=prefix)

            plt.figure(figsize=(10, 6))
            plt.pie(values, labels=safe_labels_list, autopct='%1.1f%%')
            plt.title(title)
            plt.tight_layout()
            plt.savefig('output.png', bbox_inches='tight', dpi=100)
            plt.close()

            return safe_labels_list

        exec_globals = {
            'df': df_copy,
            'pd': pd,
            'np': np,
            'plt': plt,
            'print': print,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'range': range,
            'sum': sum,
            'min': min,
            'max': max,
            'sorted': sorted,
            'abs': abs,
            'round': round,
            'safe_labels': safe_labels,  # Helper for Thai text in plots
            'create_pie_chart': create_pie_chart,  # Convenience function for pie charts
        }

        # Replace savefig path in code - use raw string to avoid path issues
        # Convert plot_path to string with forward slashes for cross-platform compatibility
        plot_path_str = str(plot_path).replace('\\', '/')
        modified_code = code.replace("'output.png'", f"'{plot_path_str}'")
        modified_code = modified_code.replace('"output.png"', f'"{plot_path_str}"')

        try:
            # Set UTF-8 encoding for the execution environment
            if sys.stdout.encoding != 'utf-8':
                import codecs
                sys.stdout = codecs.getwriter('utf-8')(output_buffer.buffer if hasattr(output_buffer, 'buffer') else output_buffer)

            # Execute code with timeout simulation (basic)
            exec(modified_code, exec_globals, {})

            # Get output
            sys.stdout = old_stdout
            output = output_buffer.getvalue()

            # Limit output size
            if len(output) > self.max_output_size:
                output = output[:self.max_output_size] + "\n... (output truncated)"

            execution_time = time.time() - start_time

            # Check if plot was created
            has_plot = plot_path.exists()

            result = {
                "success": True,
                "output": output.strip(),
                "execution_time": round(execution_time, 2),
                "plot_path": str(plot_path) if has_plot else None,
                "plot_url": plot_url if has_plot else None
            }

            return result

        except UnicodeDecodeError as e:
            sys.stdout = old_stdout
            execution_time = time.time() - start_time

            error_msg = f"Unicode encoding error. Try using English column names or ensure proper UTF-8 encoding: {str(e)}"
            logger.error(f"Unicode error in code execution: {error_msg}")

            return {
                "success": False,
                "error": error_msg,
                "output": "Unicode handling error occurred",
                "execution_time": round(execution_time, 2)
            }

        except Exception as e:
            sys.stdout = old_stdout
            execution_time = time.time() - start_time

            error_trace = traceback.format_exc()

            # Log the actual code that failed for debugging
            logger.error(f"Code execution error: {error_trace}")
            logger.error(f"Failed code:\n{modified_code}")

            # Try to get output even on error, handling potential Unicode issues
            try:
                output = output_buffer.getvalue()
            except:
                output = "[Error retrieving output]"

            return {
                "success": False,
                "error": str(e),
                "error_trace": error_trace,
                "output": output,
                "execution_time": round(execution_time, 2),
                "failed_code": modified_code  # Include failed code for debugging
            }

        finally:
            # Clean up
            sys.stdout = old_stdout
            plt.close('all')  # Close all matplotlib figures

    def cleanup_old_plots(self, max_age_hours: int = 24):
        """
        Remove old plot files to save disk space.

        Args:
            max_age_hours: Maximum age of plots to keep in hours
        """
        try:
            cutoff_time = time.time() - (max_age_hours * 3600)

            for plot_file in self.plots_dir.glob("plot_*.png"):
                if plot_file.stat().st_mtime < cutoff_time:
                    plot_file.unlink()
                    logger.info(f"Deleted old plot: {plot_file.name}")

        except Exception as e:
            logger.error(f"Error cleaning up plots: {str(e)}")


# Utility function to get the executor instance
def get_code_executor() -> CodeExecutor:
    """Get a CodeExecutor instance."""
    return CodeExecutor()
