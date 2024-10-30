import numpy as np
from qiskit import transpile
from qiskit_aer import QasmSimulator
from typing import Tuple, List
from src.drapper import DraperAdder
from src.quantum_noise import add_quantum_noise
from src.gate_basis_transformer import GateBasisTransformer

class NoiseAnalyzer:
    """
    Analyzes the effects of noise on quantum addition circuits.
    """
    
    def __init__(self):
        """Initialize components for noise analysis."""
        self.adder = DraperAdder()
        self.transformer = GateBasisTransformer()
        
    def _get_success_rate(self, counts: dict, expected_sum: int, n_qubits: int) -> float:
        """
        Calculate the success rate of quantum addition from measurement counts.
        
        Args:
            counts (dict): Measurement results
            expected_sum (int): Expected sum value
            n_qubits (int): Number of qubits used
            
        Returns:
            float: Success rate (0 to 1)
        """
        # Convert expected sum to binary string
        expected_bitstring = format(expected_sum, f'0{n_qubits}b')
        
        # Count successful measurements
        successful_counts = counts.get(expected_bitstring, 0)
        total_counts = sum(counts.values())
        
        return successful_counts / total_counts if total_counts > 0 else 0
    
    def analyze_noise_effects(self, 
                            a: int, 
                            b: int, 
                            noise_levels: List[Tuple[float, float]], 
                            shots: int = 1000) -> dict:
        """
        Analyze how different noise levels affect quantum addition.
        
        Args:
            a (int): First number to add
            b (int): Second number to add
            noise_levels (List[Tuple[float, float]]): List of (p1, p2) noise probabilities
            shots (int): Number of circuit executions per noise level
            
        Returns:
            dict: Analysis results
        """
        
        # Get the original circuit
        circuit, n_qubits = self.adder.quantum_sum(a, b)
        
        # Transform to gate basis
        base_circuit = self.transformer.transform_circuit(circuit)
        gate_counts = self.transformer.get_gate_counts(base_circuit)
        
        results = {
            'input_values': {'a': a, 'b': b, 'expected_sum': a + b},
            'circuit_stats': {
                'n_qubits': n_qubits,
                'gate_counts': gate_counts,
                'total_gates': sum(gate_counts.values())
            },
            'noise_analysis': []
        }
        
        backend = QasmSimulator()
        
        # Test each noise level
        for p1, p2 in noise_levels:
            # Create noisy circuit
            noisy_circuit = add_quantum_noise(base_circuit, p1, p2)
            
            # Execute circuit

            job = transpile(noisy_circuit, backend)
            result = backend.run(job).result()
            counts = result.get_counts()
            
            # Calculate success rate
            success_rate = self._get_success_rate(counts, a + b, n_qubits)
            
            # Analysis for this noise level
            noise_result = {
                'noise_params': {'p1': p1, 'p2': p2},
                'success_rate': success_rate,
                'measurement_distribution': counts
            }
            
            results['noise_analysis'].append(noise_result)
            
        return results
    
    def analyze_circuit_depth_impact(self, 
                                   a: int, 
                                   b: int, 
                                   p1: float, 
                                   p2: float, 
                                   shots: int = 1000) -> dict:
        """
        Analyze how circuit depth affects noise sensitivity.
        
        Args:
            a (int): First number to add
            b (int): Second number to add
            p1 (float): Single-qubit gate error probability
            p2 (float): Two-qubit gate error probability
            shots (int): Number of circuit executions
            
        Returns:
            dict: Analysis results
        """
        circuit, n_qubits = self.adder.quantum_sum(a, b)
        base_circuit = self.transformer.transform_circuit(circuit)
        
        # Get circuit statistics
        depth = base_circuit.depth()
        gate_counts = self.transformer.get_gate_counts(base_circuit)
        
        # Create noisy circuit and analyze
        noisy_circuit = add_quantum_noise(base_circuit, p1, p2)
        
        # Execute circuit
        backend = QasmSimulator()
        job = transpile(noisy_circuit, backend)
        result = backend.run(job).result()
        counts = result.get_counts()
        
        success_rate = self._get_success_rate(counts, a + b, n_qubits)
        
        return {
            'circuit_depth': depth,
            'gate_counts': gate_counts,
            'total_gates': sum(gate_counts.values()),
            'noise_params': {'p1': p1, 'p2': p2},
            'success_rate': success_rate,
            'error_rate': 1 - success_rate
        }

