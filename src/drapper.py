import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import QasmSimulator
from typing import Tuple, List
from src.quantum_fourier_transform import QuantumFourierTransform


class DraperAdder:
    """
    Implementation of the Draper quantum adder algorithm.
    """
    
    def __init__(self):
        """Initialize the Draper adder with QFT implementation."""
        self.qft = QuantumFourierTransform()
    
    def _binary_to_phase_angles(self, number: int, n_qubits: int) -> List[float]:
        """
        Convert a binary number to phase angles for the quantum circuit.
        
        Args:
            number (int): Number to convert
            n_qubits (int): Number of qubits available
            
        Returns:
            List[float]: List of phase angles
        """
        angles = []
        for i in range(n_qubits):
            angle = 0
            for j in range(i + 1):
                if number & (1 << j):
                    angle += 2 * np.pi / (2 ** (i - j + 1))
            angles.append(angle)
        return angles
    
    def construct_adder(self, a: int, b: int, n_qubits: int) -> QuantumCircuit:
        """
        Constructs a quantum circuit to add two numbers using the Draper adder.
        
        Args:
            a (int): First number to add
            b (int): Second number to add
            n_qubits (int): Number of qubits to use (must be sufficient for sum)
            
        Returns:
            QuantumCircuit: Quantum circuit implementing the addition
        """
        if a >= 2**n_qubits or b >= 2**n_qubits:
            raise ValueError(f"Numbers too large for {n_qubits} qubits")
            
        # Create quantum circuit
        circuit = QuantumCircuit(n_qubits, n_qubits)
        
        # Initialize first register with a
        for i in range(n_qubits):
            if a & (1 << i):
                circuit.x(i)
        
        # Apply QFT
        qft_circuit = self.qft.construct_qft(n_qubits)
        circuit.compose(qft_circuit, inplace=True)
        
        # Add phase angles corresponding to b
        angles = self._binary_to_phase_angles(b, n_qubits)
        for i in range(n_qubits):
            circuit.p(angles[i], i)
        
        # Apply inverse QFT
        inverse_qft_circuit = self.qft.construct_inverse_qft(n_qubits)
        circuit.compose(inverse_qft_circuit, inplace=True)
        
        # Add measurement
        circuit.measure(range(n_qubits), range(n_qubits))
        
        return circuit
    
    def quantum_sum(self, a: int, b: int) -> Tuple[QuantumCircuit, int]:
        """
        Adds two numbers using the Draper quantum adder.
        
        Args:
            a (int): First number to add
            b (int): Second number to add
            
        Returns:
            Tuple[QuantumCircuit, int]: The quantum circuit and required number of qubits
        """
        # Calculate required number of qubits
        sum_value = a + b
        n_qubits = max(sum_value.bit_length(), a.bit_length(), b.bit_length())
        
        # Construct the adder circuit
        circuit = self.construct_adder(a, b, n_qubits)
        
        return circuit, n_qubits

def test_quantum_adder(a: int, b: int, shots: int = 1000):
    """
    Test function to demonstrate the quantum adder.
    
    Args:
        a (int): First number to add
        b (int): Second number to add
        shots (int): Number of times to run the circuit
        
    Returns:
        dict: Results of the quantum addition
    """
    
    # Create and run the circuit
    adder = DraperAdder()
    circuit, n_qubits = adder.quantum_sum(a, b)
    
    # Execute the circuit
    backend = QasmSimulator()
    job = transpile(circuit, backend)
    result = backend.run(job).result()
    counts = result.get_counts(circuit)
    
    # Process results
    return {
        'input_a': a,
        'input_b': b,
        'expected_sum': a + b,
        'measurement_counts': counts,
        'n_qubits_used': n_qubits
    }
