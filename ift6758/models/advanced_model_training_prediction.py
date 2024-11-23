#importing libraries for milestone 1
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.axes as ax
import os
from typing import List, Tuple, Dict, Union, Optional, Any
Number = Union[int, float]


from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, PowerTransformer, QuantileTransformer, FunctionTransformer
from sklearn.feature_selection import SelectKBest, SelectPercentile, RFE
from sklearn.decomposition import PCA
from sklearn.calibration import calibration_curve
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import StratifiedKFold as SKFold


def set_in_dict(d : dict, path : str, value : Any) -> Any:
    """ navigate in a dictionary using a path

    Args:
        d (dict): the dictionary to navigate
        path (str): the path to navigate
        value (Any): the value to set at the end of the path

    Returns:
        Any: the value at the end of the path
    """
    path = path.split('.')
    for key in path[:-1]:
        if key.isdigit():
            key = int(key)
        if key not in d:
            d[key] = {}
        d = d[key]
    final_key = path[-1]
    if final_key.isdigit():
        final_key = int(final_key)
    d[final_key] = value


def roc_auc(y_true : np.ndarray, y_pred : np.ndarray, plot : bool = True) -> Tuple[np.ndarray, np.ndarray]:
    """ plot the ROC curve and calculate the AUC

    Args:
        y_true (np.ndarray): the true labels
        y_pred (np.ndarray): the predicted probabilities

    Returns:
        Tuple[np.ndarray, np.ndarray]: the false positive rate and true positive rate
    """
    fpr, tpr, _ = roc_curve(y_true, y_pred)
    roc_auc = auc(fpr, tpr)
    if plot:
        plt.figure()
        plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.0])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic')
        plt.legend(loc="lower right")
        plt.show()
    
    return fpr, tpr

def goal_rate_vs_percentile(y_true : np.ndarray, y_pred : np.ndarray, plot : bool = True) -> Tuple[np.ndarray, np.ndarray]:
    """ plot the goal rate vs the probability percentile

    Args:
        y_true (np.ndarray): the true labels
        y_pred (np.ndarray): the predicted probabilities
        plot (bool, optional): if you want to plot the results. Defaults to True.

    Returns:
        Tuple[np.ndarray, np.ndarray]: the probability percentiles and the goal rates
    """
    percentiles = np.percentile(y_pred, np.arange(0, 101, 1))
    goal_rates = [np.mean(y_true[y_pred >= p]) for p in percentiles]
    
    if plot:
        plt.figure()
        plt.plot(percentiles, goal_rates, marker='o')
        plt.xlabel('Probability Percentile')
        plt.ylabel('Goal Rate')
        plt.title('Goal Rate vs Probability Percentile')
        plt.show()
    
    return percentiles, goal_rates

def cumulative_goals_vs_percentile(y_true : np.ndarray, y_pred : np.ndarray, plot : bool = True) -> Tuple[np.ndarray, np.ndarray]:
    """ plot the cumulative proportion of goals vs the probability percentile

    Args:
        y_true (np.ndarray): the true labels
        y_pred (np.ndarray): the predicted probabilities
        plot (bool, optional): if you want to plot the results. Defaults to True.

    Returns:
        Tuple[np.ndarray, np.ndarray]: the probability percentiles and the cumulative proportion of goals
    """
    sorted_indices = np.argsort(y_pred)
    sorted_y_true = y_true[sorted_indices]
    cumulative_goals = np.cumsum(sorted_y_true) / np.sum(y_true)
    percentiles = np.arange(1, len(y_true) + 1) / len(y_true) * 100
    
    if plot:
        plt.figure()
        plt.plot(percentiles, cumulative_goals, marker='o')
        plt.xlabel('Probability Percentile')
        plt.ylabel('Cumulative Proportion of Goals')
        plt.title('Cumulative Proportion of Goals vs Probability Percentile')
        plt.show()

    return percentiles, cumulative_goals

def reliability_curve(y_true : np.ndarray, y_pred : np.ndarray, plot : bool = True) -> Tuple[np.ndarray, np.ndarray]:
    """ plot the reliability curve

    Args:
        y_true (np.ndarray): the true labels
        y_pred (np.ndarray): the predicted probabilities
        plot (bool, optional): if you want to plot the results. Defaults to True.

    Returns:
        Tuple[np.ndarray, np.ndarray]: the predicted probabilities and the true probabilities
    """
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=10)
    
    if plot:
        plt.figure()
        plt.plot(prob_pred, prob_true, marker='o', label='Model')
        plt.plot([0, 1], [0, 1], linestyle='--', label='Perfectly Calibrated')
        plt.xlabel('Predicted Probability')
        plt.ylabel('True Probability')
        plt.title('Reliability Curve')
        plt.legend()
        plt.show()
    
    return prob_pred, prob_true


