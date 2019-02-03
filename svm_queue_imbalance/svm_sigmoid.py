import logging
import os

import pandas as pd
from lob_data_utils import roc_results, stocks_numbers
from lob_data_utils.lob_classify import LobClassify

logger = logging.getLogger(__name__)


def main(stock):
    results_dir = 'res_svm'
    data_length = 24000
    svm_gdf_res = LobClassify(stock, data_length=data_length,
                              data_dir='../data/prepared')
    weights = svm_gdf_res.get_classes_weights()
    results = []
    for C in [0.001, 0.01, 0.1, 1, 10, 100]: #, 1000]:
        for g in [0.001, 0.01, 0.1, 1, 10, 100]: #1000]:
            for coef0 in [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]:
                scores = svm_gdf_res.train_svm(C=C, gamma=g, kernel='sigmoid', feature_name='que', coef0=coef0,
                                               class_weight=weights)
                results.append(scores)
        pd.DataFrame(results).to_csv(
            os.path.join(results_dir, 'svm_sigmoid_{}_len{}.csv_partial'.format(stock, data_length)))
    pd.DataFrame(results).to_csv(
        os.path.join(results_dir, 'svm_prev_sigmoid_{}_len{}.csv'.format(stock, data_length)))


if __name__ == '__main__':
    from multiprocessing import Pool

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

    pool = Pool(processes=2)
   # stocks = stocks_numbers.chosen_stocks
    stocks = ['9268', '4549']
    res = [pool.apply_async(main, [s]) for s in stocks]
    print([r.get() for r in res])
