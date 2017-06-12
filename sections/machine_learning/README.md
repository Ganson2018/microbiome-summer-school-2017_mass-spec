# Applying Machine Learning Algorithms

## Experimental Protocol

*explain train vs test*

*figure*

```python
from sklearn.model_selection import train_test_split
code snippet
```

## Cross-validation

*quick review of cross validation*

*already implemented in sklearn*

*create a learner*

```python
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier
param_grid = {"max_depth':[1,5,10,20,50]}
learner = GridSearchCV(DecisionTreeClassifier,param_grid)
snippet
```

## Assessing the accuracy

*review of overfitting*

*fun overfit figure*

*some metrics*

```python
code snippet
```

## On your own!

*Exercice/try other algorithms on your own!*
