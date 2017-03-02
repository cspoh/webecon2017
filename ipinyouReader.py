import pandas as pd

class ipinyouReader():
    def __init__(self, filename, header=0):
        self.__dataframe = pd.read_csv(filename, delimiter=',', low_memory=False, header=header)

    def getDataFrame(self):
        return self.__dataframe

    def getTrainData(self):
        """ Return the all data in numpy array format. """
        return self.__dataframe.as_matrix()

    def getTestData(self):
        """ Return data in test format. i.e. without click, bidprice and payprice """
        return self.__dataframe.as_matrix(['weekday',   #0
                                           'hour',      #1
                                           'bidid',     #2
                                           'logtype',   #3
                                           'userid',    #4
                                           'useragent', #5
                                           'IP',        #6
                                           'region',    #7
                                           'city',      #8
                                           'adexchange',#9
                                           'domain',    #10
                                           'url',       #11
                                           'urlid',     #12
                                           'slotid',    #13
                                           'slotwidth', #14
                                           'slotheight',#15
                                           'slotvisibility',#16
                                           'slotformat',#17
                                           'slotprice', #18
                                           'creative',  #19
                                           'keypage',   #20
                                           'advertiser',#21
                                           'usertag'])  #22


    def getResult(self):
        """ Return data in result format for evaluation. i.e. bidid, bidprice """
        return self.__dataframe.as_matrix()



class ipinyouReaderWithEncoding():
    def getTrainValidationTestDD(self, trainFilename, validationFilename, testFilename, header=0):
        """
        1. Reads train, validation and test file
        2. Represent non-numeric column with a unique int for each category/unique string
        3. Returns trainDF, validationDF, testDF, lookupDict

        :param trainFilename: Training Filename
        :param validationFilename: Validation Filename
        :param testFilename:  Test Filename
        :param header: csv has header? 0 or None
        :return: trainDF, validationDF, testDF, lookupDict
        """
        print("Reading: ", trainFilename)
        traindf = pd.read_csv(trainFilename, delimiter=',', low_memory=False, header=header)

        print("Reading: ", validationFilename)
        validationdf = pd.read_csv(validationFilename, delimiter=',', low_memory=False, header=header)

        print("Reading: ", testFilename)
        testdf = pd.read_csv(testFilename, delimiter=',', low_memory=False, header=header)

        # Concat the data vertically
        combined_set = pd.concat([traindf, validationdf, testdf], axis=0)
        # print(combined_set.info())
        dict = {}
        # Loop through all columns in the dataframe
        for feature in combined_set.columns:

            # Only apply for columns with categorical strings
            if combined_set[feature].dtype == 'object':

                original = combined_set[feature]
                # Replace strings with an integer
                combined_set[feature] = pd.Categorical(combined_set[feature]).codes

                replaced = combined_set[feature]

                if feature == 'bidid':
                    colDict = {}
                    for i in range(len(original)):
                        # print("ttt: ", original.iloc[i], "    ", replaced.iloc[i])
                        if replaced.iloc[i] not in colDict:
                            colDict[replaced.iloc[i]] = original.iloc[i]
                    dict[feature] = colDict

        train = combined_set[:traindf.shape[0]]
        validation = combined_set[traindf.shape[0]:(traindf.shape[0]+validationdf.shape[0])]
        test = combined_set[(traindf.shape[0]+validationdf.shape[0]):]

        print(train.shape[0])
        print(validation.shape[0])
        print(test.shape[0])

        return train, validation, test, dict

        # print("dict", dict)


# reader_encoded = ipinyouReaderWithEncoding()
# reader_encoded.getTrainValidationTestDD("../dataset/debug.csv", "../dataset/debug.csv", "../dataset/test.csv")


# reader = ipinyouReader("debug.csv")
# print ("A")
# debug = reader.getDataFrame()
# print ("B")
# test = reader.getMatrix()
# print("C")
#
# print(test.shape)
# print (test[0])
# print(debug.iloc[0])
# print(debug.iloc[0]['bidid'])

# for index, row in debug.iterrows():
#     # print(index)
#     print("row: ", row['bidid'])
