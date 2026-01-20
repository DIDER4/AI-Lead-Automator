"""
Project Verification Script
Run this to verify all modules are correctly installed and working
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def verify_imports():
    """Verify all imports work correctly"""
    print("🔍 Verifying module imports...\n")
    
    tests = []
    
    # Test config
    try:
        from src.config import Constants, AppConfig, get_logger
        tests.append(("✅", "Config module", f"v{Constants.APP_VERSION}"))
    except Exception as e:
        tests.append(("❌", "Config module", str(e)))
    
    # Test security
    try:
        from src.security import SecureConfigManager, InputValidator
        tests.append(("✅", "Security module", "Encryption & Validation"))
    except Exception as e:
        tests.append(("❌", "Security module", str(e)))
    
    # Test API clients
    try:
        from src.api import FirecrawlClient, OpenAIClient, AnthropicClient
        tests.append(("✅", "API clients", "Firecrawl, OpenAI, Anthropic"))
    except Exception as e:
        tests.append(("❌", "API clients", str(e)))
    
    # Test models
    try:
        from src.models import Lead
        tests.append(("✅", "Models", "Lead data model"))
    except Exception as e:
        tests.append(("❌", "Models", str(e)))
    
    # Test services
    try:
        from src.services import DataManager, LeadAnalyzer
        tests.append(("✅", "Services", "DataManager, LeadAnalyzer"))
    except Exception as e:
        tests.append(("❌", "Services", str(e)))
    
    # Test UI
    try:
        from src.ui import UIPages
        tests.append(("✅", "UI module", "Pages and components"))
    except Exception as e:
        tests.append(("❌", "UI module", str(e)))
    
    # Test utils
    try:
        from src.utils import make_gdpr_safe
        tests.append(("✅", "Utils", "GDPR compliance"))
    except Exception as e:
        tests.append(("❌", "Utils", str(e)))
    
    # Print results
    for status, name, info in tests:
        print(f"{status} {name:20s} : {info}")
    
    # Summary
    passed = sum(1 for t in tests if t[0] == "✅")
    total = len(tests)
    
    print(f"\n{'='*60}")
    print(f"Result: {passed}/{total} modules imported successfully")
    
    if passed == total:
        print("✅ All systems operational!")
        return True
    else:
        print("❌ Some modules failed to import")
        return False


def verify_dependencies():
    """Check if all required packages are installed"""
    print("\n🔍 Verifying dependencies...\n")
    
    required = [
        'streamlit',
        'pandas',
        'plotly',
        'cryptography',
        'requests',
        'openpyxl'
    ]
    
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package:15s} : Installed")
        except ImportError:
            print(f"❌ {package:15s} : Missing")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies installed!")
        return True


def verify_structure():
    """Verify project structure"""
    print("\n🔍 Verifying project structure...\n")
    
    required_dirs = [
        'src',
        'src/api',
        'src/security',
        'src/models',
        'src/services',
        'src/ui',
        'src/ui/pages',
        'src/ui/components',
        'src/utils',
        'tests',
        'data',
        'logs'
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path:30s} : Exists")
        else:
            print(f"❌ {dir_path:30s} : Missing")
            all_good = False
    
    if all_good:
        print("\n✅ All directories in place!")
    else:
        print("\n❌ Some directories are missing")
    
    return all_good


def main():
    """Run all verification tests"""
    print("="*60)
    print("  AI Lead Automator v2.0 - Verification Script")
    print("="*60)
    
    deps_ok = verify_dependencies()
    struct_ok = verify_structure()
    imports_ok = verify_imports()
    
    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    
    if deps_ok and struct_ok and imports_ok:
        print("✅ All checks passed!")
        print("🚀 Ready to run: streamlit run app.py")
        return 0
    else:
        print("❌ Some checks failed")
        print("📝 Review the output above for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