def comprehensive_noise_analysis(a: int, 
                               b: int, 
                               shots: int = 1000) -> dict:
    """
    Performs comprehensive noise analysis on quantum addition.
    
    Args:
        a (int): First number to add
        b (int): Second number to add
        shots (int): Number of shots per analysis
        
    Returns:
        dict: Comprehensive analysis results
    """
    analyzer = NoiseAnalyzer()
    
    # Test different noise levels
    noise_levels = [
        (0.001, 0.002),  # Low noise
        (0.01, 0.02),    # Medium noise
        (0.05, 0.10),    # High noise
        (0.1, 0.2)       # Very high noise
    ]
    
    # Basic noise analysis
    noise_results = analyzer.analyze_noise_effects(a, b, noise_levels, shots)
    
    # Analyze circuit depth impact (using medium noise level)
    depth_impact = analyzer.analyze_circuit_depth_impact(a, b, 0.01, 0.02, shots)
    
    # Combine results
    comprehensive_results = {
        'noise_level_analysis': noise_results,
        'circuit_depth_impact': depth_impact,
        'mitigation_recommendations': {
            'circuit_optimization': (depth_impact['circuit_depth'] > 10),
            'suggested_max_noise': _suggest_max_noise(noise_results),
            'reliability_threshold': _calculate_reliability_threshold(noise_results)
        }
    }
    
    return comprehensive_results

def _suggest_max_noise(results: dict) -> dict:
    """Calculate suggested maximum noise levels for reliable operation."""
    success_threshold = 0.95  # 95% success rate threshold
    
    max_p1 = 0.0
    max_p2 = 0.0
    
    for analysis in results['noise_analysis']:
        if analysis['success_rate'] >= success_threshold:
            max_p1 = max(max_p1, analysis['noise_params']['p1'])
            max_p2 = max(max_p2, analysis['noise_params']['p2'])
    
    return {
        'max_single_qubit_error': max_p1,
        'max_two_qubit_error': max_p2
    }

def _calculate_reliability_threshold(results: dict) -> float:
    """Calculate the reliability threshold based on noise analysis."""
    success_rates = [analysis['success_rate'] for analysis in results['noise_analysis']]
    return np.mean(success_rates) - np.std(success_rates)

# Example usage
def demonstrate_noise_analysis():
    """Demonstrates the noise analysis capabilities."""
    # Test addition with comprehensive noise analysis
    a, b = 3, 5
    analysis_results = comprehensive_noise_analysis(a, b, shots=1000)
    
    print(f"Analyzing quantum addition of {a} + {b}")
    print("\nNoise Level Analysis:")
    for result in analysis_results['noise_level_analysis']['noise_analysis']:
        print(f"Noise levels (p1={result['noise_params']['p1']}, "
              f"p2={result['noise_params']['p2']}): "
              f"Success rate = {result['success_rate']:.2%}")
    
    print("\nCircuit Depth Impact:")
    depth_impact = analysis_results['circuit_depth_impact']
    print(f"Circuit depth: {depth_impact['circuit_depth']}")
    print(f"Total gates: {depth_impact['total_gates']}")
    print(f"Success rate: {depth_impact['success_rate']:.2%}")
    
    print("\nMitigation Recommendations:")
    recommendations = analysis_results['mitigation_recommendations']
    print(f"Circuit optimization needed: {recommendations['circuit_optimization']}")
    print(f"Maximum recommended noise levels: {recommendations['suggested_max_noise']}")
    print(f"Reliability threshold: {recommendations['reliability_threshold']:.2%}")
    
    return analysis_results