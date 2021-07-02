from fbprophet import Prophet


def forecast(data, period=25):
    data = data[['Date', 'Close']]
    data.columns = ['ds', 'y']
    mod = Prophet()
    mod.fit(data)
    future = mod.make_future_dataframe(periods=period)
    forecast = mod.predict(future)
    # result = dict(
    #     '预期收益率'=forecast[['yhat'], -1]/data[['Close'], -1]-1,
    #     '最大损失率'=forecast[['yhat_lower'], -1]/data[['Close'], -1]-1,
    # )
    result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    return result
