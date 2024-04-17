import pandas as pd
import random
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from sklearn.utils import shuffle
from sklearn.metrics import recall_score, accuracy_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

DATA_FILE_PATH = '../RecordedVideos/fittingParameters.csv'
COMPONENTS = ['atmega']
DATA_COLS = ['a_rise', 'b_rise', 'c_rise', 'a_fall', 'b_fall', 'c_fall']
MODELS = [LogisticRegression, RandomForestClassifier, SVC]


def read_in_data(csv_path, components):
    all_data = pd.read_csv(csv_path)

    # dropping nan values
    all_data = all_data.dropna()

    # filtering by component
    all_data = all_data[all_data['Component'].isin(components)]

    return all_data[all_data['Board Type'] == 'baseline'], all_data[all_data['Board Type'] == 'microphone']


def split_data(baseline_data, mic_data, mic_train_boards=3, base_train_boards=3):
    b, m = ['A', 'B', 'C', 'D', 'E'], ['A', 'B', 'C', 'D', 'E']

    random.shuffle(b)
    random.shuffle(m)

    base_train_boards = b[:base_train_boards]
    mic_train_boards = m[:mic_train_boards]

    base_train, base_test = split_by_board(baseline_data, base_train_boards)
    mic_train, mic_test = split_by_board(mic_data, mic_train_boards)

    train_x = pd.concat([base_train, mic_train])
    test_x = pd.concat([base_test, mic_test])

    print('\nTRAINING SET')
    print(train_x)
    print("\nTESTING SET")
    print(test_x)

    train_x = train_x[DATA_COLS]
    test_x = test_x[DATA_COLS]

    train_y = np.concatenate((np.zeros(base_train.shape[0]), np.ones(mic_train.shape[0])))
    test_y = np.concatenate((np.zeros(base_test.shape[0]), np.ones(mic_test.shape[0])))

    return shuffle(train_x, train_y), (test_x, test_y)


def split_by_board(all_data, train_boards):
    grouped = all_data.groupby('Board Instance')
    mic_train_frames, mic_test_frames = [], []
    for board, group in grouped:
        if board in train_boards:
            mic_train_frames.append(group)
        else:
            mic_test_frames.append(group)

    train = pd.concat(mic_train_frames)
    test = pd.concat(mic_test_frames)

    return train, test


if __name__ == '__main__':
    base_data, mic_data = read_in_data(DATA_FILE_PATH, COMPONENTS)

    (train_x, train_y), (test_x, test_y) = split_data(base_data, mic_data)

    # normalizing data
    mm = MinMaxScaler()
    norm = mm.fit(train_x) # fit scaler on training data 
    train_x_norm = norm.transform(train_x) # transform training data 
    test_x_norm = norm.transform(test_x)

    print("\nRESULTS (model type, accuracy, recall)")
    # running on models
    for m in MODELS:
        model = m()
        model.fit(train_x_norm, train_y)
        predictions = model.predict(test_x_norm)
        accuracy = accuracy_score(test_y, predictions)
        recall = recall_score(test_y, predictions, pos_label=1)

        print(m, accuracy, recall)
