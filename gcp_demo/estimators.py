# =============================================================================
# Use this file to define your custom model/estimator.
# Below is an example of how to build a simple estimator using scikit-learn
# to predict house price
# =============================================================================
from typing import Self

import numpy as np
import numpy.typing as npt
import pandas as pd
import pandera as pa
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder


class HousePredictionModel:
    """
    Following sklearn principle to define a custom estimator.
    It should two methods: fit and predict. The predict function
    should ensure that the number of inputs should be the same as the
    number of outputs.
    """
    def __init__(self) -> None:
        self.model: LinearRegression
        self.sale_type_encoder: LabelEncoder
        self.mean_frontage: float

    def transform(self, raw_x: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the input data to the format that the model can understand.

        Args:
        ----
            raw_x (HouseFrame): Raw Data

        Returns:
        -------
            pd.DataFrame: Features for the model

        """

        # --- FIX: convert numerics that may come as strings ---
        raw_x = raw_x.copy()
    
        # Convert expected numeric columns
        for col in ["LotFrontage", "LotArea", "YearBuilt"]:
            raw_x[col] = pd.to_numeric(raw_x[col], errors="coerce")

        # Fill missing values
        raw_x["LotFrontage"] = raw_x["LotFrontage"].fillna(self.mean_frontage)
        raw_x["LotArea"] = raw_x["LotArea"].fillna(raw_x["LotArea"].median())
        raw_x["YearBuilt"] = raw_x["YearBuilt"].fillna(raw_x["YearBuilt"].mode()[0])

        # Convert SaleType to string (safe for LabelEncoder)
        raw_x["SaleType"] = raw_x["SaleType"].astype(str)

        return pd.DataFrame({
            "LotFrontage": raw_x.LotFrontage.fillna(self.mean_frontage).values,
            "LotArea": np.log1p(raw_x.LotArea).values,
            "YearBuilt": (2024 - raw_x.YearBuilt.astype(int)).astype(int).values,
            "SaleType": self.sale_type_encoder.transform(raw_x.SaleType),
        })

    def fit(self, raw_x: pd.DataFrame, raw_y: npt.NDArray[np.float64]) -> Self:
        """
        Trains the model.

        Args:
        ----
            raw_x (HouseFrame): Raw Input data
            raw_y (npt.NDArray[np.float64]): House prices

        Returns:
        -------
            Self: Returns the same instance of the model

        """
        # Convert before fitting as well
        raw_x = raw_x.copy()
        raw_x["SaleType"] = raw_x["SaleType"].astype(str)

        self.sale_type_encoder = LabelEncoder().fit(raw_x.SaleType)
        self.mean_frontage = raw_x.LotFrontage.mean()
        self.model = LinearRegression()
        self.model.fit(self.transform(raw_x), raw_y)
        return self

    def predict(self, raw_x: pd.DataFrame) -> pd.DataFrame:
        """
        Run the infernece.

        Args:
        ----
            raw_x (HouseFrame): Input raw data

        Returns:
        -------
            HousePredictionData: Generated predictions with additional information

        """
        price = self.model.predict(self.transform(raw_x))
        return pd.DataFrame({"price": price, "is_valid": (price > 0), "info": None})
