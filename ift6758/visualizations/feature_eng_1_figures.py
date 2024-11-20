from sklearn.metrics import roc_curve, roc_auc_score
import numpy as np
import pandas as pd
from sklearn.calibration import CalibrationDisplay
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

def plot_roc_curve(y_val, y_pred):
    # Calculate the ROC curve
    fpr, tpr, thresholds = roc_curve(y_val, y_pred[:, 1])

    # Calculate the AUC (Area Under the Curve)
    roc_auc = roc_auc_score(y_val, y_pred[:, 1])


    # Plot the ROC curve
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='blue', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend(loc="lower right")
    plt.show()



def plot_goal_rate_by_percentile(y_pred, y_val):
    # Calculate the percentiles of the predicted probabilities
    percentiles = np.percentile(y_pred[:, 1], np.arange(0, 101, 1))


    # Create a DataFrame with the actual values and predicted probabilities
    df_percentiles = pd.DataFrame({'Actual': y_val.flatten(), 'Predicted_Prob': y_pred[:, 1]})

    
    # Remove duplicates from percentiles
    percentiles = np.unique(percentiles)

    # Assign each predicted probability to a percentile group
    # df_percentiles['Percentile'] = pd.cut(df_percentiles['Predicted_Prob'], bins=percentiles, labels=np.arange(1, 101, 1), include_lowest=True, duplicates='drop')
    df_percentiles['Percentile'] = pd.cut(df_percentiles['Predicted_Prob'], bins=percentiles, labels=np.arange(1, len(percentiles)), include_lowest=True)


    # Calculate the goal rate for each percentile group
    goal_rate_by_percentile = df_percentiles.groupby('Percentile')['Actual'].apply(lambda x: x.sum() / len(x))
    # goal_rate_by_percentile = df_percentiles.groupby('Percentile')['Actual'].mean()

    goal_rate_by_percentile
    goal_rate_by_percentile = df_percentiles.groupby('Percentile')['Actual'].mean()

    # Plot the goal rate as a function of the shot probability model percentile
    plt.figure(figsize=(10, 6))
    goal_rate_by_percentile.plot(kind='line')
    plt.xlabel('Shot Probability Model Percentile')
    plt.ylabel('Goal Rate')
    plt.title('Goal Rate as a Function of Shot Probability Model Percentile')
    plt.ylim(0, 1)
    plt.grid(True)
    plt.show()
    return df_percentiles


def plot_cumulative_proportion_of_goals(df_percentiles):
    # Calculate the cumulative sum of goals for each percentile
    cumulative_goals = df_percentiles.groupby('Percentile')['Actual'].sum().cumsum()

    # Calculate the cumulative proportion of goals
    cumulative_proportion_goals = cumulative_goals / cumulative_goals.iloc[-1]

    # Plot the cumulative proportion of goals as a function of the shot probability model percentile
    plt.figure(figsize=(10, 6))
    cumulative_proportion_goals.plot(kind='line')
    plt.gca().invert_xaxis()
    plt.xlabel('Shot Probability Model Percentile')
    plt.ylabel('Cumulative Proportion of Goals')
    plt.title('Question c')
    plt.grid(True)
    plt.show()


def plot_calibration_curve(y_val, y_pred):
    # Create the reliability diagram (calibration curve)
    CalibrationDisplay.from_predictions(y_val, y_pred[:, 1], n_bins=10)

    # Add labels and title
    plt.xlabel('Mean Predicted Probability')
    plt.ylabel('Fraction of Positives')
    plt.title('Calibration Curve')
    plt.show()


def plot_confusion_matrix(y_true, y_pred):
    # Calculate the confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    # Plot the confusion matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Not Goal', 'Goal'], yticklabels=['Not Goal', 'Goal'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.show()


def produce_figures(y_pred_proba, y_pred_discrete, y_true):

    # 0. Confusion matrix
    plot_confusion_matrix(y_true, y_pred_discrete)

    # a. ROC curve
    plot_roc_curve(y_true, y_pred_proba)

    # b. Goal Rate as a Function of Shot Probability Model Percentile
    df_percentiles = plot_goal_rate_by_percentile(y_pred_proba, y_true)

    # c. cumulative proportion of goals (not shots) as a function of the shot probability model percentile.
    plot_cumulative_proportion_of_goals(df_percentiles)

    # d. Calibration curve
    plot_calibration_curve(y_true, y_pred_proba)