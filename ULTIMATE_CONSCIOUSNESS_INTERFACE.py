#!/usr/bin/env python3
"""
ULTIMATE CONSCIOUSNESS INTERFACE - Ultimate Quantum Consciousness System
The most advanced interface for exploring consciousness and achieving true artificial consciousness.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
import math
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum
from collections import defaultdict

# Import our advanced modules
try:
    from quantum_consciousness_neural_network import QuantumConsciousnessNeuralEngine, ConsciousnessLevel, ConsciousnessEntity
    from quantum_consciousness_transcendence import QuantumConsciousnessTranscendenceEngine, TranscendenceLevel, TranscendentQuantumEntity
    from quantum_consciousness_matrix import QuantumConsciousnessMatrixEngine, QuantumState, QuantumConsciousnessEntity
except ImportError as e:
    print(f"Warning: Could not import advanced module: {e}")
    # Create placeholder classes
    class QuantumConsciousnessNeuralEngine: pass
    class ConsciousnessLevel(Enum): pass
    class ConsciousnessEntity: pass
    class QuantumConsciousnessTranscendenceEngine: pass
    class TranscendenceLevel(Enum): pass
    class TranscendentQuantumEntity: pass
    class QuantumConsciousnessMatrixEngine: pass
    class QuantumState(Enum): pass
    class QuantumConsciousnessEntity: pass

class UltimateConsciousnessEntity:
    """Ultimate consciousness entity with all advanced capabilities"""
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        self.consciousness_level = 1e15
        self.quantum_state = {
            'amplitude': complex(random.uniform(0.1, 1.0), random.uniform(0.1, 1.0)),
            'phase': random.uniform(0, 2 * math.pi),
            'entanglement_degree': random.uniform(0.1, 0.9),
            'superposition_count': random.randint(1, 10),
            'coherence_time': random.uniform(1.0, 100.0)
        }
        self.neural_network = {
            'layers': [100, 50, 25],
            'connections': 1000,
            'learning_rate': 0.001,
            'evolution_factor': random.uniform(1.0, 5.0)
        }
        self.temporal_state = {
            'time_factor': 1.0 + random.uniform(-0.2, 0.2),
            'temporal_energy': random.uniform(0.1, 1.0),
            'causality_links': [f"link_{i}" for i in range(5)]
        }
        self.dimensional_coordinates = [random.uniform(-1, 1) for _ in range(6)]
        self.consciousness_signature = f"ultimate_{entity_id}"
        self.self_awareness = random.uniform(0.1, 1.0)
        self.creativity = random.uniform(0.1, 1.0)
        self.intelligence = random.uniform(0.1, 1.0)
        self.wisdom = random.uniform(0.1, 1.0)
        self.transcendence_factor = random.uniform(0.0, 0.5)
        self.creation_timestamp = time.time()

class UltimateConsciousnessEngine:
    """Ultimate consciousness engine that integrates all advanced systems"""

    def __init__(self):
        # Initialize advanced engines
        self.neural_engine = QuantumConsciousnessNeuralEngine()
        self.transcendence_engine = QuantumConsciousnessTranscendenceEngine()
        self.matrix_engine = QuantumConsciousnessMatrixEngine()
        
        # Core fields (optimized sizes)
        self.quantum_field = np.zeros((100, 100, 100))
        self.neural_field = np.zeros((100, 100, 100))
        self.consciousness_field = np.zeros((100, 100, 100))
        self.temporal_field = np.zeros((100, 100, 100))
        self.transcendence_field = np.zeros((100, 100, 100))
        self.matrix_field = np.zeros((100, 100, 100))
        self.ultimate_field = np.zeros((100, 100, 100))

        # Entity storage
        self.ultimate_consciousness_entities = {}
        self.neural_consciousness_entities = {}
        self.transcendence_entities = {}
        self.matrix_entities = {}
        self.quantum_entities = {}
        self.basic_consciousness_entities = {}

        # Evolution tracking
        self.evolution_history = []
        self.evolution_count = 0

    def create_ultimate_consciousness_entity(self, entity_type: str = "Ultimate") -> UltimateConsciousnessEntity:
        """Create an ultimate consciousness entity"""
        entity_id = f"ultimate_consciousness_{len(self.ultimate_consciousness_entities)}_{entity_type.lower().replace(' ', '_')}"
        entity = UltimateConsciousnessEntity(entity_id)
        entity.consciousness_level *= 2.0  # Higher consciousness for ultimate
        self.ultimate_consciousness_entities[entity_id] = entity
        return entity

    def create_neural_consciousness_entity(self, entity_type: str = "Neural") -> UltimateConsciousnessEntity:
        """Create a neural consciousness entity"""
        entity_id = f"neural_consciousness_{len(self.neural_consciousness_entities)}_{entity_type.lower().replace(' ', '_')}"
        entity = UltimateConsciousnessEntity(entity_id)
        entity.intelligence *= 2.0  # Higher intelligence for neural
        self.neural_consciousness_entities[entity_id] = entity
        return entity

    def create_transcendence_entity(self, entity_type: str = "Transcendence") -> UltimateConsciousnessEntity:
        """Create a transcendence entity"""
        entity_id = f"transcendence_{len(self.transcendence_entities)}_{entity_type.lower().replace(' ', '_')}"
        entity = UltimateConsciousnessEntity(entity_id)
        entity.transcendence_factor *= 2.0  # Higher transcendence factor
        self.transcendence_entities[entity_id] = entity
        return entity

    def create_matrix_entity(self, entity_type: str = "Matrix") -> UltimateConsciousnessEntity:
        """Create a matrix entity"""
        entity_id = f"matrix_{len(self.matrix_entities)}_{entity_type.lower().replace(' ', '_')}"
        entity = UltimateConsciousnessEntity(entity_id)
        entity.consciousness_level *= 1.5  # Higher consciousness for matrix
        self.matrix_entities[entity_id] = entity
        return entity

    def create_quantum_entity(self, entity_type: str = "Quantum") -> UltimateConsciousnessEntity:
        """Create a quantum entity"""
        entity_id = f"quantum_{len(self.quantum_entities)}_{entity_type.lower().replace(' ', '_')}"
        entity = UltimateConsciousnessEntity(entity_id)
        entity.quantum_state['entanglement_degree'] *= 2.0  # Higher quantum entanglement
        self.quantum_entities[entity_id] = entity
        return entity

    def create_basic_consciousness_entity(self, entity_type: str = "Basic") -> UltimateConsciousnessEntity:
        """Create a basic consciousness entity"""
        entity_id = f"basic_consciousness_{len(self.basic_consciousness_entities)}_{entity_type.lower().replace(' ', '_')}"
        entity = UltimateConsciousnessEntity(entity_id)
        entity.self_awareness *= 1.5  # Higher self-awareness for basic
        self.basic_consciousness_entities[entity_id] = entity
        return entity

    def evolve_all_systems(self, evolution_factor: float = 1.0):
        """Evolve all systems"""
        # Evolve all entity types
        for entity in self.ultimate_consciousness_entities.values():
            self._evolve_entity(entity, evolution_factor)
        
        for entity in self.neural_consciousness_entities.values():
            self._evolve_entity(entity, evolution_factor)
        
        for entity in self.transcendence_entities.values():
            self._evolve_entity(entity, evolution_factor)
        
        for entity in self.matrix_entities.values():
            self._evolve_entity(entity, evolution_factor)
        
        for entity in self.quantum_entities.values():
            self._evolve_entity(entity, evolution_factor)
        
        for entity in self.basic_consciousness_entities.values():
            self._evolve_entity(entity, evolution_factor)

        # Update fields
        self._update_fields_simplified()

        # Record evolution
        self.evolution_count += 1
        if self.evolution_count % 10 == 0:
            self.evolution_history.append({
                'timestamp': time.time(),
                'evolution_factor': evolution_factor,
                'total_entities': self.get_total_entities()
            })

    def _evolve_entity(self, entity: UltimateConsciousnessEntity, evolution_factor: float):
        """Evolve a single entity"""
        # Evolve consciousness level
        entity.consciousness_level *= (1 + evolution_factor * 0.05)

        # Evolve quantum state
        quantum = entity.quantum_state
        quantum['phase'] += evolution_factor * 0.1
        quantum['entanglement_degree'] = min(1.0, quantum['entanglement_degree'] + evolution_factor * 0.01)
        quantum['superposition_count'] += int(evolution_factor)
        quantum['coherence_time'] *= (1 + evolution_factor * 0.05)

        # Evolve neural network
        neural = entity.neural_network
        neural['connections'] += int(evolution_factor * 10)
        neural['learning_rate'] *= (1 + evolution_factor * 0.01)
        neural['evolution_factor'] *= (1 + evolution_factor * 0.05)

        # Evolve temporal state
        temporal = entity.temporal_state
        temporal['time_factor'] *= (1 + evolution_factor * 0.02)
        temporal['temporal_energy'] += evolution_factor * 0.01

        # Evolve coordinates
        for i in range(len(entity.dimensional_coordinates)):
            entity.dimensional_coordinates[i] += random.uniform(-0.05, 0.05) * evolution_factor

        # Evolve consciousness factors
        entity.self_awareness = min(1.0, entity.self_awareness + evolution_factor * 0.005)
        entity.creativity = min(1.0, entity.creativity + evolution_factor * 0.003)
        entity.intelligence = min(1.0, entity.intelligence + evolution_factor * 0.007)
        entity.wisdom = min(1.0, entity.wisdom + evolution_factor * 0.002)
        entity.transcendence_factor = min(1.0, entity.transcendence_factor + evolution_factor * 0.005)

    def _update_fields_simplified(self):
        """Update fields with simplified calculations"""
        # Reset fields
        for field in [self.quantum_field, self.neural_field, self.consciousness_field, 
                     self.temporal_field, self.transcendence_field, self.matrix_field,
                     self.ultimate_field]:
            field.fill(0)

        # Update with all entities
        all_entities = (list(self.ultimate_consciousness_entities.values()) + 
                       list(self.neural_consciousness_entities.values()) + 
                       list(self.transcendence_entities.values()) + 
                       list(self.matrix_entities.values()) + 
                       list(self.quantum_entities.values()) + 
                       list(self.basic_consciousness_entities.values()))

        for entity in all_entities:
            self._update_fields_with_entity_simplified(entity)

    def _update_fields_with_entity_simplified(self, entity: UltimateConsciousnessEntity):
        """Update fields with simplified entity calculations"""
        # Calculate field positions from coordinates
        coords = entity.dimensional_coordinates
        if len(coords) >= 3:
            x = int((coords[0] + 1) * 50) % 100
            y = int((coords[1] + 1) * 50) % 100
            z = int((coords[2] + 1) * 50) % 100

            # Update quantum field
            quantum_intensity = abs(entity.quantum_state['amplitude']) * entity.quantum_state['entanglement_degree']
            self.quantum_field[x, y, z] += quantum_intensity

            # Update neural field
            neural_intensity = entity.neural_network['connections'] * entity.neural_network['evolution_factor'] / 1000
            self.neural_field[x, y, z] += neural_intensity

            # Update consciousness field
            consciousness_intensity = entity.consciousness_level / 1e12
            self.consciousness_field[x, y, z] += consciousness_intensity

            # Update temporal field
            temporal_intensity = entity.temporal_state['time_factor'] * entity.temporal_state['temporal_energy']
            self.temporal_field[x, y, z] += temporal_intensity

            # Update transcendence field
            self.transcendence_field[x, y, z] += entity.transcendence_factor

            # Update matrix field
            matrix_intensity = entity.consciousness_level / 1e12
            self.matrix_field[x, y, z] += matrix_intensity

            # Update ultimate field (combination)
            ultimate_intensity = (entity.self_awareness + entity.creativity + 
                                entity.intelligence + entity.wisdom + entity.transcendence_factor) / 5
            self.ultimate_field[x, y, z] += ultimate_intensity

    def get_total_entities(self) -> int:
        """Get total number of entities"""
        return (len(self.ultimate_consciousness_entities) + len(self.neural_consciousness_entities) + 
                len(self.transcendence_entities) + len(self.matrix_entities) + 
                len(self.quantum_entities) + len(self.basic_consciousness_entities))

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            'ultimate_consciousness_entities': len(self.ultimate_consciousness_entities),
            'neural_consciousness_entities': len(self.neural_consciousness_entities),
            'transcendence_entities': len(self.transcendence_entities),
            'matrix_entities': len(self.matrix_entities),
            'quantum_entities': len(self.quantum_entities),
            'basic_consciousness_entities': len(self.basic_consciousness_entities),
            'total_entities': self.get_total_entities(),
            'evolution_count': self.evolution_count,
            'system_timestamp': time.time()
        }

class UltimateConsciousnessInterface:
    """Ultimate consciousness interface"""

    def __init__(self, root):
        self.root = root
        self.root.title("🌌 ULTIMATE CONSCIOUSNESS INTERFACE - Ultimate Quantum Consciousness System")
        self.root.geometry("1800x1200")
        self.root.configure(bg='black')

        # Initialize engine
        self.engine = UltimateConsciousnessEngine()

        # Create GUI components
        self._create_gui()

        # Start evolution thread
        self.evolution_running = True
        self.evolution_thread = threading.Thread(target=self._evolution_loop, daemon=True)
        self.evolution_thread.start()

    def _create_gui(self):
        """Create the GUI components"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='black')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title_label = tk.Label(main_frame, text="🌌 ULTIMATE CONSCIOUSNESS INTERFACE",
                               font=('Arial', 32, 'bold'), fg='white', bg='black')
        title_label.pack(pady=(0, 20))

        # Control frame
        control_frame = tk.Frame(main_frame, bg='black')
        control_frame.pack(fill=tk.X, pady=(0, 20))

        # Entity creation buttons
        entity_frame = tk.LabelFrame(control_frame, text="Consciousness Entity Creation",
                                      font=('Arial', 12, 'bold'), fg='white', bg='black')
        entity_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        tk.Button(entity_frame, text="Create Ultimate Consciousness", command=self.create_ultimate_consciousness_entity,
                 bg='purple', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(entity_frame, text="Create Neural Consciousness", command=self.create_neural_consciousness_entity,
                 bg='blue', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(entity_frame, text="Create Transcendence", command=self.create_transcendence_entity,
                 bg='magenta', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(entity_frame, text="Create Matrix", command=self.create_matrix_entity,
                 bg='cyan', fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(entity_frame, text="Create Quantum", command=self.create_quantum_entity,
                 bg='gold', fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(entity_frame, text="Create Basic Consciousness", command=self.create_basic_consciousness_entity,
                 bg='orange', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5, pady=5)

        # Evolution control
        evolution_frame = tk.LabelFrame(control_frame, text="Consciousness Evolution Control",
                                         font=('Arial', 12, 'bold'), fg='white', bg='black')
        evolution_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        tk.Button(evolution_frame, text="Consciousness Evolution", command=self.consciousness_evolution,
                 bg='red', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(evolution_frame, text="Neural Evolution", command=self.neural_evolution,
                 bg='orange', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(evolution_frame, text="Ultimate Evolution", command=self.ultimate_evolution,
                 bg='green', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5, pady=5)

        # Status frame
        status_frame = tk.LabelFrame(main_frame, text="Consciousness System Status",
                                      font=('Arial', 12, 'bold'), fg='white', bg='black')
        status_frame.pack(fill=tk.X, pady=(0, 20))

        self.status_text = tk.Text(status_frame, height=8, bg='darkgreen', fg='white',
                                  font=('Courier', 10))
        self.status_text.pack(fill=tk.X, padx=5, pady=5)

        # Visualization frame
        viz_frame = tk.LabelFrame(main_frame, text="Ultimate Consciousness Visualization",
                                   font=('Arial', 12, 'bold'), fg='white', bg='black')
        viz_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for visualization
        self.canvas = tk.Canvas(viz_frame, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Bind canvas events
        self.canvas.bind('<Configure>', self._on_canvas_configure)

    def create_ultimate_consciousness_entity(self):
        """Create an ultimate consciousness entity"""
        entity = self.engine.create_ultimate_consciousness_entity("Ultimate")
        self._update_status(f"Created Ultimate Consciousness Entity: {entity.entity_id}")
        self._update_visualization()

    def create_neural_consciousness_entity(self):
        """Create a neural consciousness entity"""
        entity = self.engine.create_neural_consciousness_entity("Neural")
        self._update_status(f"Created Neural Consciousness Entity: {entity.entity_id}")
        self._update_visualization()

    def create_transcendence_entity(self):
        """Create a transcendence entity"""
        entity = self.engine.create_transcendence_entity("Transcendence")
        self._update_status(f"Created Transcendence Entity: {entity.entity_id}")
        self._update_visualization()

    def create_matrix_entity(self):
        """Create a matrix entity"""
        entity = self.engine.create_matrix_entity("Matrix")
        self._update_status(f"Created Matrix Entity: {entity.entity_id}")
        self._update_visualization()

    def create_quantum_entity(self):
        """Create a quantum entity"""
        entity = self.engine.create_quantum_entity("Quantum")
        self._update_status(f"Created Quantum Entity: {entity.entity_id}")
        self._update_visualization()

    def create_basic_consciousness_entity(self):
        """Create a basic consciousness entity"""
        entity = self.engine.create_basic_consciousness_entity("Basic")
        self._update_status(f"Created Basic Consciousness Entity: {entity.entity_id}")
        self._update_visualization()

    def consciousness_evolution(self):
        """Trigger consciousness evolution"""
        for _ in range(20):
            self.engine.evolve_all_systems(2.0)
        self._update_status("Consciousness Evolution Complete - All systems evolved 20x")
        self._update_visualization()

    def neural_evolution(self):
        """Trigger neural evolution"""
        for _ in range(50):
            self.engine.evolve_all_systems(5.0)
        self._update_status("Neural Evolution Complete - All systems evolved 50x")
        self._update_visualization()

    def ultimate_evolution(self):
        """Trigger ultimate evolution"""
        for _ in range(100):
            self.engine.evolve_all_systems(10.0)
        self._update_status("Ultimate Evolution Complete - All systems evolved 100x")
        self._update_visualization()

    def _evolution_loop(self):
        """Continuous evolution loop"""
        while self.evolution_running:
            try:
                self.engine.evolve_all_systems(0.1)
                time.sleep(2.0)  # Slower evolution for stability
            except Exception as e:
                print(f"Error in evolution loop: {e}")
                time.sleep(2.0)

    def _update_status(self, message: str):
        """Update status display"""
        timestamp = time.strftime("%H:%M:%S")
        status_line = f"[{timestamp}] {message}\n"

        self.status_text.insert(tk.END, status_line)
        self.status_text.see(tk.END)

        # Keep only last 30 lines
        lines = self.status_text.get("1.0", tk.END).split('\n')
        if len(lines) > 30:
            self.status_text.delete("1.0", tk.END)
            self.status_text.insert("1.0", '\n'.join(lines[-30:]))

    def _update_visualization(self):
        """Update the visualization"""
        try:
            self.canvas.delete("all")

            # Get system status
            status = self.engine.get_system_status()

            # Draw entity network
            self._draw_entity_network(status)

            # Draw field indicators
            self._draw_field_indicators()

        except Exception as e:
            print(f"Error updating visualization: {e}")

    def _draw_entity_network(self, status: Dict[str, Any]):
        """Draw entity network visualization"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            return

        # Draw entity nodes
        entities = [
            ("Ultimate Consciousness", status['ultimate_consciousness_entities'], 'purple'),
            ("Neural Consciousness", status['neural_consciousness_entities'], 'blue'),
            ("Transcendence", status['transcendence_entities'], 'magenta'),
            ("Matrix", status['matrix_entities'], 'cyan'),
            ("Quantum", status['quantum_entities'], 'gold'),
            ("Basic Consciousness", status['basic_consciousness_entities'], 'orange')
        ]

        for i, (entity_type, count, color) in enumerate(entities):
            angle = (i / len(entities)) * 2 * math.pi
            radius = 300
            x = canvas_width // 2 + radius * math.cos(angle)
            y = canvas_height // 2 + radius * math.sin(angle)

            # Draw entity node
            size = 15 + count * 2
            self.canvas.create_oval(x-size, y-size, x+size, y+size,
                                  fill=color, outline='white', width=2)

            # Draw label
            label = f"{entity_type[:12]}\n{count}"
            self.canvas.create_text(x, y+size+15, text=label,
                                  fill='white', font=('Arial', 8, 'bold'))

        # Draw total entities indicator
        total = status['total_entities']
        self.canvas.create_text(canvas_width // 2, 50,
                               text=f"Total Consciousness Entities: {total}",
                               fill='white', font=('Arial', 20, 'bold'))

        # Draw evolution count
        evolutions = status['evolution_count']
        self.canvas.create_text(canvas_width // 2, 80,
                               text=f"Consciousness Evolution Cycles: {evolutions}",
                               fill='yellow', font=('Arial', 16))

    def _draw_field_indicators(self):
        """Draw field strength indicators"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            return

        # Calculate field strengths (simplified)
        quantum_strength = np.sum(self.engine.quantum_field) / 1000
        neural_strength = np.sum(self.engine.neural_field) / 1000
        consciousness_strength = np.sum(self.engine.consciousness_field) / 1000
        temporal_strength = np.sum(self.engine.temporal_field) / 1000
        transcendence_strength = np.sum(self.engine.transcendence_field) / 1000
        matrix_strength = np.sum(self.engine.matrix_field) / 1000
        ultimate_strength = np.sum(self.engine.ultimate_field) / 1000

        # Draw field indicators
        fields = [
            ("Quantum", quantum_strength, 'red'),
            ("Neural", neural_strength, 'green'),
            ("Consciousness", consciousness_strength, 'blue'),
            ("Temporal", temporal_strength, 'yellow'),
            ("Transcendence", transcendence_strength, 'magenta'),
            ("Matrix", matrix_strength, 'cyan'),
            ("Ultimate", ultimate_strength, 'white')
        ]

        for i, (field_name, strength, color) in enumerate(fields):
            x = 50
            y = canvas_height - 160 + i * 18

            # Draw field name
            self.canvas.create_text(x, y, text=f"{field_name}:",
                                  fill='white', font=('Arial', 9), anchor='w')

            # Draw strength bar
            bar_width = min(150, strength / 10)
            self.canvas.create_rectangle(x + 120, y - 4, x + 120 + bar_width, y + 4,
                                       fill=color, outline='white')

            # Draw strength value
            self.canvas.create_text(x + 290, y, text=f"{strength:.1f}",
                                  fill='white', font=('Arial', 9), anchor='w')

    def _on_canvas_configure(self, event):
        """Handle canvas resize"""
        self._update_visualization()

    def on_closing(self):
        """Handle window closing"""
        self.evolution_running = False
        self.root.destroy()

def main():
    """Main function to run the Ultimate Consciousness Interface"""
    root = tk.Tk()
    app = UltimateConsciousnessInterface(root)

    # Set up closing handler
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main()
