"""
Test runner for all ontology module tests.

Run with: python tests/run_all_tests.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_information_module import run_all_tests as test_information
from tests.test_capabilities_module import run_all_tests as test_capabilities
from tests.test_qualities_module import run_all_tests as test_qualities


def run_all():
    """Run all module tests."""
    print("\n" + "=" * 70)
    print("WATERFRAME ONTOLOGY MODULE TEST SUITE")
    print("=" * 70)
    
    all_results = {}
    
    # Test information module
    print("\n" + "-" * 70)
    all_results["information"] = test_information()
    
    # Test capabilities module
    print("\n" + "-" * 70)
    all_results["capabilities"] = test_capabilities()
    
    # Test qualities module
    print("\n" + "-" * 70)
    all_results["qualities"] = test_qualities()
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in all_results.values() if v)
    total = len(all_results)
    
    for module, result in all_results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {module}: {status}")
    
    print(f"\n{'=' * 70}")
    if passed == total:
        print("✓ ALL TESTS PASSED!")
    else:
        print(f"✗ {total - passed}/{total} modules have failing tests")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
