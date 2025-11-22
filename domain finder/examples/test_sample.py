#!/usr/bin/env python3
"""
Domain Finder - Test Sample Script
Tests with first 5 schools to verify setup.

Version: 1.0
Date: 2025-11-15
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from src.domain_finder import DomainFinder

def test_sample():
    """Test with 5 schools"""
    
    print("\n" + "="*70)
    print("🧪 DOMAIN FINDER - TEST SAMPLE (5 Schools)")
    print("="*70 + "\n")
    
    # Load first 5 schools
    input_file = 'data/input/schools_womens_volleyball_all_divisions.csv'
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        print("   Make sure you're running from project root directory")
        return
    
    df = pd.read_csv(input_file).head(5)
    
    print(f"📂 Testing with {len(df)} schools:\n")
    for idx, row in df.iterrows():
        print(f"   {idx+1}. {row['school_name']}")
    
    print("\n" + "-"*70 + "\n")
    
    # Initialize finder
    finder = DomainFinder()
    
    results = []
    
    for idx, row in df.iterrows():
        school_name = row['school_name']
        print(f"[{idx+1}/5] 🔍 Searching: {school_name}")
        
        domain, status = finder.find_athletics_domain(school_name)
        
        if status == "FOUND":
            print(f"        ✅ Found: {domain}")
        elif status == "NOT_FOUND":
            print(f"        ❌ Not found")
        else:
            print(f"        ⚠️  No results")
        
        results.append({
            'school_name': school_name,
            'domain': domain if domain else 'N/A',
            'status': status
        })
        
        print()
    
    # Summary
    print("-"*70)
    print("\n📊 TEST RESULTS:\n")
    
    found = len([r for r in results if r['status'] == 'FOUND'])
    not_found = len([r for r in results if r['status'] == 'NOT_FOUND'])
    
    for r in results:
        status_icon = "✅" if r['status'] == "FOUND" else "❌"
        print(f"   {status_icon} {r['school_name']:<40} → {r['domain']}")
    
    print(f"\n   Found: {found}/5 ({found/5*100:.0f}%)")
    print(f"   Not Found: {not_found}/5\n")
    
    if found >= 4:
        print("✅ TEST PASSED - System working correctly!")
        print("   Ready to process all 1,261 schools.\n")
    elif found >= 2:
        print("⚠️  TEST PARTIAL - Some issues detected")
        print("   Check your API credentials and internet connection.\n")
    else:
        print("❌ TEST FAILED - Setup issue detected")
        print("   Run: python scripts/validate_env.py\n")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    test_sample()