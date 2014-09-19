%% Start assignment 1
close all
clear all
tic
clc

%% Input

%Read the data into matrices
A = dlmread('data/features.txt'); B = dlmread('data/targets.txt');


%translate targets to the binary code the nnw will produce
targets = full(ind2vec(B'))';
clear j

hidden_neurons = 30;    %number of hidden neurons
alpha = 0.1;            %learning rate

training_set = A(1:4000,:);    %training set is first 5000 data
validation_set = A(4001:5500,:);
test_set = A(5501:length(A),:);

training_targets = targets(1:4000,:);
validation_targets = targets(4001:5500,:);
test_targets = targets(5501:length(targets),:);

training_B = B(1:4000);
validation_B = B(4001:5500);
test_B = B(5501:length(B));
test_prestatie_best = 0

validation_mse = zeros(1,250);
%validation_mse(1) = 1;

for cycle = 1:10
    
    wij = zeros(hidden_neurons,10);
    wjk = zeros(7,hidden_neurons);
    treshold_hl = zeros(1,hidden_neurons);
    treshold_ol = zeros(1,7);
    mse = zeros(1,250);
    output = zeros(length(training_set),7);
    
    validation_msqe = zeros(1,length(validation_set));
    validation_output = zeros(length(validation_set),7);
    validation_fout = zeros(1,250);
    
    %initial weights are random numbers from -1 to 1 for ten hidden neurons
    for gewicht = 1:hidden_neurons
        for gewwicht = 1:10
            wij(gewicht,gewwicht) = 2*rand - 1;
        end
        
        for gewwicht = 1:7
            wjk(gewwicht,gewicht) = 2*rand - 1;
            treshold_ol(gewwicht) = 4*rand - 2;
        end
        
        %tresholds are randum numbers from -2 to 2 for two layers
        treshold_hl(gewicht) = 4*rand - 2;
        
    end
    clear gewicht gewwicht
    
    %Ten input neurons; one for each sample
    
    weighted_sum_ij = zeros(1,hidden_neurons);
    weighted_sum_jk = zeros(1,7);
    msqe = 1;
    delta_wjk = zeros(7,hidden_neurons);
    delta_wij = zeros(hidden_neurons,10);
    delta_j = zeros(1,hidden_neurons);
    epoch = 1;
    mse(1) = 1;
    stop = 0;
    
    
    
    while mse(epoch) > 10^(-4) && epoch < 100 && stop == 0
        epoch = epoch + 1;
        msqe = zeros(1,length(training_set));
        for h = 1:length(training_set)
            for i = 1:hidden_neurons
                %Apply weights and calculate sum
                weight = wij(i,:);
                weighted_sum_ij(i) = sum(A(h,:) .* weight);
            end
            
            %calculate the activation function of the hidden layer
            hidden_layer = 1./(1 + exp(-(weighted_sum_ij - treshold_hl)));
            
            for j = 1:7
                %Apply weights and calculate sum
                weight = wjk(j,:);
                weighted_sum_jk(j) = sum(hidden_layer .* weight);
            end
            
            %calculate the activation function of the output layer
            output(h,:) = 1./(1 + exp(-(weighted_sum_jk - treshold_ol)));
            
            %calculate the error
            error = training_targets(h,:) - output(h,:);
            msqe(h) = mean(error.^2);
            delta_k = output(h,:) .* (1 - output(h,:)) .* error;
            
            %The sum of delta_k and wjk is calculated for every value of j.
            for k = 1:hidden_neurons
                delta_j(k) = hidden_layer(k) .* (1 - hidden_layer(k)) .* sum(delta_k .* wjk(:,k)');
            end
            
            %update the weights of the output layer
            delta_wjk = alpha * (delta_k' * hidden_layer);
            wjk = wjk + delta_wjk;
            
            %update the tresholds of the output layer
            delta_theta_k = alpha * (-1) * delta_k;
            treshold_ol = treshold_ol + delta_theta_k;
            
            %update the weights of the hidden layer
            delta_wij = alpha * (A(length(training_set),:)' * delta_j)';
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
        
        %Validation of the system
        for i = 1:length(validation_set)
            for j = 1:hidden_neurons
                weighted_sum_ij(j) = sum(validation_set(i,:).*wij(j,:));
            end
            hidden_layer(i,:) = 1./(1 + exp(-(weighted_sum_ij - treshold_hl)));
            
            for j = 1:7
                weighted_sum_jk(j) = sum(hidden_layer(i,:) .* wjk(j,:));
            end
            
            validation_output(i,:) = 1./(1 + exp(-(weighted_sum_jk - treshold_ol)));
            validation_error = validation_targets(i,:) - validation_output(i,:);
            validation_msqe(i) = mean(validation_error.^2);
            
            
            
        end
        
        if epoch > 40
            if abs(mse(epoch) - mse(epoch - 10)) < mse(epoch)/1000 || (validation_fout(epoch) >= validation_fout(epoch - 1) && validation_fout(epoch - 1) >= validation_fout(epoch -2))
                %Stops the looop when the mean square error doesn't change
                %anymore or when the validation_mse starts rising again.
                stop = 1;
            end
        end
        
        %Show the result of the validation
        validation_class = vec2ind(validation_output');
        validation_fout(epoch) = nnz(validation_class - validation_B');
        validation_mse(epoch) = mean(validation_msqe);
        
    end
    validation_prestatie = 1 - mean(nonzeros(validation_fout'))/length(validation_set);
    clear validation fout class MAX hidden_layer output
    
    test_set = test_set;
    
    
    for i = 1:length(test_set)
        for j = 1:hidden_neurons
            weight = wij(j,:);
            weighted_sum_ij(j) = sum(test_set(i,:).*weight);
        end
        hidden_layer(i,:) = 1./(1 + exp(-(weighted_sum_ij - treshold_hl(:,:))));
        
        for j = 1:7
            weight = wjk(j,:);
            weighted_sum_jk(j) = sum(hidden_layer(i,:) .* weight);
        end
        
        output(i,:) = 1./(1 + exp(-(weighted_sum_jk - treshold_ol(:,:))));
    end
    
    class = vec2ind(output');
    validation = class' - test_B;
    test_prestatie = 1 - nnz(validation)/length(test_B);
    
    
    
    if test_prestatie > test_prestatie_best
        wij_best = wij;
        wjk_best = wjk;
        treshold_ol_best = treshold_ol;
        treshold_hl_best = treshold_hl;
        test_prestatie_best = test_prestatie;
    end
    
end
clear h i j weight

figure
x = 1:length(mse);
semilogy(x,mse)
hold on
semilogy(1:length(validation_mse),validation_mse,'r');

figure
plot(1:length(validation_fout),validation_fout);

figure
for i = 1:10
    hold all
    semilogy(validation_mse(:,i));
end
%make the figure more clear
legend('1','2','3','4','5','6','7','8','9','10');
title('The change of the MSE for different initial values');
xlabel('number of epochs');
ylabel('Mean-square error');

%define the class
class = vec2ind(output');
test = class' - B(1:length(class));
prestatie = 1 - nnz(test)/length(class);

toc

