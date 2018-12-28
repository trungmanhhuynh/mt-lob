import logging
import os
from typing import Optional

import numpy as np
import pandas as pd
from lob_data_utils import lob, model, roc_results
from sklearn.decomposition import PCA
from sklearn.svm import SVC


logger = logging.getLogger(__name__)


class SvmGdfResults(object):

    def __init__(self, stock, r=1.0, s=1.0, data_length=10000, gdf_filename_pattern='',
                 data_dir='../gaussian_filter/data_gdf'):
        self.stock = stock
        self.r = r
        self.s = s
        self.data_length = data_length
        self.gdf_filename_pattern = gdf_filename_pattern
        self.data_dir = data_dir
        self.df, self.df_test = self._read_stock()

    all_gdf = ['gdf_{}'.format(i) for i in range(0, 50)]
    all_gdf_que = ['gdf_{}'.format(i) for i in range(0, 50)] + ['queue_imbalance']
    all_gdf_que_prev = ['gdf_{}'.format(i) for i in range(0, 50)] + ['queue_imbalance', 'prev_queue_imbalance']

    feature_columns_dict = {
        'que': ['queue_imbalance'],
        'que_prev': ['queue_imbalance', 'prev_queue_imbalance'],
        'gdf_24_26': ['gdf_24', 'gdf_25'],
        'gdf_24-26_que': ['gdf_24', 'gdf_25', 'queue_imbalance'],
        'gdf_24-26_que_prev': ['gdf_24', 'gdf_25', 'queue_imbalance', 'prev_queue_imbalance'],
        'gdf_23-27': ['gdf_23', 'gdf_24', 'gdf_25', 'gdf_26'],
        'gdf_23-27_que': ['gdf_23', 'gdf_24', 'gdf_25', 'gdf_26', 'queue_imbalance'],
        'gdf_23-27_que_prev': ['gdf_23', 'gdf_24', 'gdf_25', 'gdf_26', 'queue_imbalance', 'prev_queue_imbalance'],
        'gdf_20_30': ['gdf_{}'.format(i) for i in range(20, 30)],
        'gdf_20_30_que': ['gdf_{}'.format(i) for i in range(20, 30)] + ['queue_imbalance'],
        'gdf_20_30_que_prev': ['gdf_{}'.format(i) for i in range(20, 30)] + ['queue_imbalance', 'prev_queue_imbalance'],
        'gdf_0_50': all_gdf,
        'gdf_0-50_que': all_gdf_que,
        'gdf_0-50_que_prev': all_gdf_que_prev,
        'pca_gdf1': all_gdf,
        'pca_gdf2': all_gdf,
        'pca_gdf3': all_gdf,
        'pca_gdf4': all_gdf,
        'pca_gdf5': all_gdf,
        'pca_gdf6': all_gdf,
        'pca_gdf7': all_gdf,
        'pca_gdf8': all_gdf,
        'pca_gdf9': all_gdf,
        'pca_gdf10': all_gdf,
        'pca_gdf_que1': all_gdf_que,
        'pca_gdf_que2': all_gdf_que,
        'pca_gdf_que3': all_gdf_que,
        'pca_gdf_que4': all_gdf_que,
        'pca_gdf_que5': all_gdf_que,
        'pca_gdf_que6': all_gdf_que,
        'pca_gdf_que7': all_gdf_que,
        'pca_gdf_que8': all_gdf_que,
        'pca_gdf_que9': all_gdf_que,
        'pca_gdf_que10': all_gdf_que,
        'pca_gdf_que_prev1': all_gdf_que_prev,
        'pca_gdf_que_prev2': all_gdf_que_prev,
        'pca_gdf_que_prev3': all_gdf_que_prev,
        'pca_gdf_que_prev4': all_gdf_que_prev,
        'pca_gdf_que_prev5': all_gdf_que_prev,
        'pca_gdf_que_prev6': all_gdf_que_prev,
        'pca_gdf_que_prev7': all_gdf_que_prev,
        'pca_gdf_que_prev8': all_gdf_que_prev,
        'pca_gdf_que_prev9': all_gdf_que_prev,
        'pca_gdf_que_prev10': all_gdf_que_prev,
    }

    def get_score_for_clf(self, clf, df_test, feature_name, pca=None):
        x_test = df_test[self.feature_columns_dict[feature_name]]
        if pca:
            x_test = pca.transform(x_test)
        y_test = df_test['mid_price_indicator'].values
        return model.test_model(clf, x_test, y_test)

    @staticmethod
    def get_number_of_pca_components(feature_name: str) -> Optional[int]:
        if 'pca_gdf_que_prev' in feature_name:
            return int(feature_name.replace('pca_gdf_que_prev', ''))
        if 'pca_gdf_que' in feature_name:
            return int(feature_name.replace('pca_gdf_que', ''))
        if 'pca_gdf' in feature_name:
            return int(feature_name.replace('pca_gdf', ''))
        return None

    @staticmethod
    def get_mean_scores(scores: dict) -> dict:
        mean_scores = {}
        for k, v in scores.items():
            mean_scores[k] = np.mean(v)
        return mean_scores

    def train_log(self, clf, feature_name='', should_validate=True):
        logger.info('Training %s r=%s s=%s: clf=%s',
                    self.stock, self.r, self.s, clf)
        train_x = self.df[self.feature_columns_dict[feature_name]]
        n_components = self.get_number_of_pca_components(feature_name)
        pca = None
        if n_components:
            pca = PCA(n_components=n_components)
            pca.fit(train_x)
            train_x = pca.transform(train_x)
        if should_validate:
            scores_arrays = model.validate_model(clf, train_x, self.df['mid_price_indicator'])
            scores = self.get_mean_scores(scores_arrays)
        else:
            scores = model.train_model(clf, train_x, self.df['mid_price_indicator'])
        res = {
            **scores,
            'stock': self.stock,
            'kernel': 'logistic',
            'features': feature_name
        }
        test_scores = self.get_score_for_clf(clf, self.df_test, feature_name=feature_name, pca=pca)
        logger.info('Finished training %s %s', self.stock, {**res, **test_scores})
        return {**res, **test_scores}

    def train_svm(self, C=np.nan, gamma=np.nan, feature_name='', kernel='rbf', coef0=np.nan, should_validate=True):
        logger.info('Training %s r=%s s=%s: kernel=%s C=%s gamma=%s coef0=%s',
                    self.stock, self.r, self.s, kernel, C, gamma, coef0)
        if C and gamma and coef0:
            clf = SVC(kernel=kernel, C=C, gamma=gamma, coef0=coef0)
        elif C and gamma:
            clf = SVC(kernel=kernel, C=C, gamma=gamma)
        else:
            clf = SVC(kernel=kernel)
        train_x = self.df[self.feature_columns_dict[feature_name]]
        n_components = self.get_number_of_pca_components(feature_name)
        pca = None
        if n_components:
            pca = PCA(n_components=n_components)
            pca.fit(train_x)
            train_x = pca.transform(train_x)
        if should_validate:
            scores_arrays = model.validate_model(clf, train_x, self.df['mid_price_indicator'])
            scores = self.get_mean_scores(scores_arrays)
        else:
            scores = model.train_model(clf, train_x, self.df['mid_price_indicator'])
        res = {
            **scores,
            'stock': self.stock,
            'C': C,
            'gamma': gamma,
            'coef0': coef0,
            'kernel': kernel,
            'features': feature_name
        }
        test_scores = self.get_score_for_clf(clf, self.df_test, feature_name=feature_name, pca=pca)
        logger.info('Finished training %s %s', self.stock, {**res, **test_scores})
        return {**res, **test_scores}

    def _read_stock(self):
        gdf_filename = self.gdf_filename_pattern.format(self.stock, self.r, self.s)
        reg_filename = '{}'.format(self.stock)
        logger.debug('Will read %s and %s', gdf_filename, reg_filename)
        df, df_test = lob.load_prepared_data(
            gdf_filename, data_dir=self.data_dir, cv=False, length=self.data_length)
        df_reg, df_reg_test = lob.load_prepared_data(
            reg_filename, data_dir='../gaussian_filter/data', cv=False, length=self.data_length)
        df['datetime'] = df_reg['Unnamed: 0']
        df['bid_price'] = df_reg['bid_price']
        df['ask_price'] = df_reg['ask_price']
        df['queue_imbalance'] = df_reg['queue_imbalance']
        df['prev_queue_imbalance'] = df['queue_imbalance'].shift()
        df.index = pd.to_datetime(df['datetime'])
        df.dropna(inplace=True)
        df_test['datetime'] = df_reg_test['Unnamed: 0']
        df_test['bid_price'] = df_reg_test['bid_price']
        df_test['ask_price'] = df_reg_test['ask_price']
        df_test['queue_imbalance'] = df_reg_test['queue_imbalance']
        df_test['prev_queue_imbalance'] = df_test['queue_imbalance'].shift()
        df_test.index = pd.to_datetime(df_test['datetime'])
        df_test.dropna(inplace=True)
        return df, df_test

    def features(self, clf) -> pd.DataFrame:
        res = []

        for feature_name, features in self.feature_columns_dict.items():
            logger.debug('Checking feature %s for %s r=%s s=%s', feature_name, self.stock, self.r, self.s)
            train_x = self.df[features]
            n_components = self.get_number_of_pca_components(feature_name)
            if n_components:
                pca = PCA(n_components=n_components)
                pca.fit(train_x)
                train_x = pca.transform(train_x)
            scores = model.validate_model(clf, train_x, self.df['mid_price_indicator'])
            df_score = pd.DataFrame(scores)
            scores = {
                'matthews': np.mean(df_score['matthews'].values),
                'f1': np.mean(df_score['f1'].values),
                'roc_auc': np.mean(df_score['roc_auc'].values),
                'stock': self.stock,
                'features': feature_name
            }
            logger.info('Scores %s r=%s s=%s - %s', self.stock, self.r, self.s, scores)
            res.append(scores)
        return pd.DataFrame(res)


