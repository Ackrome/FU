# Source code for _prepare_features from PLDataModule

    def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        if 'location' in df.columns:
            has_metro_cities = ["������", "������", "�������", "������", "��������", "�������", "������", "������������"]
            df["has_metro"] = df["location"].isin(has_metro_cities).astype(int)

        if 'underground' in df.columns and 'location' in df.columns:
            metro_dict = { "������": ["������������", "�������������"], "������": ["����������������", "��������"] }
            is_moscow = df['underground'].isin(metro_dict["������"])
            is_kazan = df['underground'].isin(metro_dict["������"])
            df.loc[df['location'].isna() & is_moscow, 'location'] = "������"
            df.loc[df['location'].isna() & is_kazan, 'location'] = "������"

        if 'location' in df.columns:
            df['location'] = df['location'].map(self.cities_index)

        df = df.drop(columns=self.columns_to_drop, errors='ignore')

        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return df
