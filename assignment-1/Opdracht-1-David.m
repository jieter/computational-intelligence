%% Start assignment 1
close all
clear all
tic
clc

%% Input

%Read the data into matrices
A = dlmread('features.txt'); B = dlmread('targets.txt');


%translate targets to the binary code the nnw will produce
targets = zeros(length(B),max(B));
for j = 1:length(B)
    targets(j,B(j)) = 1;
end
clear j

alpha = 0.1;
training_set = 5000;
%initial weights are random numbers from -1 to 1 for ten hidden neurons
wij = zeros(10,10);
wjk = zeros(7,10);
treshold_hl = zeros(1,10);
treshold_ol = zeros(1,7);
mse = zeros(1,400);
output = zeros(training_set,7);


%ten different training sets


for gewicht = 1:10
    for gewwicht = 1:10
        wij(gewicht,gewwicht) = 2*rand - 1;
    end
    
    for gewwicht = 1:7
        wjk(gewwicht,gewicht) = 2*rand - 1;
    end
    
    %tresholds are randum numbers from -2 to 2 for two layers
    treshold_hl(:,gewicht) = 4*rand - 2;
    
end
clear gewicht gewwicht 
for gewicht = 1:7
    treshold_ol(:,gewicht) = 4*rand - 2;
end
    %Ten input neurons; one for each sample
    
    weighted_sum_ij = zeros(1,10);
    weighted_sum_jk = zeros(1,7);
    msqe = 1;
    delta_wjk = zeros(7,10);
    delta_wij = zeros(10,10);
    delta_j = zeros(1,10);
    epoch = 1;
    mse(1) = 1;
    
    
while mse(epoch) > 10^(-5) && epoch < 400 && alpha > 10^-6
    epoch = epoch + 1;
    msqe = zeros(1,training_set);
for h = 1:training_set
    for i = 1:10
       %Apply weights and calculate sum
       weight = wij(i,:);
       weighted_sum_ij(:,i) = sum(A(h,:) .* weight);
    end
    
    %calculate the activation function of the hidden layer
    hidden_layer = 1./(1 + exp(-(weighted_sum_ij - treshold_hl)));
    
    for j = 1:7
        %Apply weights and calculate sum
        weight = wjk(j,:);
        weighted_sum_jk(j) = sum(hidden_layer .* weight);
    end
    %only the first seven elements are used
    %weighted_sum_jk(:,:,o) = weighted_sum_jk_step(1:7);
    
    %calculate the activation function of the output layer
    output(h,:) = 1./(1 + exp(-(weighted_sum_jk - treshold_ol)));
    
    %calculate the error
    error = targets(h,:) - output(h,:);
    msqe_iteration = sum(error.^2)/7;
    msqe(:,h) = msqe_iteration;
    delta_k = output(h,:) .* (1 - output(h,:)) .* error;
    
    %The sum of delta_k and wjk is calculated for every value of j. 
    for k = 1:10
        delta_j(k) = hidden_layer(k) .* (1 - hidden_layer(k)) .* sum(delta_k .* wjk(:,k)'); 
    end
    
    %update the weights of the output layer
    delta_wjk = alpha * (delta_k' * hidden_layer);
    wjk = wjk + delta_wjk;
    
    %update the tresholds of the output layer
    delta_theta_k = alpha * (-1) * delta_k;
    treshold_ol = treshold_ol + delta_theta_k;
    
    %update the weights of the hidden layer
    delta_wij = alpha * (A(training_set,:)' * delta_j);
    wij = wij + delta_wij;
    
    %update the tresholds of the hidden layer
    delta_theta_j = alpha * (-1) * delta_j;
    treshold_hl = treshold_hl + delta_theta_j;
    
end 
mse(epoch) = mean(msqe);

%improve the value of alpha
if epoch > 1
if mse(epoch) < mse(epoch - 1)
    alpha = alpha * 1.02;
else 
    alpha = alpha / 1.3;
end
end


disp(epoch); disp(mse(epoch));
end
    clear h i j weight 

    figure 
    x = 1:length(mse);
    semilogy(x,mse)
    
    %define the class
    MAX = max(output');
    for m = 1:training_set
    class(m) = find(output(m,:) == MAX(m));
    end
    validation = class' - B(1:length(class));
    fout = nnz(validation);

toc
