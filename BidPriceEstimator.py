import numpy as np
import pandas as pd
from Evaluator import * #name overlap

class BidEstimator():

    def linearBidPrice(self, y_pred, base_bid, avg_ctr):
        '''
        Based on the formula
            bid = base_bid x (pCTR/avgCTR)

        p_ctr = prob of 1 from model
        avg_ctr = np.count_nonzero(testset)/len(testset)


        :param y_pred: Array of prediction based on 1 and 0. 1 means click
        :param base_bid: A integer value between 1 to 1000 or anything
        :param avg_ctr:
        :return:
        '''
        # print("y_pred: ", y_pred[0:10])
        #bids = [base_bid * (i/avg_ctr) for i in y_pred]
        bids = base_bid * (y_pred / avg_ctr)
        # print("ave bid: ", np.mean(bids))
        # print(bids[0:10])

        return bids

    def linearBidPrice_mConfi(self, y_pred, base_bid, variable_bid, m_conf):
        '''
        Based on the formula
            bid = base_bid + variable_bid ( (y_pred[i] - m_conf) / (1-m_conf) ) if y_pred[i] > m_conf
            -1                                                                  else

        1. Only bid when confidence is higher than m_conf
        2. Price to bid is depend on the confidence level

        :param y_pred: Array of prediction based on 1 and 0. 1 means click
        :param base_bid: A integer value between 1 to 1000 or anything
        :param variable_bid: Range of variable bid
        :param m_conf: Minimum confidence level
        :return:
        '''
        # bids = [base_bid * (i/avg_ctr) if i>min_confidence else -1 for i in y_pred]
        bids = [base_bid + ((i-m_conf / 1-m_conf)*variable_bid) if i > m_conf else -1 for i in y_pred]
        # print("y_pred: ", y_pred[0:20])
        # print(bids[0:20])

        return bids

    def confidenceBidPrice(self, y_pred, base_bid, max_variable_bid):
        '''
        Bid higher when the click prediction is more confident

        Bid = base_bid + (Confidence for the impression * max_variable_bid)

        :param y_pred: Array of prediction in their original confidence
        :param base_bid: The base price to bid
        :param max_variable_bid: Variable component
        :return: bids
        '''
        bid = []
        for i in y_pred:
            bid.append(base_bid+int(i*max_variable_bid))

        return bid

    def linearBidPrice_variation(self, y_prob, base_bid, avg_ctr, slotprices, prune_thresh):
        # 1. Get linear bid
        # 2. Increase bid to min slot price
        # 3. Prune those below pred thresh

        # 1. Get linear bid
        initial_bids = self.linearBidPrice(y_prob, base_bid, avg_ctr)
        print('inital bid total               : {}'.format(int(initial_bids.sum())))

        # 2. Increase bid to min slot price + bit of fudge
        bids_reserve_price_met = np.maximum(initial_bids, slotprices * 1.1)
        print('bid total post-reserve match   : {}'.format(int(bids_reserve_price_met.sum())))
        ## alternative where we prune instead:
        # bids_reserve_price_met = np.ma.masked_less(initial_bids, slotprices)  # mask out values less than
        # np.ma.set_fill_value(bids_reserve_price_met, 0.0)
        # # print(bids_reserve_price_met.filled()) # return with filled value i.e masked out values become 0
        # print('bid total post-reserve prune   : {}'.format(int(bids_reserve_price_met.filled().sum())))

        # 3. Prune those below pred thresh
        prune_tresh_mask = np.less(y_prob, prune_thresh)
        # print(prune_tresh_mask)
        # bids_click_thresh_mask = np.ma.masked_array(bids_reserve_price_met.filled(), prune_tresh_mask) #this is for the alternative step 2.
        bids_click_thresh_mask = np.ma.masked_array(bids_reserve_price_met, prune_tresh_mask)
        np.ma.set_fill_value(bids_click_thresh_mask, 0.0)
        # print(bids_click_thresh_mask.filled()) # return with filled value i.e masked out values become 0
        print('bid total post-prob {0:.2f} prune  : {1}'.format(prune_thresh, int(bids_click_thresh_mask.filled().sum())))

        return bids_click_thresh_mask.filled().astype(int)

    def gridSearch_linearBidPrice_variation(self,y_prob, avg_ctr, slotprices,gold_df,budget=25000000):
        # TODO this could be generalised to other models too.
        performance_list = []
        for pred_threshold in np.arange(0.05,1.00,0.05): #np.arange(0.1,1.00,0.1): #
            print("== pred_threshold = {}".format(pred_threshold))
            for base_bid in range(50,500,10):#range(100,300,10):
                print(" = base_bid = {}".format(base_bid))
                bids=self.linearBidPrice_variation(y_prob,base_bid,avg_ctr, slotprices,pred_threshold)
                # format bids into bidids pandas frame
                est_bids_df = gold_df[['bidid']].copy()
                est_bids_df['bidprice'] = bids
                myEvaluator = Evaluator()
                myEvaluator.computePerformanceMetricsDF(budget, est_bids_df, gold_df, verbose=True)
                #myEvaluator.printResult()
                myEvaluator.resultDict['pred_threshold']=pred_threshold
                myEvaluator.resultDict['base_bid']=base_bid
                #print(myEvaluator.resultDict)
                performance_list+=[myEvaluator.resultDict]

        ## stick performance metrics into pandas frame
        performance_pd = pd.DataFrame(performance_list,columns=['base_bid', 'pred_threshold', 'won', 'click', 'spend', 'trimmed_bids', 'CTR', 'CPM', 'CPC'])
        print("GRID SEARCH PERF TABLE")
        print(performance_pd)

        ## Determine 'best' params from 'CTR', 'click'/total_gold_clicks, 1-'spend'/max_budget,
        total_gold_clicks = len(gold_df[gold_df['click'] == 1])
        perf_score = performance_pd.apply(lambda x: x['CTR'] * 0.5 + (x['click']/ total_gold_clicks)*0.3 + (1-x['spend']/budget) * 0.2, axis=1)
        print("GRID SEARCH PERF SCORE")
        print(perf_score)
        best_idx=perf_score.idxmax(axis=0)

        print("best score {}".format(perf_score[best_idx]))
        print(performance_pd.loc[best_idx])

        best_pred_thresh=performance_pd['pred_threshold'][best_idx]
        best_base_bid=performance_pd['base_bid'][best_idx]

        return best_pred_thresh,best_base_bid