from prefect import task, flow
from datetime import timedelta
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


@task(                                      #Over the task we can define few important parameters definida en clase 17
    name="Load Iris Dataset",
    tags=["data_loading"],
    description="Load Iris dataset from sklearn",
)
def get_data_from_sklearn() -> dict:                                                        #Now we define our task
    """This function loads the iris dataset from sklearn and returns it as a dictionary."""
    data = load_iris()
    return {"data": data.data, "target": data.target}


@task(                                  #definida en clase 18
    name="Split Data",
    tags=["data_processing"],
    description="Split dataset into train and test sets",
)
def split_data(dataset: dict) -> tuple:
    """This function splits the dataset into train and test sets."""
    X_train, X_test, y_train, y_test = train_test_split(
        dataset["data"], dataset["target"], test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test


@task(                                          #definida en clase 18
    name="Train Model",
    tags=["model_training"],
    description="Train RandomForestClassifier model",
)
def train_model(X_train: list, X_test: list, y_train: list, y_test: list) -> str:
    """This function trains a RandomForestClassifier model and returns the accuracy."""
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    print("el accuracy es de: ", accuracy)
    return f"Model trained with accuracy: {accuracy:.2f}"


@flow(retries=3, retry_delay_seconds=5, log_prints=True)            #We have to define a flow, retires= how many times we run the task
def iris_classification():                                          #Try every 5 seg, and print the logs to know if its working
    """This function orchestrates the whole flow"""
    dataset = get_data_from_sklearn()
    X_train, X_test, y_train, y_test = split_data(dataset)
    train_model(X_train, X_test, y_train, y_test)


iris_classification()           #execute the flow.
