# risk_scoring_agent.py
import numpy as np
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AgentStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"

@dataclass
class RiskAssessment:
    entity_id: str
    risk_score: float
    risk_level: RiskLevel
    factors: Dict[str, float]
    timestamp: datetime
    confidence: float

@dataclass
class AgentHealthMetrics:
    agent_id: str
    status: AgentStatus
    uptime: float
    response_time: float
    error_rate: float
    throughput: float
    cpu_usage: float
    memory_usage: float
    last_heartbeat: datetime
    active_assessments: int

class RiskScoringAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.is_running = False
        self.health_metrics = AgentHealthMetrics(
            agent_id=agent_id,
            status=AgentStatus.OFFLINE,
            uptime=0.0,
            response_time=0.0,
            error_rate=0.0,
            throughput=0.0,
            cpu_usage=0.0,
            memory_usage=0.0,
            last_heartbeat=datetime.now(),
            active_assessments=0
        )
        self.risk_weights = {
            'financial_exposure': 0.3,
            'credit_history': 0.25,
            'market_volatility': 0.2,
            'regulatory_compliance': 0.15,
            'operational_risk': 0.1
        }
        self.assessment_history = []
        self.start_time = None
        self._lock = threading.Lock()
        
    def start(self):
        """Start the risk scoring agent"""
        self.is_running = True
        self.start_time = datetime.now()
        self.health_metrics.status = AgentStatus.HEALTHY
        logger.info(f"Risk scoring agent {self.agent_id} started")
        
        # Start health monitoring thread
        self.health_thread = threading.Thread(target=self._monitor_health, daemon=True)
        self.health_thread.start()
    
    def stop(self):
        """Stop the risk scoring agent"""
        self.is_running = False
        self.health_metrics.status = AgentStatus.OFFLINE
        logger.info(f"Risk scoring agent {self.agent_id} stopped")
    
    def assess_risk(self, entity_data: Dict) -> RiskAssessment:
        """Assess risk for a given entity"""
        start_time = time.time()
        
        try:
            with self._lock:
                self.health_metrics.active_assessments += 1
            
            # Simulate risk factor calculations
            factors = self._calculate_risk_factors(entity_data)
            
            # Calculate weighted risk score
            risk_score = sum(factors[factor] * weight 
                           for factor, weight in self.risk_weights.items())
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Calculate confidence based on data completeness
            confidence = self._calculate_confidence(entity_data)
            
            assessment = RiskAssessment(
                entity_id=entity_data.get('entity_id', 'unknown'),
                risk_score=risk_score,
                risk_level=risk_level,
                factors=factors,
                timestamp=datetime.now(),
                confidence=confidence
            )
            
            self.assessment_history.append(assessment)
            
            # Update metrics
            response_time = time.time() - start_time
            self._update_performance_metrics(response_time, success=True)
            
            logger.info(f"Risk assessment completed for {assessment.entity_id}: {risk_score:.2f}")
            return assessment
            
        except Exception as e:
            self._update_performance_metrics(time.time() - start_time, success=False)
            logger.error(f"Risk assessment failed: {str(e)}")
            raise
        finally:
            with self._lock:
                self.health_metrics.active_assessments -= 1
    
    def _calculate_risk_factors(self, entity_data: Dict) -> Dict[str, float]:
        """Calculate individual risk factors"""
        # Simulate realistic risk factor calculations
        factors = {}
        
        # Financial exposure risk (0-1)
        exposure = entity_data.get('financial_exposure', 0)
        factors['financial_exposure'] = min(exposure / 1000000, 1.0)  # Normalize to millions
        
        # Credit history risk (0-1)
        credit_score = entity_data.get('credit_score', 750)
        factors['credit_history'] = max(0, (750 - credit_score) / 300)
        
        # Market volatility risk (0-1)
        volatility = entity_data.get('market_volatility', 0.2)
        factors['market_volatility'] = min(volatility, 1.0)
        
        # Regulatory compliance risk (0-1)
        compliance_score = entity_data.get('compliance_score', 0.9)
        factors['regulatory_compliance'] = 1.0 - compliance_score
        
        # Operational risk (0-1)
        operational_incidents = entity_data.get('operational_incidents', 0)
        factors['operational_risk'] = min(operational_incidents / 10, 1.0)
        
        return factors
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level based on score"""
        if risk_score < 0.25:
            return RiskLevel.LOW
        elif risk_score < 0.5:
            return RiskLevel.MEDIUM
        elif risk_score < 0.75:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _calculate_confidence(self, entity_data: Dict) -> float:
        """Calculate confidence based on data completeness"""
        required_fields = ['entity_id', 'financial_exposure', 'credit_score', 
                          'market_volatility', 'compliance_score']
        present_fields = sum(1 for field in required_fields if field in entity_data)
        return present_fields / len(required_fields)
    
    def _update_performance_metrics(self, response_time: float, success: bool):
        """Update performance metrics"""
        with self._lock:
            # Update response time (moving average)
            self.health_metrics.response_time = (
                self.health_metrics.response_time * 0.9 + response_time * 0.1
            )
            
            # Update error rate
            if not success:
                self.health_metrics.error_rate = (
                    self.health_metrics.error_rate * 0.9 + 0.1
                )
            else:
                self.health_metrics.error_rate = self.health_metrics.error_rate * 0.95
            
            # Update throughput (assessments per second)
            self.health_metrics.throughput = len(self.assessment_history) / max(1, 
                (datetime.now() - self.start_time).total_seconds())
    
    def _monitor_health(self):
        """Monitor agent health in background thread"""
        while self.is_running:
            try:
                with self._lock:
                    # Update uptime
                    if self.start_time:
                        self.health_metrics.uptime = (
                            datetime.now() - self.start_time
                        ).total_seconds()
                    
                    # Simulate system metrics
                    self.health_metrics.cpu_usage = random.uniform(10, 80)
                    self.health_metrics.memory_usage = random.uniform(30, 90)
                    self.health_metrics.last_heartbeat = datetime.now()
                    
                    # Determine health status
                    if self.health_metrics.error_rate > 0.1:
                        self.health_metrics.status = AgentStatus.CRITICAL
                    elif (self.health_metrics.response_time > 5.0 or 
                          self.health_metrics.cpu_usage > 90):
                        self.health_metrics.status = AgentStatus.WARNING
                    else:
                        self.health_metrics.status = AgentStatus.HEALTHY
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Health monitoring error: {str(e)}")
                time.sleep(1)
    
    def get_health_metrics(self) -> AgentHealthMetrics:
        """Get current health metrics"""
        with self._lock:
            return AgentHealthMetrics(**asdict(self.health_metrics))
    
    def get_assessment_history(self, limit: int = 100) -> List[RiskAssessment]:
        """Get recent assessment history"""
        return self.assessment_history[-limit:]

class RiskScoringSystem:
    def __init__(self):
        self.agents = {}
        self.system_metrics = {
            'total_assessments': 0,
            'average_response_time': 0.0,
            'system_uptime': 0.0,
            'active_agents': 0
        }
        self.start_time = datetime.now()
    
    def add_agent(self, agent_id: str) -> RiskScoringAgent:
        """Add a new risk scoring agent"""
        agent = RiskScoringAgent(agent_id)
        self.agents[agent_id] = agent
        return agent
    
    def start_all_agents(self):
        """Start all agents"""
        for agent in self.agents.values():
            agent.start()
        logger.info(f"Started {len(self.agents)} risk scoring agents")
    
    def stop_all_agents(self):
        """Stop all agents"""
        for agent in self.agents.values():
            agent.stop()
        logger.info("Stopped all risk scoring agents")
    
    def get_system_health(self) -> Dict:
        """Get overall system health"""
        active_agents = sum(1 for agent in self.agents.values() 
                          if agent.health_metrics.status != AgentStatus.OFFLINE)
        
        if active_agents > 0:
            avg_response_time = np.mean([agent.health_metrics.response_time 
                                       for agent in self.agents.values() 
                                       if agent.health_metrics.status != AgentStatus.OFFLINE])
            
            total_assessments = sum(len(agent.assessment_history) 
                                  for agent in self.agents.values())
        else:
            avg_response_time = 0.0
            total_assessments = 0
        
        return {
            'total_assessments': total_assessments,
            'average_response_time': avg_response_time,
            'system_uptime': (datetime.now() - self.start_time).total_seconds(),
            'active_agents': active_agents,
            'total_agents': len(self.agents)
        }
    
    def get_all_agent_health(self) -> List[AgentHealthMetrics]:
        """Get health metrics for all agents"""
        return [agent.get_health_metrics() for agent in self.agents.values()]

# Example usage and data generation
def generate_sample_data() -> Dict:
    """Generate sample entity data for testing"""
    return {
        'entity_id': f"ENT_{random.randint(1000, 9999)}",
        'financial_exposure': random.uniform(10000, 5000000),
        'credit_score': random.randint(300, 850),
        'market_volatility': random.uniform(0.1, 0.8),
        'compliance_score': random.uniform(0.6, 1.0),
        'operational_incidents': random.randint(0, 8)
    }

if __name__ == "__main__":
    # Create and start the risk scoring system
    system = RiskScoringSystem()
    
    # Add multiple agents
    for i in range(3):
        agent = system.add_agent(f"agent_{i+1}")
    
    # Start all agents
    system.start_all_agents()
    
    # Simulate some risk assessments
    try:
        for _ in range(10):
            agent_id = random.choice(list(system.agents.keys()))
            agent = system.agents[agent_id]
            sample_data = generate_sample_data()
            assessment = agent.assess_risk(sample_data)
            print(f"Assessment: {assessment.entity_id} - Risk: {assessment.risk_score:.2f}")
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nStopping system...")
    finally:
        system.stop_all_agents()