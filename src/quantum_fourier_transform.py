import numpy as np
from qiskit import QuantumCircuit

class QuantumFourierTransform:
    """
    Implementation of Quantum Fourier Transform from scratch.
    """
    
    @staticmethod
    def _create_cphase_gate(circuit: QuantumCircuit, control: int, target: int, k: int):
        """
        Creates a controlled phase rotation gate.
        
        Args:
            circuit (QuantumCircuit): Circuit to add the gate to
            control (int): Control qubit index
            target (int): Target qubit index
            k (int): Phase rotation parameter
        """
        angle = 2 * np.pi / (2 ** k)
        circuit.cp(angle, control, target)
    
    def construct_qft(self, n_qubits: int) -> QuantumCircuit:
        """
        Constructs the Quantum Fourier Transform circuit.
        
        Args:
            n_qubits (int): Number of qubits in the circuit
            
        Returns:
            QuantumCircuit: QFT circuit
        """
        circuit = QuantumCircuit(n_qubits)
        
        # Implement QFT
        for i in range(n_qubits):
            # Hadamard gate on current qubit
            circuit.h(i)
            
            # Controlled phase rotations
            for j in range(i + 1, n_qubits):
                k = j - i + 1
                self._create_cphase_gate(circuit, j, i, k)
        
        # Swap qubits to match standard QFT output order
        for i in range(n_qubits // 2):
            circuit.swap(i, n_qubits - i - 1)
            
        return circuit
    
    def construct_inverse_qft(self, n_qubits: int) -> QuantumCircuit:
        """
        Constructs the inverse Quantum Fourier Transform circuit.
        
        Args:
            n_qubits (int): Number of qubits in the circuit
            
        Returns:
            QuantumCircuit: Inverse QFT circuit
        """
        qft = self.construct_qft(n_qubits)
        return qft.inverse()