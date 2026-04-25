"""
Response (Output) Layer
=========================
Text-to-Speech and formatting for output delivery.
"""

import subprocess
from typing import Optional


class TextToSpeech:
    """Convert text to speech."""
    
    def __init__(self):
        self.available = False
        self.engine = None
    
    def speak(self, text: str) -> bool:
        """Speak text."""
        try:
            import pyttsx3
            if not self.engine:
                self.engine = pyttsx3.init()
            self.engine.say(text)
            self.engine.runAndWait()
            self.available = True
            return True
        except:
            pass
        
        # Fallback to system TTS
        try:
            if subprocess.os.name == "nt":
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Speak(text)
                self.available = True
                return True
        except:
            pass
        
        return False


class ResponseFormatter:
    """Format output for display."""
    
    def __init__(self):
        pass
    
    def format_text(self, text: str, format_type: str = "plain") -> str:
        """Format text output."""
        if format_type == "markdown":
            return self._format_markdown(text)
        elif format_type == "code":
            return self._format_code(text)
        elif format_type == "html":
            return self._format_html(text)
        return text
    
    def _format_markdown(self, text: str) -> str:
        """Format as markdown."""
        # Simple markdown formatting
        import re
        
        # Code blocks
        text = re.sub(r'```(\w+)?\n(.*?)```', r'```\1\n\2\n```', text, flags=re.DOTALL)
        
        # Bold
        text = re.sub(r'\*\*(.*?)\*\*', r'**\1**', text)
        
        # Italic
        text = re.sub(r'\*(.*?)\*', r'*\1*', text)
        
        return text
    
    def _format_code(self, text: str) -> str:
        """Format code blocks."""
        import re
        
        # Wrap in code block
        if "```" not in text:
            # Detect language from content
            lang = "python" if "def " in text or "import " in text else ""
            text = f"```{lang}\n{text}\n```"
        
        return text
    
    def _format_html(self, text: str) -> str:
        """Format as HTML."""
        import re
        
        # Simple conversions
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
        text = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code class="language-\1">\2</code></pre>', text, flags=re.DOTALL)
        
        return text


class OutputHandler:
    """Main output handler."""
    
    def __init__(self):
        self.tts = TextToSpeech()
        self.formatter = ResponseFormatter()
    
    def output(
        self,
        text: str,
        speak: bool = False,
        format_type: str = "plain"
    ) -> str:
        """Process and deliver output."""
        # Format
        formatted = self.formatter.format_text(text, format_type)
        
        # Speak if requested
        if speak:
            self.tts.speak(text)
        
        return formatted
    
    def markdown(self, text: str) -> str:
        """Format as markdown."""
        return self.formatter.format_text(text, "markdown")
    
    def code(self, text: str) -> str:
        """Format as code."""
        return self.formatter.format_text(text, "code")


def get_output_handler() -> OutputHandler:
    """Get output handler."""
    return OutputHandler()


if __name__ == "__main__":
    print("Response (Output) Layer")
    handler = get_output_handler()
    
    # Test formatting
    code_output = "def hello():\n    print('Hello')"
    formatted = handler.code(code_output)
    print(formatted)