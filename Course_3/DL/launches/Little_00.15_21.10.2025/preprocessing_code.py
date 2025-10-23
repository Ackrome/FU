# Source code for _prepare_features from PLDataModule

    def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        if 'location' in df.columns:
            has_metro_cities = ["Москва", "Казань", "Иваново", "Кашира", "Подольск", "Люберцы", "Реутов", "Долгопрудный"]
            df["has_metro"] = df["location"].isin(has_metro_cities).astype(int)

        if 'underground' in df.columns and 'location' in df.columns:
            metro_dict = { "Москва": ["Авиамоторная", "Автозаводская"], "Казань": ["Авиастроительная", "Аметьево"] }
            is_moscow = df['underground'].isin(metro_dict["Москва"])
            is_kazan = df['underground'].isin(metro_dict["Казань"])
            df.loc[df['location'].isna() & is_moscow, 'location'] = "Москва"
            df.loc[df['location'].isna() & is_kazan, 'location'] = "Казань"

        if 'location' in df.columns:
            df['location'] = df['location'].map(self.cities_index)

        df = df.drop(columns=self.columns_to_drop, errors='ignore')

        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return df
