%% Start assignment 1
close all
clear all
tic
clc

%% Input

%Read the data into matrices
A = dlmread('features.txt'); B = dlmread('targets.txt');
alpha = 0.1;

%translate targets to the binary code the nnw will produce
targets = zeros(length(B),max(B));
for j = 1:length(B)
    targets(j,B(j)) = 1;
end
clear j

%initial weights are random numbers from -1 to 1 for ten hidden neurons
wij = zeros(10,10);
wjk = zeros(7,10);
treshold_hl = zeros(1,10);
treshold_ol = zeros(1,7);
for gewicht = 1:10
    for gewwicht = 1:10
    wij(gewicht,gewwicht) = 2*rand - 1;
    wjk(gewicht,gewwicht) = 2*rand - 1;
    end
    %tresholds are randum numbers from -2 to 2 for two layers
    treshold_hl(gewicht) = 4*rand - 2;
    treshold_ol(gewicht) = 4*rand - 2;
end
treshold_ol = treshold_ol(1:7);
clear gewicht gewwicht 


    %Ten input neurons; one for each sample
    weighted_sum_ij = zeros(1,10);
    weighted_sum_jk = zeros(1,10);
for h = 1:3000
    for i = 1:10
       %Apply weights and calculate sum
       weight = wij(i,:);
       weighted_sum_ij(i) = sum(A(h,:) .* weight);
    end
    
    %calculate the activation function of the hidden layer
    hidden_layer = 1./(1 + exp(-(weighted_sum_ij - treshold_hl(1,:))));
    
    for j = 1:7
        %Apply weights and calculate sum
        weight = wjk(j,:);
        weighted_sum_jk(j) = sum(hidden_layer .* weight);
    end
    %only the first seven elements are used
    weighted_sum_jk = weighted_sum_jk(1:7);
    
    %calculate the activation function of the output layer
    output = 1./(1 + exp(-(weighted_sum_jk - treshold_ol)));
    
    %calculate the error
    error = targets(h,:) - output;
    msqe = sum(error.^2)/7;
   
end 
    clear h i j weight hidden_layer
    
toc
