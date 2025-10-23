# Source code for data_preprocessing from PLDataModule

    def data_preprocessing(self, X_train, X_val, X_test):
        # --- 1. ����������� ����� ������� ---
        high_card_cols = ['author', 'district', 'street', 'underground']

        # ������� ��� �������������� (object) �������, �������� ��, ��� ��� � high_card_cols
        all_object_cols = X_train.select_dtypes(include=['object']).columns.tolist()
        low_card_cols = [col for col in all_object_cols if col not in high_card_cols]

        numerical_cols = X_train.select_dtypes(include=np.number).columns.tolist()

        # --- 2. ��������� ������-������������ ��������� (Top-K) ---
        top_k_values = {}
        for col in high_card_cols:
            if col in X_train.columns:
                top_vals = X_train[col].value_counts().nlargest(self.top_k).index.tolist()
                top_k_values[col] = top_vals
                for val in top_vals:
                    X_train[f'{col}_{val}'] = (X_train[col] == val).astype(int)
                    X_val[f'{col}_{val}'] = (X_val[col] == val).astype(int)
                    X_test[f'{col}_{val}'] = (X_test[col] == val).astype(int)

        X_train = X_train.drop(columns=[col for col in high_card_cols if col in X_train.columns])
        X_val = X_val.drop(columns=[col for col in high_card_cols if col in X_val.columns])
        X_test = X_test.drop(columns=[col for col in high_card_cols if col in X_test.columns])
        self.preprocessing_artifacts['top_k_values'] = top_k_values

        # --- 3. ��������� �����-������������ ��������� (One-Hot) ---
        if low_card_cols:
            X_train = pd.get_dummies(X_train, columns=low_card_cols, dummy_na=True, dtype=int)
            X_val = pd.get_dummies(X_val, columns=low_card_cols, dummy_na=True, dtype=int)
            X_test = pd.get_dummies(X_test, columns=low_card_cols, dummy_na=True, dtype=int)

        # --- 4. �������� ������������ ������� ---
        train_cols = X_train.columns
        X_val = X_val.reindex(columns=train_cols, fill_value=0)
        X_test = X_test.reindex(columns=train_cols, fill_value=0)
        self.preprocessing_artifacts['final_columns'] = train_cols.tolist()

        # --- 5. ��������� �������� ��������� (Impute + Scale) ---
        imputer = SimpleImputer(strategy='median')
        scaler = StandardScaler()

        if numerical_cols:
            X_train[numerical_cols] = imputer.fit_transform(X_train[numerical_cols])
            X_train[numerical_cols] = scaler.fit_transform(X_train[numerical_cols])

            X_val[numerical_cols] = imputer.transform(X_val[numerical_cols])
            X_val[numerical_cols] = scaler.transform(X_val[numerical_cols])

            X_test[numerical_cols] = imputer.transform(X_test[numerical_cols])
            X_test[numerical_cols] = scaler.transform(X_test[numerical_cols])

        self.preprocessing_artifacts['numerical_imputer'] = imputer
        self.preprocessing_artifacts['scaler'] = scaler
        self.preprocessing_artifacts['numerical_columns'] = numerical_cols

        print("Preprocessing: �����")
        # ��������, ��� ���������� ������ float
        return X_train.astype(float).values, X_val.astype(float).values, X_test.astype(float).values


# Source code for save_preprocessing from PLDataModule

    def save_preprocessing(self, directory_path: str):
        preprocess_dir = os.path.join(directory_path, "preprocessing")
        os.makedirs(preprocess_dir, exist_ok=True)

        if self.preprocessing_artifacts:
            artifacts_path = os.path.join(preprocess_dir, "preprocessing_artifacts.joblib")
            joblib.dump(self.preprocessing_artifacts, artifacts_path)
            print(f"������� ������������� ��������� �: {artifacts_path}")
            return preprocess_dir
        return None
