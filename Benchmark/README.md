
This directory offers a benchmark on GPU with two concrete utilizations.
The only thing to do to launch the tests is to go to one of the two subdirectories and run "python main.py" on
a computer with a GPU.

Requirements :
- numpy
- tensorflow-gpu >= 1.5


For the Supervised benchmark, the number of GPUs used can be set with the option --nb_gpu n (for example "python main.py --nb_gpu 2").
The GPUs used will be the 0th to the (n-1)th.


Reinforcement :
    After initializing the network, the algorithm will apply gradient descents and print the time spent every 100 descents.

    Benchmark : on the current GPU of the lab :
    - 100 descents in a mean time of 12s (between 11s and 13s)
    - Total time : ~242s 


Supervised :
    After initializing the network, the algorithm will train a GAN for 2 epochs on 100 batchs.
    
    Benchmark :
    - Une descente de gradient sur un batch en 
    - Total time : 
