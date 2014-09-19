% TI2730B computational intelligence
%
% main neural network function.
%
% Jan Pieter Waagmeester

% number of hidden neurons
hidden_neurons = 18;

% maximum number of epochs
max_epochs = 150;

% if debug is true, jieter_ANN will report progress, generate some figures and
% write the classified unknowns to output/5_classes_<success_rate>.txt
debug_on = true;

% files features.txt, targets.txt and unknown.txt assumed to be in `data/` subdirectory
[success_rate, w_ij, w_jk, threshold_hidden, threshold_output] = jieter_ANN(hidden_neurons, max_epochs, debug_on);

% after training the network, a couple of files are created in `output/`
% - 5_classes_<success_rate>.txt
% - confusion-matrix-h*-e*-t*.(eps|png)
% - learning_curve-<success_rate>.txt

% weights and thresholds available in workspace
% weight matrices are visualised in an image.

fprintf('Network trained with succes rate %f\n', success_rate);

