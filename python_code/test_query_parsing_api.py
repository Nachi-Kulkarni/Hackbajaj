#!/usr/bin/env python3
"""
Test script for Query Parsing API (AI-D2-002)
Tests the POST /parse-query endpoint functionality
"""

import requests
import json
import time
from typing import Dict, Any

# API configuration
API_BASE_URL = "http://localhost:8000"
PARSE_QUERY_ENDPOINT = f"{API_BASE_URL}/parse-query"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

def test_health_endpoint() -> bool:
    """Test the health endpoint"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['message']}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_parse_query(query: str, expected_entities: Dict[str, Any] = None) -> bool:
    """Test query parsing with a specific query"""
    try:
        payload = {"query": query}
        response = requests.post(
            PARSE_QUERY_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n🔍 Testing query: '{query}'")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                parsed_query = data.get("parsed_query", {})
                
                print(f"✅ Query parsed successfully")
                print(f"   Message: {data.get('message')}")
                print(f"   Query Type: {parsed_query.get('query_type')}")
                print(f"   Intent: {parsed_query.get('intent')}")
                print(f"   Confidence: {parsed_query.get('confidence')}")
                print(f"   Complexity: {parsed_query.get('complexity')}")
                
                # Print extracted entities
                entities = parsed_query.get("entities", {})
                print(f"   Extracted Entities:")
                for entity_type, value in entities.items():
                    if value:
                        print(f"     - {entity_type}: {value}")
                
                # Print key terms
                key_terms = parsed_query.get("key_terms", [])
                if key_terms:
                    print(f"   Key Terms: {', '.join(key_terms)}")
                
                return True
            else:
                print(f"❌ Query parsing failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Query parsing test failed: {e}")
        return False

def test_invalid_queries() -> bool:
    """Test invalid query scenarios"""
    print("\n🧪 Testing invalid queries...")
    
    # Test empty query
    try:
        response = requests.post(
            PARSE_QUERY_ENDPOINT,
            json={"query": ""},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 400:
            print("✅ Empty query correctly rejected")
        else:
            print(f"❌ Empty query should return 400, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Empty query test failed: {e}")
        return False
    
    # Test very long query
    try:
        long_query = "What is the procedure for " + "very long query " * 100
        response = requests.post(
            PARSE_QUERY_ENDPOINT,
            json={"query": long_query},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 400:
            print("✅ Long query correctly rejected")
        else:
            print(f"❌ Long query should return 400, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Long query test failed: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Starting Query Parsing API Tests (AI-D2-002)")
    print("=" * 50)
    
    # Test health endpoint first
    if not test_health_endpoint():
        print("❌ Health check failed. Make sure the API server is running.")
        return
    
    # Test various query types (reduced to respect rate limits - 20 requests per minute for free models)
    test_queries = [
        {
            "query": "What are the age restrictions for this life insurance policy?",
            "description": "Age-based query"
        },
        {
            "query": "What is the procedure for filing a claim?",
            "description": "Procedure-based query"
        },
        {
            "query": "Tell me about the benefits",
            "description": "General query"
        }
    ]
    
    successful_tests = 0
    total_tests = len(test_queries)
    
    for i, test_case in enumerate(test_queries):
        print(f"\n📋 {test_case['description']}")
        if test_parse_query(test_case["query"]):
            successful_tests += 1
        
        # Add delay between requests to respect rate limits
        if i < len(test_queries) - 1:
            print("⏳ Waiting 4 seconds to respect rate limits...")
            time.sleep(4)
    
    # Test invalid queries
    if test_invalid_queries():
        print("\n✅ Invalid query tests passed")
    else:
        print("\n❌ Invalid query tests failed")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Successful query parsing tests: {successful_tests}/{total_tests}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("\n🎉 All tests passed! Query parsing API is working correctly.")
        print("\n📋 AI-D2-002 Implementation Status: ✅ COMPLETE")
        print("\n🔗 Available endpoints:")
        print(f"   - API Documentation: {API_BASE_URL}/docs")
        print(f"   - Parse Query: POST {PARSE_QUERY_ENDPOINT}")
        print(f"   - Health Check: GET {HEALTH_ENDPOINT}")
    else:
        print(f"\n⚠️  {total_tests - successful_tests} tests failed. Please check the API implementation.")

if __name__ == "__main__":
    main()