class Transformation:
    
    
    def __init__(self, build_instructions : Dict[str, Any], retrain : bool = False):
        """ initialize the transformation

        Args:
            build_instructions (Dict[str, Any]): the instructions to build the transformation
            retrain (bool, optional): whethere or not we want to retrain the transformation after each run or keep the previously trained transformation. Defaults to False.
        
        Example of build_instructions:
        {
            "transformation": StandardScaler,
            "params": {
                "required": [],
                "optional": {}
            }
        }
        """
        transfor = build_instructions['transformation']
        params : dict = build_instructions.get('params', {})
        req_param = params.get('required', [])
        opt_param = params.get('optional', {})
        transformer = transfor(*req_param, **opt_param)
        
        self.transformation = transformer 
        self.trained = False
        self.retrain = retrain
        self.pre_trained_x = None
        self.trained_x = None
    
    def fit(self, x : np.ndarray, force_fit : bool = False):
        """ fit the transformation

        Args:
            x (np.ndarray): the data to fit the transformation on
            force_fit (bool, optional): if you want to force the fit. Defaults to False.
        """
        if not self.trained or force_fit:
            try:
                self.transformation.fit(x)
            except:
                pass
            self.trained = True
            self.trained_x = None
            self.pre_trained_x = None
        if self.retrain:
            self.trained = False

    def transform(self, x : np.ndarray) -> np.ndarray:
        """ transform the data

        Args:
            x (np.ndarray): the data to transform

        Returns:
            np.ndarray: the transformed data
        """
        if self.trained_x is not None and np.array_equal(x, self.pre_trained_x):
            return self.trained_x
        
        self.pre_trained_x = x
        new_x = self.transformation.transform(x)
        self.trained_x = new_x
        return new_x

class TransformationPipeline:
        
    def __init__(self, steps : List[Dict[str, Any]], steps_to_iterate : Optional[str]= None):
        """ initialize the transformation pipeline

        Args:
            steps (List[Dict[str, Any]]): the steps of the pipeline
            steps_to_iterate (Optional[str], optional): the step containing the hyperparameter to tune. Defaults to None.

        Example of steps:
        [
            {
                "transformation": StandardScaler,
                "params": {
                    "required": [],
                    "optional": {}
                }
            },
            {
                "transformation": PCA,
                "params": {
                    "required": [],
                    "optional": {'n_components': 2}
                }
            }
        ]
        """
        self.cross_val_step = steps_to_iterate
        self.steps : Dict[int, Transformation] = {}
        retrain = False
        for i, step in enumerate(steps):
            if steps_to_iterate is not None and steps_to_iterate == i:
                retrain = True
            trans = Transformation(step, retrain)
            self.steps[i] = trans
            
    def fit(self, x : np.ndarray, force_fit : bool = False):
        """ fit the transformation pipeline

        Args:
            x (np.ndarray): the data to fit the pipeline on
            force_fit (bool, optional): if you want to force the fit. Defaults to False.
        """
        X = x.copy()
        for i in range(len(self.steps)):
            step = self.steps[i]
            step.fit(X, force_fit)
            X = step.transform(X)
        
    def transform(self, x : np.ndarray) -> np.ndarray:
        """ transform the data

        Args:
            x (np.ndarray): the data to transform

        Returns:
            np.ndarray: the transformed data
        """
        X = x.copy()
        for step in self.steps.values():
            X = step.transform(X)
        return X
    
    def update_step(self, new_step : Dict[str, Any]):
        """ update a step in the pipeline

        Args:
            new_step (Dict[str, Any]): the new step to replace the old one
        """
        self.steps[self.cross_val_step] = Transformation(new_step, True)
        

class Classifier:
    
    
    def __init__(self, build_instructions : Dict[str, Any]):
        """ initialize the classifier

        Args:
            build_instructions (Dict[str, Any]): the instructions to build the classifier
            
        Example of build_instructions:
        {
            "model": XGB,
            "params": {
                "required": [],
                "optional": {
                    "n_estimators": 100,
                    "learning_rate": 0.1,
                    "max_depth": 6,
                    "min_child_weight": 1,
                    "subsample": 0.8,
                    "colsample_bytree": 0.8,
                    "gamma": 0,
                    "reg_alpha": 0,
                    "reg_lambda": 1,
                    "scale_pos_weight": 1,
                    "objective": "binary:logistic",
                    "eval_metric": "logloss",
                    "use_label_encoder": False
                }
            }
        }
        """
        model = build_instructions['model']
        params : dict = build_instructions.get('params', {})
        req_param = params.get('required', [])
        opt_param = params.get('optional', {})
        self.model = model(*req_param, **opt_param)
    
    def fit(self, X: np.ndarray, y: np.ndarray, force_fit : bool = False):
        """ fit the model

        Args:
            X (np.ndarray): the data to fit the model on
            y (np.ndarray): the labels
            force_fit (bool, optional): whethere or not you want to retrain the model even if it has already been trained. Defaults to False.
        """
        self.model.fit(X, y)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """ predict the labels

        Args:
            X (np.ndarray): the data to predict

        Returns:
            np.ndarray: the predicted labels
        """
        return self.model.predict(X)
    
