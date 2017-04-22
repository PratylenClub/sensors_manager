from Neuron import LIF_neuron
import pickle
import pandas as pd
import numpy as np

class neural_network:
        def __init__(self, model):
                self.model = model
                self.neural_network = {}
                for neuron_name,n in self.model["Cells_types"].iteritems():
                        self.neural_network[neuron_name] = LIF_neuron()
                for neuron_name,n in self.model["Neural Network"].iteritems():
                        for neuron_name_2,weight in n.iteritems():
                                self.neural_network[neuron_name].append_neighbor({neuron_name_2:{"Cell":self.neural_network[neuron_name_2],"Weight":weight}})
                self.activity = pd.Series(index = self.neural_network.keys())
                self.nb_neurons_firing = {type_neuron: 0 for type_neuron in np.unique(self.model["Cells_types"].values())}

        def update_neural_network(self):
                for neuron_name in self.neural_network:
                        nb_neurons_firing_local = self.neural_network[neuron_name].update()
                        self.activity[neuron_name] = self.neural_network[neuron_name].Vm
                        self.nb_neurons_firing[self.model["Cells_types"][neuron_name]] += nb_neurons_firing_local

        def reset(self):
                for neuron_name in self.neural_network:
                        self.activity[neuron_name] = 0
                        self.neural_network[neuron_name].Vm = 0
                        self.neural_network[neuron_name].I_local *= 0
                        self.neural_network[neuron_name].t_res = 0
                        self.neural_network[neuron_name].current_I_index = 0
                self.nb_neurons_firing = {type_neuron: 0 for type_neuron in np.unique(self.model["Cells_types"].values())}

if __name__ == "__main__":
        celegans = pickle.load(open("connectome_manager/models/celegans3000_full_neuroml.pickle","rb"))
        celegans_nn = neural_network(celegans)
        I = np.ones(100)*3
        dt = 0.01
        results = {}
        for neuron in celegans_nn.neural_network.keys()[0:2]:
                for i in range(1000):
                        celegans_nn.neural_network[neuron].update_I(I)
                        celegans_nn.update_neural_network()
                        celegans_nn.update_neural_network()
                results[neuron] = celegans_nn.nb_neurons_firing 
        print results
        #pickle.dump(results,open("RESULTS","rb"))