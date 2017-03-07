import ipinyouReader
import ipinyouWriter
import Evaluator
import BidModels
import numpy as np
import LogisticRegressionBidModel


def exeConstantBidModel(validationData, trainData=None, writeResult2CSV=False):
    # Constant Bidding Model
    constantBidModel = BidModels.ConstantBidModel()
    if trainData != None:
        constantBidModel.trainModel(trainData.getTrainData(), searchRange=[1, 500], budget=int(25000*1000*8.88))

    bids = constantBidModel.getBidPrice(validationData.getDataFrame().bidid)
    # bids = np.apply_along_axis(constantBidModel.getBidPrice, axis=1, arr=validationData.getTestData())

    if writeResult2CSV:
        ipinyouWriter.ResultWriter().writeResult("resultConstantBidModel.csv", bids)
    # myEvaluator = Evaluator.Evaluator(25000*1000, bids, validationData.getTrainData())
    # myEvaluator.computePerformanceMetrics()
    myEvaluator = Evaluator.Evaluator()
    myEvaluator.computePerformanceMetricsDF(25000 * 1000, bids, validationData.getDataFrame())
    myEvaluator.printResult()

def exeGaussianRandomBidModel(validationData, trainData=None, writeResult2CSV=False):
    # gaussian random Bidding Model
    randomBidModel = BidModels.GaussianRandomBidModel()

    bids = randomBidModel.getBidPrice(validationData.getDataFrame().bidid)
    # bids = np.apply_along_axis(randomBidModel.getBidPrice, axis=1, arr=validationData.getTestData())

    if writeResult2CSV:
        ipinyouWriter.ResultWriter().writeResult("resultGaussianRandomBidModel.csv", bids)
    # myEvaluator = Evaluator.Evaluator(25000*1000, bids, validationData.getTrainData())
    # myEvaluator.computePerformanceMetrics()
    myEvaluator = Evaluator.Evaluator()
    myEvaluator.computePerformanceMetricsDF(25000 * 1000, bids, validationData.getDataFrame())
    myEvaluator.printResult()

def exeUniformRandomBidModel(validationData, trainData=None, writeResult2CSV=False):
    # uniform random Bidding Model
    randomBidModel = BidModels.UniformRandomBidModel(300) #upper bound for random bidding range
    # TODO: could train this too in a range.

    bids = randomBidModel.getBidPrice(validationData.getDataFrame().bidid)
    # bids = np.apply_along_axis(randomBidModel.getBidPrice, axis=1, arr=validationData.getTestData())

    if writeResult2CSV:
        ipinyouWriter.ResultWriter().writeResult("resultUniformRandomBidModel.csv", bids)
    # myEvaluator = Evaluator.Evaluator(25000*1000, bids, validationData.getTrainData())
    # myEvaluator.computePerformanceMetrics()
    myEvaluator = Evaluator.Evaluator()
    myEvaluator.computePerformanceMetricsDF(25000 * 1000, bids, validationData.getDataFrame())
    myEvaluator.printResult()

def exeLogisticRegressionBidModel(validationData=None, trainData=None, writeResult2CSV=False):
    lrBidModel=LogisticRegressionBidModel.LogisticRegressionBidModel(regressionFormulaY='click', regressionFormulaX='weekday + hour + region + city + adexchange +slotwidth + slotheight + slotprice + advertiser',cBudget=272.412385*1000, avgCTR=0.2)
    print(type(validationData))
    lrBidModel.trainModel(trainData.getDataFrame(), retrain=True)
    # lrBidModel.gridSearchandCrossValidate(trainData.getDataFrame())

    bids = lrBidModel.getBidPrice(validationData.getDataFrame())
    if writeResult2CSV:
        ipinyouWriter.ResultWriter().writeResult("LRbidModelresult.csv", bids)
    myEvaluator = Evaluator.Evaluator()
    myEvaluator.computePerformanceMetricsDF(25000*1000, bids, validationData.getDataFrame())
    myEvaluator.printResult()



# Read in train.csv to train the model
trainReader = ipinyouReader.ipinyouReader("../dataset/train.csv")
trainData = trainReader.getTrainData()

# Read in Validation.csv for developmental testing
devReader = ipinyouReader.ipinyouReader("../dataset/validation.csv")
devData = devReader.getTestData()

# Execute Constant Bid Model
print("== Constant bid model")
exeConstantBidModel(validationData=devReader, trainData=None, writeResult2CSV=True)

# Execute Gaussian Random Bid Model
print("== Gaussian random bid model")
exeGaussianRandomBidModel(validationData=devReader, trainData=None, writeResult2CSV=False)

# Execute Uniform Random Bid Model
print("== Uniform random bid model")
exeUniformRandomBidModel(validationData=devReader, trainData=None, writeResult2CSV=False)

# Execute LR Bid Model
print("============ Logistic Regression bid model")
exeLogisticRegressionBidModel(validationData=devReader, trainData=trainReader, writeResult2CSV=True)


