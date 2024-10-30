from qiskit import QuantumCircuit
import random

def add_quantum_noise(circuit: QuantumCircuit, 
                     p1: float, 
                     p2: float) -> QuantumCircuit:
    """
    Adds Pauli noise to a quantum circuit after gates.
    
    Args:
        circuit (QuantumCircuit): Input quantum circuit
        p1 (float): Probability of error after single-qubit gates (0 to 1)
        p2 (float): Probability of error after two-qubit gates (0 to 1)
    
    Returns:
        QuantumCircuit: New circuit with added noise gates
    """
    if not (0 <= p1 <= 1) or not (0 <= p2 <= 1):
        raise ValueError("Probabilities must be between 0 and 1")
    
    # Create a new circuit with the same number of qubits and classical bits
    noisy_circuit = QuantumCircuit(circuit.num_qubits, circuit.num_clbits)
    
    # Pauli operators to choose from
    pauli_ops = ['x', 'y', 'z']
    
    # Process each instruction in the circuit
    for instruction in circuit.data:
        gate = instruction[0]
        qubits = instruction[1]
        
        # Add the original gate
        noisy_circuit.append(gate, qubits)
        
        # Determine if it's a single or two-qubit gate
        num_qubits = len(qubits)
        error_prob = p1 if num_qubits == 1 else p2
        
        # Apply random Pauli errors to each affected qubit
        for qubit in qubits:
            if random.random() < error_prob:
                # Randomly select a Pauli operator
                pauli_error = random.choice(pauli_ops)
                
                # Apply the chosen Pauli operator
                if pauli_error == 'x':
                    noisy_circuit.x(qubit)
                elif pauli_error == 'y':
                    noisy_circuit.y(qubit)
                else:  # z
                    noisy_circuit.z(qubit)

            noisy_circuit.measure_all()
    
    return noisy_circuit

def analyze_noise_effect(circuit: QuantumCircuit, 
                        p1: float, 
                        p2: float, 
                        num_samples: int = 100) -> dict:
    """
    Analyzes the effect of noise by counting the number and types of errors added.
    
    Args:
        circuit (QuantumCircuit): Input quantum circuit
        p1 (float): Single-qubit gate error probability
        p2 (float): Two-qubit gate error probability
        num_samples (int): Number of noisy circuits to generate for analysis
        
    Returns:
        dict: Statistics about the noise effects
    """
    total_errors = {'x': 0, 'y': 0, 'z': 0}
    total_single_qubit_errors = 0
    total_two_qubit_errors = 0
    
    for _ in range(num_samples):
        noisy_circuit = add_quantum_noise(circuit, p1, p2)
        
        # Count errors in this sample
        for instruction in noisy_circuit.data:
            gate = instruction[0].name
            if gate in ['x', 'y', 'z']:
                total_errors[gate] += 1
                if len(instruction[1]) == 1:
                    total_single_qubit_errors += 1
                else:
                    total_two_qubit_errors += 1
    
    # Calculate averages
    stats = {
        'avg_x_errors': total_errors['x'] / num_samples,
        'avg_y_errors': total_errors['y'] / num_samples,
        'avg_z_errors': total_errors['z'] / num_samples,
        'avg_single_qubit_errors': total_single_qubit_errors / num_samples,
        'avg_two_qubit_errors': total_two_qubit_errors / num_samples
    }
    
    return stats
