# Applying Machine Learning Algorithms

## Experimental Protocol

Here we begin the machine learning analysis.

We first need to design the experiment so that we have reproductible and unbiaised results.
As seen in previous tutorials in this summer school, we need to ensure that we keep some data separate in order to ensure we have good, generalizable results.

This is done by randomly splitting the dataset into a **training set** and a **test set**.
The algorithms will be trained on the training set, but the test set is kept separate to check whether an algorithm performs well on new, or never seen before, data.

<img src="figures/train_test_sets.png" height="150" />

For this machine learning section, much of the code has already been released in [scikit-learn](http://scikit-learn.org/stable/).
We will use many of their functionalities for the rest of this tutorial.

The following function and code will automatically split a dataset into randomly selected training sets and test sets.

```python
from sklearn.model_selection import train_test_split

X_train, X_test, Y_train, Y_test = train_test_split(data, tags, test_size=0.25, random_state=42)
```

## Cross-validation

*quick review of cross validation*

<img src="figures/cross_validation.png" height="150" />

*already implemented in sklearn*

*create a learner*

```python
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier
param_grid = {"max_depth':[1,5,10,20,50]}
learner = GridSearchCV(DecisionTreeClassifier,param_grid)
```

## Assessing the accuracy

*review of overfitting*

<img src="figures/overfitting.png" height="150" />

*some metrics*

```python
code snippet
```

## On your own!

*Exercice/try other algorithms on your own!*
