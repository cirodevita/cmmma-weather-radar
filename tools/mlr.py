import pickle
import sys
import pandas as pd
from sklearn.feature_selection import RFE
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'usage: {sys.argv[0]} <input dataset>')
        exit(-1)

    datasetFilename = sys.argv[1]
    dataset = pd.read_csv(datasetFilename)
    # dataset = dataset.drop(dataset[dataset.rainRate > 80].index)

    """
    x = dataset.iloc[:, 2:]

    Q1 = x.quantile(0.25)
    Q3 = x.quantile(0.75)
    IQR = Q3 - Q1

    x_out = x[~((x < (Q1 - 1.5 * IQR)) | (x > (Q3 + 1.5 * IQR))).any(axis=1)]
    x = x_out.iloc[:, :-6]
    y = x_out["rainRate"]

    nof_list = np.arange(1, x.shape[1])
    high_score = 0

    nof = 0
    score_list = []
    for n in range(len(nof_list)):
        X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=0)
        model = LinearRegression()
        rfe = RFE(model, nof_list[n])
        X_train_rfe = rfe.fit_transform(X_train, y_train)
        X_test_rfe = rfe.transform(X_test)
        model.fit(X_train_rfe, y_train)
        score = model.score(X_test_rfe, y_test)
        score_list.append(score)
        if score > high_score:
            high_score = score
            nof = nof_list[n]
    print("Optimum number of features: %d" % nof)
    print("Score with %d features: %f" % (nof, high_score))

    # 2022/07/08 -> 93 70%
    # 2021/01/24 -> 109 46%
    # 2021/11/27 -> 109 73%
    # 2021/12/09 -> 110 28%
    # final_dataset -> 104 28%
    RFE_regressor = LinearRegression()
    rfe = RFE(RFE_regressor, 93)
    X_rfe = rfe.fit_transform(x, y)
    indexes = [i for i, e in enumerate(rfe.ranking_) if e == 1]
    x = x.iloc[:, indexes]

    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    RFE_regressor.fit(X_train, y_train)

    print(X_test.iloc[0, :])

    y_pred = RFE_regressor.predict(X_test.iloc[0, :])
    print(y_pred)
    # accuracy = r2_score(y_test, y_pred) * 100
    # print("Accuracy of the model is %.2f" % accuracy)

    # plt.ylabel('Predicted')
    # sns.regplot(x=y_test, y=y_pred, marker="+", scatter_kws={"color": "blue"}, line_kws={"color": "red"})
    # plt.show()
    """

    x = dataset.iloc[:, 3:-6]
    y = dataset["rainRate"]

    # for var in list(x.columns):
    #    sns.pairplot(dataset, x_vars=[var], y_vars='rainRate', size=7, aspect=0.7)
    # plt.show()

    # MODULO
    # columns = list(x.columns)
    # for idx, column in enumerate(columns):
    #    if column.startswith('U') and columns[idx+2].startswith('V'):
    #        x[column + "-" + columns[idx+2]] = ((x[column]**2 + x[columns[idx+2]]**2)**-2)
    #        x = x.drop([column, columns[idx+2]], axis=1)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=10)
    model = LinearRegression()
    model.fit(x_train, y_train)
    filename = 'multilinear_regression.sav'
    pickle.dump(model, open(filename, 'wb'))

    # y_pred = model.predict(x_test)
    # print(y_test)
    # print(y_pred)

    # accuracy = r2_score(y_test, y_pred) * 100
    # print("Accuracy of the model is %.2f" % accuracy)

    # plt.ylabel('Predicted')
    # sns.regplot(x=y_test, y=y_pred, marker="+", scatter_kws={"color": "blue"}, line_kws={"color": "red"})
    # plt.show()

    # pred_df = pd.DataFrame({'Actual Value': y_test, 'Predicted Value': y_pred, 'Difference': y_test - y_pred})
    # print(pred_df)
