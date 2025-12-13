"""
Setup verification script for slide generation system
"""

import os
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.9+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_env_file():
    """Check if .env file exists"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print("   → Create .env from .env.example:")
        print("   → cp .env.example .env")
        return False
    print("✓ .env file exists")
    return True


def check_env_variables():
    """Check if required environment variables are set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required = ["LLM_API_KEY", "IMAGE_API_KEY", "IMAGE_API_URL"]
    missing = []
    
    for var in required:
        value = os.getenv(var, "")
        if not value or "xxxx" in value.lower() or "your-" in value.lower():
            missing.append(var)
    
    if missing:
        print(f"❌ Missing or invalid environment variables: {', '.join(missing)}")
        print("   → Edit .env file and add your API credentials")
        return False
    
    print("✓ Environment variables configured")
    return True


def check_dependencies():
    """Check if key dependencies are installed"""
    required_modules = [
        ("langgraph", "LangGraph"),
        ("langchain", "LangChain"),
        ("jinja2", "Jinja2"),
        ("PIL", "Pillow"),
        ("playwright", "Playwright"),
        ("weasyprint", "WeasyPrint"),
        ("dotenv", "python-dotenv")
    ]
    
    missing = []
    for module, name in required_modules:
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"❌ {name} not installed")
            missing.append(name)
    
    if missing:
        print("\n→ Install missing dependencies:")
        print("  pip install -r requirements.txt")
        return False
    
    return True


def check_output_directories():
    """Check if output directories exist"""
    dirs = ["output", "output/html", "output/images", "output/slide_images"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✓ Output directories created")
    return True


def main():
    """Run all checks"""
    print("="*60)
    print("SLIDE GENERATION SYSTEM - SETUP VERIFICATION")
    print("="*60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Environment Variables", check_env_variables),
        ("Output Directories", check_output_directories)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        results.append(check_func())
    
    print("\n" + "="*60)
    if all(results):
        print("✓ ALL CHECKS PASSED - Ready to run!")
        print("="*60)
        print("\nRun the system:")
        print("  python main.py")
        return 0
    else:
        print("❌ SETUP INCOMPLETE - Fix issues above")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

