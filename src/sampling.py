from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

def apply_smote(X_train, y_train, random_state=42):
    """Applies SMOTE to oversample the minority fraud class."""
    smote = SMOTE(random_state=random_state)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
    return X_resampled, y_resampled

def apply_undersample(X_train, y_train, random_state=42):
    """Applies Random Undersampling to reduce the majority non-fraud class."""
    rus = RandomUnderSampler(random_state=random_state)
    X_resampled, y_resampled = rus.fit_resample(X_train, y_train)
    return X_resampled, y_resampled