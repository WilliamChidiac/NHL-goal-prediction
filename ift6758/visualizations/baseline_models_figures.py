from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix
import numpy as np
import pandas as pd
from sklearn.calibration import CalibrationDisplay
import seaborn as sns
import matplotlib.pyplot as plt

def plot_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Not Goal', 'Goal'], yticklabels=['Not Goal', 'Goal'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.show()


def plot_roc_curve(ax, y_val, y_pred):
    fpr, tpr, thresholds = roc_curve(y_val, y_pred[:, 1])

    roc_auc = roc_auc_score(y_val, y_pred[:, 1])

    ax.plot(fpr, tpr, color='blue', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    ax.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('Receiver Operating Characteristic (ROC) Curve')
    ax.legend(loc="lower right")

def plot_goal_rate_by_percentile(ax, y_pred, y_val):
    # percentiles of the predicted probabilities
    percentiles = np.percentile(y_pred[:, 1], np.arange(0, 101, 1))


    # df with the actual values and predicted probabilities
    df_percentiles = pd.DataFrame({'Actual': y_val.flatten(), 'Predicted_Prob': y_pred[:, 1]})

    percentiles = np.unique(percentiles)

    # assign each predicted probability to a percentile group
    df_percentiles['Percentile'] = pd.cut(df_percentiles['Predicted_Prob'], bins=percentiles, labels=np.arange(1, len(percentiles)), include_lowest=True)


    # goal rate for each percentile group
    goal_rate_by_percentile = df_percentiles.groupby('Percentile')['Actual'].apply(lambda x: x.sum() / len(x))


    # goal rate by percentile
    ax.plot(goal_rate_by_percentile)
    ax.set_xlabel('Percentile')
    ax.set_ylabel('Goal Rate')
    ax.set_ylim(0, 1)
    ax.set_title('Goal Rate by Percentile')

    return df_percentiles

def plot_cumulative_proportion_of_goals(ax, df_percentiles):
    # cumulative sum of goals for each percentile
    cumulative_goals = df_percentiles.groupby('Percentile')['Actual'].sum().cumsum()

    # cumulative proportion of goals
    cumulative_proportion_goals = cumulative_goals / cumulative_goals.iloc[-1]

    ax.plot(cumulative_proportion_goals)
    ax.set_xlabel('Shot Probability Model Percentile')
    ax.set_ylabel('Cumulative Proportion of Goals')
    ax.set_title('Cumulative Proportion of Goals by Percentile')

def plot_calibration_curve(ax, y_val, y_pred):
    CalibrationDisplay.from_predictions(y_val, y_pred[:, 1], ax=ax, n_bins=10)
    ax.set_title('Calibration Curve')


def plot_figures(y_pred_proba, y_true, model_name):
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))

    # a. ROC curve
    plot_roc_curve(axs[0, 0], y_true, y_pred_proba)

    # b. goal Rate as a Function of Shot Probability Model Percentile
    df_percentiles = plot_goal_rate_by_percentile(axs[1, 0], y_pred_proba, y_true)

    # c. cumulative proportion of goals (not shots) as a function of the shot probability model percentile.
    plot_cumulative_proportion_of_goals(axs[0, 1], df_percentiles)

    # d. calibration curve
    plot_calibration_curve(axs[1, 1], y_true, y_pred_proba)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.suptitle(f"Model evaluation curves for {model_name}", fontsize=16)
    
    plt.show()
