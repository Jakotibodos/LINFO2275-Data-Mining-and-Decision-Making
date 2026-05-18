To test a saved model, run test.py.
You can select which model to train by modifying the "--saved_model" argument.
If you select model "cnn_model", you need to specify argument "--use_cnn" as True
Occasionally, a window will pop-up showing the gameplay of the current epoch. You can change the frequency of apparition of this window on line 103.

To train a new model, run train.py
If you want to further train an existing model, specify argument "--model_path"
If you want to train a model using CNN, you need to specify argument "--use_cnn" as True

Due to size constraints, only the final cnn model is saved in folder "trained_models".