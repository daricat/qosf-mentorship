from qiskit import QuantumCircuit
from qiskit.synthesis import OneQubitEulerDecomposer
from qiskit.converters import circuit_to_dag


class GateBasisTransformer:
    def __init__(self):
        self.basis_gates = {'cx', 'id', 'rz', 'sx', 'x'}
        self.euler_decomposer = OneQubitEulerDecomposer(basis='ZSX')
        
    def _decompose_single_qubit_gate(self, gate, qubit):
        matrix = gate.to_matrix() if hasattr(gate, 'to_matrix') else gate
        temp_circuit = QuantumCircuit(1)
        theta, phi, lambda_ = self.euler_decomposer.angles(matrix)
        
        temp_circuit.rz(phi, 0)
        temp_circuit.sx(0)
        temp_circuit.rz(theta, 0)
        temp_circuit.sx(0)
        temp_circuit.rz(lambda_, 0)
        
        return [(gate, [qubit]) for gate, _, _ in temp_circuit.data]
        
    def transform_circuit(self, circuit: QuantumCircuit) -> QuantumCircuit:
        new_circuit = QuantumCircuit(circuit.num_qubits, circuit.num_clbits)
        dag = circuit_to_dag(circuit)
        
        for node in dag.op_nodes():
            qubits = node.qargs
            gate = node.op
            
            # Skip non-unitary operations such as measurements
            if gate.name == 'measure':
                continue
            
            if gate.name.lower() in self.basis_gates:
                new_circuit.append(gate, qubits)
            elif len(qubits) == 1:
                decomposed_gates = self._decompose_single_qubit_gate(gate, qubits[0])
                for decomp_gate, decomp_qubits in decomposed_gates:
                    new_circuit.append(decomp_gate, decomp_qubits)
            elif gate.name == 'cx':
                new_circuit.append(gate, qubits)
            else:
                temp_circuit = QuantumCircuit(len(qubits))
                temp_circuit.append(gate, list(range(len(qubits))))
                decomposed = temp_circuit.decompose()
                for inst in decomposed.data:
                    inst_gate, inst_qubits, _ = inst
                    if len(inst_qubits) == 1:
                        original_qubit = qubits[temp_circuit.qubits.index(inst_qubits[0])]
                        decomp_gates = self._decompose_single_qubit_gate(inst_gate, original_qubit)
                        for decomp_gate, decomp_qubits in decomp_gates:
                            new_circuit.append(decomp_gate, decomp_qubits)
                    else:
                        mapped_qubits = [qubits[temp_circuit.qubits.index(q)] for q in inst_qubits]
                        new_circuit.append(inst_gate, mapped_qubits)
        
        return new_circuit

    def get_gate_counts(self, circuit: QuantumCircuit) -> dict:
        counts = {gate: 0 for gate in self.basis_gates}
        for instruction in circuit.data:
            gate_name = instruction[0].name.lower()
            if gate_name in counts:
                counts[gate_name] += 1
        return counts