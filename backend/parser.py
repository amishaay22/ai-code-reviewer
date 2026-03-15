import ast

class CodeParser:
    
    def chunk_code(self, code: str, chunk_size: int = 50):
        """
        Splits large code files into smaller pieces
        """
        lines = code.split('\n')
        chunks = []
        
        for i in range(0, len(lines), chunk_size):
            chunk = '\n'.join(lines[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def detect_language(self, filename: str):
        """
        Detects programming language from filename
        Example: 'main.py' → 'Python'
        """
        extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.go': 'Go'
        }
        
        ext = '.' + filename.split('.')[-1]
        return extensions.get(ext, 'Unknown')