import json
import os
from wino_logic import WinoLogicPipeline

def run_tests():
    pipeline = WinoLogicPipeline(mock_llm=False)
    
    # 5 Distinct Evaluation Scenarios
    test_data = [
        # Scenario 1: Mixed Anomaly (Over-provisioned + Security Risk)
        {
            "resource_id": "i-1",
            "cpu_avg": 2,
            "cpu_p95": 5,
            "memory_avg": 70,
            "network_pct": 10,
            "internet_facing": True,
            "identity_attached": True
        },
        # Scenario 2: Overloaded Compute
        {
            "resource_id": "i-2",
            "cpu_avg": 85,
            "cpu_p95": 98,
            "memory_avg": 40,
            "network_pct": 60,
            "internet_facing": False,
            "identity_attached": False
        },
        # Scenario 3: Healthy Baseline (Should bypass LLM for speed and cost optimization)
        {
            "resource_id": "i-healthy-01",
            "cpu_avg": 45,
            "cpu_p95": 60,
            "memory_avg": 45,
            "network_pct": 30,
            "internet_facing": False,
            "identity_attached": False
        },
        # Scenario 4: Pure Security Risk (Normal utilization, but critical public exposure)
        {
            "resource_id": "i-public-db",
            "cpu_avg": 20,
            "cpu_p95": 35,
            "memory_avg": 50,
            "network_pct": 20,
            "internet_facing": True,
            "identity_attached": True
        },
        # Scenario 5: Missing / Ambiguous Data (Incomplete Telemetry)
        {
            "resource_id": "i-ghost-node",
            "cpu_avg": 2,
            "internet_facing": False
            # Notice memory, network, and p95 are completely missing
        }
    ]

    print("============================================================")
    print("Executing Wino-Logic Pipeline Final Run for Sample Outputs")
    print("============================================================")

    raw_json = json.dumps(test_data)
    
    # Process the multiple resources automatically
    reports = pipeline.process(raw_json)
    
    # Write to sample_outputs.json for easy submission
    output_path = os.path.join(os.path.dirname(__file__), "sample_outputs.json")
    
    parsed_reports = [json.loads(report) for report in reports]
    
    with open(output_path, "w") as f:
        json.dump(parsed_reports, f, indent=2)
        
    for report in reports:
        print(report)
        print("-" * 40)
        
    print(f"\n✅ All sample outputs have been successfully written to: {output_path}")

if __name__ == "__main__":
    run_tests()
