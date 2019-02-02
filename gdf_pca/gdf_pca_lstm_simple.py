import functools
import logging
import os

import pandas as pd
import sklearn
import tensorflow as tf
from keras import backend as K
from keras.layers import Dense
from keras.layers import LSTM
from keras.models import Sequential
from keras import regularizers
from lob_data_utils import gdf_pca, roc_results, stocks_numbers
from numpy.random import seed
seed(1)


def as_keras_metric(method):
    @functools.wraps(method)
    def wrapper(self, args, **kwargs):
        """ Wrapper for turning tensorflow metrics into keras metrics """
        value, update_op = method(self, args, **kwargs)
        K.get_session().run(tf.local_variables_initializer())
        with tf.control_dependencies([update_op]):
            value = tf.identity(value)
        return value

    return wrapper


auc_roc = as_keras_metric(tf.metrics.auc)
mcc = as_keras_metric(sklearn.metrics.matthews_corrcoef)


def train_lstm(stock, r, s, data_length):
    gdf_filename_pattern = 'gdf_{}_r{}_s{}_K50'
    gdf_dfs = gdf_pca.SvmGdfResults(
        str(stock), r=r, s=s, data_length=data_length, gdf_filename_pattern=gdf_filename_pattern)

    units = [4, 6, 8, 12, 16, 20, 24, 32]
    weights = gdf_dfs.get_classes_weights()
    features = ['pca_n_gdf_que', 'pca_n_gdf_que_prev']
    epochs = 10
    batch_size = 300
    n_steps = 5
    scores = []
    filename = os.path.join(
        'res_lstm_weird', f'res_lstm_pca_n_simple_{stock}_len{data_length}_r{r}_s{s}.csv')
    if os.path.exists(filename):
        return
    partial_filename = filename + '_partial'
    if os.path.exists(partial_filename):
        df_partial = pd.read_csv(partial_filename)
        for i, row in df_partial.iterrows():
            scores.append(row.to_dict())
    for unit in units:
        for feature in features:
            if os.path.exists(filename):
                print(f'Exists {filename}.')
                return None
            pca = gdf_dfs.get_pca(feature)
            model = Sequential()
            model.add(LSTM(unit, input_shape=(n_steps, pca.n_components_)))
            model.add(Dense(1, input_shape=(unit, 1), activation='sigmoid'))
            model.compile(loss='binary_crossentropy', optimizer='adam', metrics=[auc_roc])
            plot_name = f'plot_lstm_weird/{stock}_small_u{unit}_pca_n_r{r}_s{s}'
            score = gdf_dfs.train_lstm(
                model, feature_name=feature,
                fit_kwargs={'epochs': epochs, 'batch_size': batch_size, 'verbose': 0, 'shuffle': False},
                compile_kwargs={'loss': 'binary_crossentropy', 'optimizer': 'adam', 'metrics': [auc_roc]},
                plot_name=plot_name, class_weight=weights, n_steps=n_steps)
            score = {**score, 'r': r, 's': s,  'unit': unit, 'arch': model.to_json(),
                     'epochs': epochs, 'batch_size': batch_size, 'n_steps': n_steps}
            scores.append(score)
        pd.DataFrame(scores).to_csv(partial_filename)
    df_scores = pd.DataFrame(scores)
    df_scores.to_csv(filename)
    return True


def main():
    from multiprocessing import Pool
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    data_length = 24000
    stocks = stocks_numbers.chosen_stocks
    pool = Pool(processes=3)
    stocks = ['11869', '4799', '9268']
    res = [pool.apply_async(train_lstm, [s, 0.1, 0.1, data_length]) for s in stocks]
    print([r.get() for r in res])
    res = [pool.apply_async(train_lstm, [s, 0.01, 0.1, data_length]) for s in stocks]
    print([r.get() for r in res])
    res = [pool.apply_async(train_lstm, [s, 0.1, 0.5, data_length]) for s in stocks]
    print([r.get() for r in res])
    res = [pool.apply_async(train_lstm, [s, 0.01, 0.5, data_length]) for s in stocks]
    print([r.get() for r in res])


if __name__ == '__main__':
    main()
