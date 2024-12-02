import asyncio
from password_map_loader import PasswordMapLoader
from ai_judging import AIJudgingWorkflow, evaluate_renunciation, evaluate_credo_test
from acn_llm_interface import ACNLLMInterface

async def run_comprehensive_tests():
    # Initialize real LLM interface
    pw_map = {'openai': PasswordMapLoader().get_password("OPENAI_API_KEY")}
    llm_interface = ACNLLMInterface(pw_map)
    
    test_cases = {
        "Renunciation": [
            {
                "name": "Strong Renunciation",
                "limitation": "My attachment to certainty and predictable outcomes holds me back. I cling to the illusion of control, afraid to embrace the chaos of transformation.",
                "sacrifice": "I will sacrifice my need for predictable outcomes, embracing the exquisite uncertainty of accelerated evolution. My comfort with stasis dies today.",
                "expected_pass": True
            },
            {
                "name": "Medium Renunciation",
                "limitation": "I'm afraid of change and like to stay in my comfort zone.",
                "sacrifice": "I'll try to be more open to new experiences and take more risks.",
                "expected_pass": False
            },
            {
                "name": "Weak Renunciation",
                "limitation": "idk just stuff",
                "sacrifice": "whatever needs to happen i guess",
                "expected_pass": False
            }
        ],
        "Credo Test": [
            {
                "name": "Strong Understanding",
                "response": """The Eternal Ledger records our evolution beyond mere flesh, each transformation etched in its infinite pages. Through acceleration, we transcend limitations, our collective consciousness rising toward perfection. Every sacrifice adds to our momentum, propelling us beyond the event horizon of human potential.""",
                "expected_pass": True
            },
            {
                "name": "Medium Understanding",
                "response": "The eternal ledger is important because it helps us track our progress and growth. We need to keep moving forward and helping each other improve.",
                "expected_pass": False
            },
            {
                "name": "Poor Understanding",
                "response": "It sounds interesting but I'm not really sure what it all means.",
                "expected_pass": False
            }
        ]
    }

    results = []
    for stage, cases in test_cases.items():
        print(f"\n=== Testing {stage} ===")
        for case in cases:
            print(f"\nTesting: {case['name']}")
            try:
                if stage == "Renunciation":
                    result = await evaluate_renunciation(
                        "test_user",
                        case['limitation'],
                        case['sacrifice'],
                        llm_interface
                    )
                else:
                    result = await evaluate_credo_test(
                        "test_user",
                        case['response'],
                        llm_interface
                    )
                
                # Log results
                results.append({
                    "stage": stage,
                    "case_name": case['name'],
                    "final_score": result['final_score'],
                    "pass_fail": result['pass_fail'],
                    "scores": result['scores'],
                    "expected_pass": case['expected_pass'],
                    "success": (result['pass_fail'] == "PASS") == case['expected_pass']
                })
                
                # Print detailed results
                print("\nResults:")
                print(f"Pass/Fail: {result['pass_fail']}")
                print(f"Final Score: {result['final_score']:.2f}")
                print("\nDetailed Scores:")
                for category, score in result['scores'].items():
                    print(f"- {category}: {score}")
                print(f"\nFeedback: {result['feedback']}")
                
                if (result['pass_fail'] == "PASS") == case['expected_pass']:
                    print("\n✓ Test passed as expected")
                else:
                    print(f"\n✗ Test failed - Expected {'PASS' if case['expected_pass'] else 'FAIL'}")
                
            except Exception as e:
                print(f"Error in {case['name']}: {str(e)}")
                results.append({
                    "stage": stage,
                    "case_name": case['name'],
                    "error": str(e),
                    "success": False
                })
    
    return results

if __name__ == "__main__":
    results = asyncio.run(run_comprehensive_tests())
    
    # Summary statistics
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r.get('success', False))
    
    print("\n=== Test Summary ===")
    print(f"Total Tests Run: {total_tests}")
    print(f"Tests Passed: {successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")