class CrossValidation:
    
    cross_val_split : List[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = None

    @staticmethod
    def generate_new_split(X : np.ndarray, y : np.ndarray, n_splits : int = 5):
        """ generate a new split

        Args:
            X (np.ndarray): the features
            y (np.ndarray): the labels
            n_splits (int, optional): the number of splits. Defaults to 5.
        """
        CrossValidation.cross_val_split = []
        skf = SKFold(n_splits=n_splits)
        for train_index, val_index in skf.split(X, y):
            X_train, X_val = X[train_index], X[val_index]
            y_train, y_val = y[train_index], y[val_index]
            CrossValidation.cross_val_split.append((X_train, X_val, y_train, y_val))
    
    
    def __init__(self, build_instructions : Dict[str, Any]):
        """ initialize the cross validation

        Args:
            build_instructions (Dict[str, Any]): the instructions to build the cross validation
            
        Example of build_instructions:
        
        {
            "model": {
                "model": XGB,
                "params": {
                    "required": [],
                    "optional": {
                        "n_estimators": 100,
                        "learning_rate": 0.1,
                        "max_depth": 6,
                        "min_child_weight": 1,
                        "subsample": 0.8,
                        "colsample_bytree": 0.8,
                        "gamma": 0,
                        "reg_alpha": 0,
                        "reg_lambda": 1,
                        "scale_pos_weight": 1,
                        "objective": "binary:logistic",
                        "eval_metric": "logloss",
                        "use_label_encoder": False
                    }
                },
            },
            "transformation": [
                {
                    "transformation": StandardScaler,
                    "params": {
                        "required": [],
                        "optional": {}
                    }
                },
                {
                    "transformation": PCA,
                    "params": {
                        "required": [],
                        "optional": {'n_components': 2}
                    }
                }
            ],
            "hyperparameter": {
                "path": "model.params.optional.n_estimators",
                "values": [10, 50, 100, 200, 500]
            }
        }
        """
        model = build_instructions['model']
        transformation = build_instructions['transformation']
        hyperparameter = build_instructions['hyperparameter']
        hyperparameter_path : str = hyperparameter['path']
        self.model = Classifier(model)
        step = hyperparameter_path.split('.')[1]
        if hyperparameter_path is not None and 'transformation' in  hyperparameter_path:
            self.transformation = TransformationPipeline(transformation, int(step))
        else:
            self.transformation = TransformationPipeline(transformation)
    
    def fit(self, X_train: np.ndarray, y_train: np.ndarray, force_fit : bool = False):
        """ fit the cross validation

        Args:
            X_train (np.ndarray): the features
            y_train (np.ndarray): the labels
            force_fit (bool, optional): whethere or not everything should be retrained. Defaults to False.
        """
        self.transformation.fit(X_train, force_fit)
        X_trans = self.transformation.transform(X_train)
        self.model.fit(X_trans, y_train, force_fit)
        
    def predict(self, X_val: np.ndarray) -> np.ndarray:
        """ predict the labels

        Args:
            X_val (np.ndarray): the features

        Returns:
            np.ndarray: the predicted labels
        """
        X_trans = self.transformation.transform(X_val)
        return self.model.predict(X_trans)
    
    @staticmethod
    def cross_validate(build_instructions : Dict[str, Any]):
        """ cross validate the model

        Args:
            build_instructions (Dict[str, Any]): the instructions to build the model
        """
        hyperparameter_inst = build_instructions['hyperparameter']
        path = hyperparameter_inst['path']
        values = hyperparameter_inst['values']
        roc_auc_res, gr_vs_p_res, cg_vs_p_res, rc_res = "roc_auc", "goal_rate_vs_percentile", "cumulative_goals_vs_percentile", "reliability_curve"
        list_metrics = ((roc_auc_res, roc_auc), (gr_vs_p_res, goal_rate_vs_percentile), (cg_vs_p_res, cumulative_goals_vs_percentile), (rc_res, reliability_curve))
        total_results = {}
        for value in values:
            metrics = {
                roc_auc_res: [],
                gr_vs_p_res: [],
                cg_vs_p_res: [],
                rc_res: []
            }
            set_in_dict(build_instructions, path, value)
            cv = CrossValidation(build_instructions)
            y_preds = np.array([])
            y_trues = np.array([])
            for X_train, X_val, y_train, y_val in CrossValidation.cross_val_split:
                cv.fit(X_train, y_train, force_fit=True)
                y_pred = cv.predict(X_val)
                y_preds = np.concatenate((y_preds, y_pred))
                y_trues = np.concatenate((y_trues, y_val))
            for metric, func in list_metrics:
                metrics[metric].append(func(y_trues, y_preds, plot=False))
            total_results[value] = {"metrics" : metrics, "predictions" : y_trues, "true_labels" : y_preds}
            
        return total_results






if __name__ == '__main__':
    df = pd.read_csv('../../notebooks/season2016.csv')
    skf = SKFold(n_splits=5)
    y = df['goal'].values
    X = df.drop(columns=['goal']).values
    for train_index, test_index in skf.split(X, y):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        