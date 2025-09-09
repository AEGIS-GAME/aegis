import numpy as np
import os
import matplotlib.pyplot as plt

values = np.load(os.path.join("sys_files", "values.npy"))
labels = np.load(os.path.join("sys_files", "labels.npy"))

# shuffle data
data_size = values.shape[0]
indices = np.arange(data_size)
np.random.shuffle(indices)

values = values[indices]
labels = labels[indices]

# split data
split_index = int(0.8 * data_size)
x_train, x_test = values[:split_index], values[split_index:]
y_train, y_test = labels[:split_index], labels[split_index:]

plt.imshow(values[0], cmap="gray")
plt.title(f"Label: {labels[0]}")
plt.axis("off")
plt.show()

# save data to the 4 spots ! !
agent_training_output_dir = os.path.join("src", "assist", "model_training_data")
ares_testing_output_dir = os.path.join(
    "src", "aegis", "agent_predictions", "model_testing_data"
)

os.makedirs(agent_training_output_dir, exist_ok=True)
os.makedirs(ares_testing_output_dir, exist_ok=True)

np.save(os.path.join(agent_training_output_dir, "x_train_a3.npy"), x_train)
np.save(os.path.join(agent_training_output_dir, "y_train_a3.npy"), y_train)
np.save(os.path.join(ares_testing_output_dir, "x_test_a3.npy"), x_test)
np.save(os.path.join(ares_testing_output_dir, "y_test_a3.npy"), y_test)
