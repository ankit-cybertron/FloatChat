#!/usr/bin/env python3
"""
Test script for the enhanced NLP + RAG + LLM chatbot functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_enhanced_chat():
    """Test the enhanced chat functionality"""
    try:
        # Import the enhanced chat function
        from dash_frontend.research_dashboard import enhanced_chat_with_nlp_rag_llm, generate_fallback_ocean_data

        print("🧪 Testing Enhanced Chat Functionality")
        print("=" * 50)

        # Test 1: ARGO float query
        print("\n1. Testing ARGO float query...")
        result1 = enhanced_chat_with_nlp_rag_llm("Show me data for ARGO_5001", "light")
        print(f"Response length: {len(result1.get('response', ''))}")
        print(f"Has table: {result1.get('table_data') is not None}")
        print(f"Has statistics: {result1.get('statistics') is not None}")
        print(f"Plots needed: {result1.get('plots_needed', False)}")

        # Test 2: General ocean question (will use fallback since no API key)
        print("\n2. Testing general ocean question...")
        result2 = enhanced_chat_with_nlp_rag_llm("What is ocean acidification?", "light")
        print(f"Response: {result2.get('response', '')[:100]}...")
        print(f"Has table: {result2.get('table_data') is not None}")

        # Test 3: Statistics query
        print("\n3. Testing statistics query...")
        result3 = enhanced_chat_with_nlp_rag_llm("Show me temperature statistics", "light")
        print(f"Response length: {len(result3.get('response', ''))}")
        print(f"Has statistics: {result3.get('statistics') is not None}")

        # Test 4: Fallback data generation
        print("\n4. Testing fallback data generation...")
        table_data = generate_fallback_ocean_data("temperature statistics")
        print(f"Fallback table generated: {len(table_data.get('data', []))} rows")

        print("\n✅ All tests completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_chat()
    sys.exit(0 if success else 1)
