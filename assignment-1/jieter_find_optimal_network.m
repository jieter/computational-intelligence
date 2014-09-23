% TI2730B computational intelligence
%
% Find the best network.
% Jan Pieter Waagmeester

epochs = 100;
no_tries = 100;
min_hidden_neurons = 19;
max_hidden_neurons = 25;

fprintf('Find the best network: %d tries, %d epochs.\n', no_tries, epochs);

for hidden_neurons = min_hidden_neurons:max_hidden_neurons
    fprintf('Test with %d hidden neurons: ', hidden_neurons);
    for i = 1:no_tries

        [success_rate, w_ij, w_jk, threshold_hidden, threshold_output] = jieter_ANN(hidden_neurons, epochs, false);

        fprintf('.');
        save(sprintf('networks/network-weights-%0.5f.mat', success_rate), ...,
        	 'epochs', 'hidden_neurons', 'success_rate', 'w_ij', 'w_jk', 'threshold_output', 'threshold_hidden');
    end
    fprintf('\n');
end
