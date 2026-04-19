import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import datetime

class SalesPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False

    def train(self, df: pd.DataFrame):
        if df.empty:
            return False
            
        # Group data by Date
        daily_sales = df.groupby('date').agg({'sales': 'sum'}).reset_index()
        daily_sales['date'] = pd.to_datetime(daily_sales['date'])
        
        daily_sales['Year'] = daily_sales['date'].dt.year
        daily_sales['Month'] = daily_sales['date'].dt.month
        daily_sales['Day'] = daily_sales['date'].dt.day
        daily_sales['DayOfWeek'] = daily_sales['date'].dt.dayofweek
        
        X = daily_sales[['Year', 'Month', 'Day', 'DayOfWeek']]
        y = daily_sales['sales']
        
        self.model.fit(X, y)
        self.is_trained = True
        self.last_date = daily_sales['date'].max()
        return True

    def predict(self, days: int = 30):
        if not self.is_trained:
            raise Exception("Model is not trained yet.")
            
        future_dates = [self.last_date + datetime.timedelta(days=i) for i in range(1, days + 1)]
        future_df = pd.DataFrame({'date': future_dates})
        
        future_df['Year'] = future_df['date'].dt.year
        future_df['Month'] = future_df['date'].dt.month
        future_df['Day'] = future_df['date'].dt.day
        future_df['DayOfWeek'] = future_df['date'].dt.dayofweek
        
        X_pred = future_df[['Year', 'Month', 'Day', 'DayOfWeek']]
        predictions = self.model.predict(X_pred)
        
        return [{"date": date.strftime('%Y-%m-%d'), "predicted_sales": round(pred, 2)} 
                for date, pred in zip(future_dates, predictions)]

# Singleton instance
ai_model = SalesPredictor()
