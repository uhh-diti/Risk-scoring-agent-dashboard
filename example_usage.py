# example_usage.py
"""
Example script demonstrating how to use the Risk Scoring Agent system
"""

import time
import json
from risk_scoring_agent import RiskScoringSystem, generate_sample_data

def main():
    print("🎯 Risk Scoring Agent System Example")
    print("=" * 50)
    
    # Create the risk scoring system
    system = RiskScoringSystem()
    
    # Add multiple agents
    print("\n📊 Setting up agents...")
    agent_ids = ['risk_agent_1', 'risk_agent_2', 'risk_agent_3']
    
    for agent_id in agent_ids:
        agent = system.add_agent(agent_id)
        print(f"✅ Added agent: {agent_id}")
    
    # Start all agents
    print("\n🚀 Starting all agents...")
    system.start_all_agents()
    
    # Wait for agents to initialize
    time.sleep(2)
    
    # Generate and process some sample risk assessments
    print("\n📈 Processing risk assessments...")
    
    sample_entities = [
        {
            'entity_id': 'CORP_001',
            'financial_exposure': 2500000,
            'credit_score': 720,
            'market_volatility': 0.15,
            'compliance_score': 0.95,
            'operational_incidents': 1
        },
        {
            'entity_id': 'CORP_002', 
            'financial_exposure': 750000,
            'credit_score': 680,
            'market_volatility': 0.25,
            'compliance_score': 0.88,
            'operational_incidents': 3
        },
        {
            'entity_id': 'CORP_003',
            'financial_exposure': 5000000,
            'credit_score': 590,
            'market_volatility': 0.45,
            'compliance_score': 0.72,
            'operational_incidents': 7
        }
    ]
    
    # Process assessments using different agents
    assessments = []
    for i, entity_data in enumerate(sample_entities):
        agent_id = agent_ids[i % len(agent_ids)]
        agent = system.agents[agent_id]
        
        print(f"\n🔍 Processing {entity_data['entity_id']} with {agent_id}...")
        
        try:
            assessment = agent.assess_risk(entity_data)
            assessments.append(assessment)
            
            print(f"  Risk Score: {assessment.risk_score:.3f}")
            print(f"  Risk Level: {assessment.risk_level.value.upper()}")
            print(f"  Confidence: {assessment.confidence:.2f}")
            print(f"  Factors:")
            for factor, value in assessment.factors.items():
                print(f"    {factor}: {value:.3f}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Generate additional random assessments
    print(f"\n🎲 Generating 10 random assessments...")
    for i in range(10):
        agent_id = agent_ids[i % len(agent_ids)]
        agent = system.agents[agent_id]
        
        sample_data = generate_sample_data()
        try:
            assessment = agent.assess_risk(sample_data)
            print(f"  {assessment.entity_id}: {assessment.risk_score:.3f} ({assessment.risk_level.value})")
        except Exception as e:
            print(f"  ❌ Error processing {sample_data['entity_id']}: {e}")
        
        time.sleep(0.5)  # Small delay between assessments
    
    # Display system health
    print(f"\n🏥 System Health Summary")
    print("=" * 30)
    
    system_health = system.get_system_health()
    print(f"Total Assessments: {system_health['total_assessments']}")
    print(f"Active Agents: {system_health['active_agents']}/{system_health['total_agents']}")
    print(f"Average Response Time: {system_health['average_response_time']:.3f}s")
    print(f"System Uptime: {system_health['system_uptime']:.1f}s")
    
    # Display individual agent health
    print(f"\n🔍 Agent Health Details")
    print("=" * 30)
    
    agent_health = system.get_all_agent_health()
    for agent in agent_health:
        print(f"\n{agent.agent_id}:")
        print(f"  Status: {agent.status.value.upper()}")
        print(f"  Uptime: {agent.uptime:.1f}s")
        print(f"  Response Time: {agent.response_time:.3f}s")
        print(f"  Error Rate: {agent.error_rate*100:.1f}%")
        print(f"  Throughput: {agent.throughput:.2f} req/s")
        print(f"  CPU Usage: {agent.cpu_usage:.1f}%")
        print(f"  Memory Usage: {agent.memory_usage:.1f}%")
        print(f"  Active Assessments: {agent.active_assessments}")
    
    # Show recent assessment history
    print(f"\n📚 Recent Assessment History")
    print("=" * 30)
    
    for agent_id in agent_ids:
        agent = system.agents[agent_id]
        recent_assessments = agent.get_assessment_history(limit=5)
        
        if recent_assessments:
            print(f"\n{agent_id} (last 5 assessments):")
            for assessment in recent_assessments[-5:]:
                print(f"  {assessment.entity_id}: {assessment.risk_score:.3f} "
                      f"({assessment.risk_level.value}) - {assessment.timestamp.strftime('%H:%M:%S')}")
    
    # Export assessment data
    print(f"\n💾 Exporting assessment data...")
    
    all_assessments = []
    for agent_id in agent_ids:
        agent = system.agents[agent_id]
        agent_assessments = agent.get_assessment_history()
        
        for assessment in agent_assessments:
            all_assessments.append({
                'agent_id': agent_id,
                'entity_id': assessment.entity_id,
                'risk_score': assessment.risk_score,
                'risk_level': assessment.risk_level.value,
                'confidence': assessment.confidence,
                'timestamp': assessment.timestamp.isoformat(),
                'factors': assessment.factors
            })
    
    # Save to JSON file
    with open('risk_assessments.json', 'w') as f:
        json.dump(all_assessments, f, indent=2)
    
    print(f"✅ Exported {len(all_assessments)} assessments to 'risk_assessments.json'")
    
    # Performance test
    print(f"\n⚡ Performance Test")
    print("=" * 20)
    
    print("Running 50 rapid assessments...")
    start_time = time.time()
    
    for i in range(50):
        agent_id = agent_ids[i % len(agent_ids)]
        agent = system.agents[agent_id]
        sample_data = generate_sample_data()
        
        try:
            assessment = agent.assess_risk(sample_data)
        except Exception as e:
            print(f"Error in assessment {i}: {e}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Completed 50 assessments in {duration:.2f} seconds")
    print(f"📊 Average rate: {50/duration:.2f} assessments/second")
    
    # Final system health check
    print(f"\n🔍 Final System Health Check")
    print("=" * 30)
    
    final_health = system.get_system_health()
    print(f"Total Assessments: {final_health['total_assessments']}")
    print(f"Final Average Response Time: {final_health['average_response_time']:.3f}s")
    
    final_agent_health = system.get_all_agent_health()
    healthy_agents = sum(1 for agent in final_agent_health 
                        if agent.status.value == 'healthy')
    print(f"Healthy Agents: {healthy_agents}/{len(final_agent_health)}")
    
    # Stop all agents
    print(f"\n🛑 Stopping all agents...")
    system.stop_all_agents()
    
    print(f"\n✅ Example completed successfully!")
    print(f"💡 To view real-time monitoring, run: streamlit run streamlit_dashboard.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        #streamlit run "c:\Users\aditi\risk scoring dashboard\streamlit_dashboard.py"
