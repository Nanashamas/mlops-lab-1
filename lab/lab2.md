### Question 7: In the mlflow UI, open the food11 experiment. Select these runs and click "Compare". Which learning rate gave the best val_accuracy? Is higher always better?
- The learning rate that gave the best `val_accuracy` is **`lr = 0.0001`**, achieving a validation accuracy of **73.81%** (and test accuracy of **78.01%**).
- **Is higher always better?** No. Higher learning rates (such as `0.01`) caused unstable weight updates, resulting in poor validation accuracy (~12.59%). A smaller learning rate is essential when fine-tuning a pretrained model to prevent destroying existing useful representations.

### Question 8: Use the parallel coordinates plot on the compare page to look at lr, batch_size and val_accuracy together. What pattern do you see?
- The parallel coordinates plot clearly shows that runs with the lowest learning rate (`0.0001`) converge to the highest validation accuracy (represented by the highest point on the `val_accuracy` axis).
- A batch size of `32` combined with `lr = 0.0001` yielded optimal results on the mini dataset.
- Increasing the batch size to `64` reduced the number of optimization steps per epoch, leading to lower performance compared to batch size `32` under the same number of epochs.

### Question 9: Sort the runs table by val_accuracy descending. Which run is the best one? Note its run ID, you'll need it in the next lab.
- **Best Run Name:** `flawless-tern-879`
- **Best Run ID:** `03a6c8bb8d84470fa1327ac0cbdf6473`
- **Validation Accuracy:** `0.73814`
- **Test Accuracy:** `0.7801`