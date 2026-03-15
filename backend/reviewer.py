from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import json
import os

load_dotenv()

class CodeReviewer:
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0
        )
        print("✅ AI Model connected successfully!")
    
    def review_for_bugs(self, code: str, language: str):
        prompt = PromptTemplate(
            template="""
            You are an expert {language} developer doing a code review.
            
            Look at this code carefully and find:
            1. Any bugs or errors that would make it crash
            2. Logic errors
            3. Unhandled errors
            
            Here is the code to review:
            {code}
            
            Reply ONLY in this exact JSON format, nothing else:
            {{
                "bugs": [
                    {{
                        "line": <line number where bug is>,
                        "severity": "high or medium or low",
                        "description": "explain what the bug is",
                        "fix": "explain how to fix it"
                    }}
                ],
                "overall_score": <score from 1 to 10>,
                "summary": "one sentence summary"
            }}
            """,
            input_variables=["language", "code"]
        )
        
        chain = prompt | self.llm
        print(f"🔍 Checking for bugs in {language} code...")
        response = chain.invoke({
            "language": language,
            "code": code
        })
        
        try:
            return json.loads(response.content)
        except:
            return {"bugs": [], "overall_score": 5, "summary": "Could not parse response"}
    
    def review_for_security(self, code: str, language: str):
        prompt = PromptTemplate(
            template="""
            You are a cybersecurity expert reviewing {language} code.
            
            Look for these security problems:
            1. Hardcoded passwords or API keys
            2. SQL Injection
            3. Missing input validation
            4. Any other security risks
            
            Here is the code:
            {code}
            
            Reply ONLY in this exact JSON format:
            {{
                "vulnerabilities": [
                    {{
                        "type": "name of the security issue",
                        "line": <line number>,
                        "severity": "critical or high or medium or low",
                        "description": "explain the security risk",
                        "fix": "explain how to make it secure"
                    }}
                ],
                "security_score": <score from 1 to 10>
            }}
            """,
            input_variables=["language", "code"]
        )
        
        chain = prompt | self.llm
        print(f"🔒 Checking security in {language} code...")
        response = chain.invoke({"language": language, "code": code})
        
        try:
            return json.loads(response.content)
        except:
            return {"vulnerabilities": [], "security_score": 5}
    
    def full_review(self, code: str, language: str):
        print(f"\n📝 Starting full review of {language} code...")
        print("=" * 50)
        
        bugs = self.review_for_bugs(code, language)
        security = self.review_for_security(code, language)
        
        overall = (bugs["overall_score"] + security["security_score"]) / 2
        
        print(f"✅ Review complete! Score: {overall}/10")
        
        return {
            "bugs": bugs,
            "security": security,
            "overall_score": round(overall, 1)
        }


# TEST CODE - runs when you do: python reviewer.py
if __name__ == "__main__":
    
    test_code = """
def get_user(user_id):
    password = "admin123"
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query)
    return result[0]

def divide(a, b):
    return a / b
    """
    
    reviewer = CodeReviewer()
    result = reviewer.full_review(test_code, "Python")
    
    print("\n🐛 BUGS FOUND:")
    for bug in result["bugs"]["bugs"]:
        print(f"  Line {bug['line']}: {bug['description']}")
    
    print("\n🔒 SECURITY ISSUES:")
    for vuln in result["security"]["vulnerabilities"]:
        print(f"  Line {vuln['line']}: {vuln['description']}")
    
    print(f"\n⭐ OVERALL SCORE: {result['overall_score']}/10")
    