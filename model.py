import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
df=pd.read_csv(
    "data/merged_features.csv",
    index_col=0,
    parse_dates=True
)
print(df.head())
print(df.columns)
features= [
    "return",
    "news_count_lag1",
    "sentiment_sum_lag1",
    "sentiment_mean_lag1"
]
X= df[features]
y=df["target_vol"]
split = int(len(df) * 0.8)

X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]
model=RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
model.fit(X_train,y_train)
print("\nModel training completed")
predictions=model.predict(X_test)
print("\nFirst10 predictions:")
print (predictions[:10])
accuracy=accuracy_score(
    y_test,
    predictions
 
)
print("\nModel accuracy:")
print(accuracy)
importance=pd.Series(
    model.feature_importances_,
    index=features
)
importance=importance.sort_values(
    ascending=False
)
print("\nFeature Importance:")
print(importance)