from __future__ import annotations
import streamlit as st
import pandas as pd
from google.cloud import firestore
import seaborn as sns


def format_doc_data(collection="groups", document="000") -> tuple:
    """
    Quick function to pull a firebase doc and get the required fields. Assumed
    firestore-creds.json exists in project root

    Args:
        collection (str, optional): collection name. Defaults to "groups".
        document (str, optional): document id. Defaults to "000".

    Returns:
        tuple: groupID, investor_name, trustee_name, current_state, current_trial,
        trials (array), full_doc (dict)
    """

    # Auth to Firestore using service account key

    # This is if we use the key directly
    # db = firestore.Client.from_service_account_json("firestore-creds.json")

    # This is using streamlit secrets
    import json

    key_dict = json.loads(st.secrets["textkey"])
    db = firestore.Client.from_service_account_info(key_dict)

    # Create ref to demo group doc
    doc_ref = db.collection("groups").document("000")

    # Get data
    doc = doc_ref.get()
    data = doc.to_dict()

    return (
        data["groupId"],
        data["I_name"],
        data["T_name"],
        data["currentState"],
        data["currentTrial"],
        data["trials"],
        data,
    )


def prepare_trials_df(trials: list[dict]) -> pd.DataFrame:
    """
    Formats an array of dicts into a dataframe while creating a few new normalized columns

    Args:
        trials (list): list of dicts

    Returns:
        pd.DataFrame: trials x responses dataframe
    """
    trials = pd.DataFrame(trials)
    trials.index.rename("trials")
    trials = trials.assign(
        I_expect_norm=trials["I_1ST_ORDER_EXPECTATION"] / trials["endowment"] * 100,
        I_choice_norm=trials["I_CHOICE"] / trials["endowment"] * 100,
        T_expect_norm=trials["T_2ND_ORDER_EXPECTATION"]
        / (trials["endowment"] * 4)
        * 100,
        T_choice_norm=trials["T_CHOICE"] / (trials["endowment"] * 4) * 100,
    ).rename(
        columns={
            "I_expect_norm": "Investor Expectation",
            "I_choice_norm": "Investor Behavior",
            "T_expect_norm": "Trustee Expectation",
            "T_choice_norm": "Trustee Behavior",
        }
    )
    return trials


# Setup db connection and get formatted data
(
    groupId,
    investor,
    trustee,
    current_state,
    current_trial,
    trials,
    doc,
) = format_doc_data()

# Make df
trials_df = prepare_trials_df(trials)

# Configure the web-app meta-data
st.set_page_config(
    page_title="Trust Game Demo Data Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "[Check out the source code on Github](https://github.com/cosanlab/trust-game-analysis)",
    },
)

# From here is all web-app "front-end" code

"""
# Trust Game Demo Data Analysis

This app uses [streamlit](https://streamlit.io/) to automatically connect to the
same database that powers the [demo trust game web
app](https://trust-game-demo.netlify.app/). You can checkout the source code for the app on [github](https://github.com/cosanlab/trust-game-analysis).

**It will always pull the latest data!**

## Trial Level Data

Below is a 2d table with a few example trials. Each row is a signel trial and each column is the corresponding
decision, ratinging, and/or outcome data for that trial:
"""

# Create a sidebar with the group meta-data
st.sidebar.write(f"# Group ID: {groupId}")
st.sidebar.write("---")
st.sidebar.write(f"## *Current Trial:* {current_trial}")
st.sidebar.write(f"## *Current State:* {current_state}")
st.sidebar.write(f"## *Investor:* {investor}")
st.sidebar.write(f"## *Trustee:* {trustee}")


st.dataframe(trials_df.head())

"""
## Figures

We can also quickly generate some figures comparing Investors' and Trustee's
expectations to their actual behavior:
"""

col1, col2, col3 = st.columns(3)
with col1:
    st.pyplot(sns.lmplot(trials_df, x="Investor Expectation", y="Investor Behavior"))
with col2:
    st.pyplot(sns.lmplot(trials_df, x="Trustee Expectation", y="Trustee Behavior"))
with col3:
    st.pyplot(sns.lmplot(trials_df, x="Investor Expectation", y="Trustee Expectation"))


"""
## Raw Firestore Document Data:
"""
with st.expander("Click to open"):
    st.json(doc)


# st.write(f"### Document ID: {doc.id}")
# st.write(f"Doc contents:\n {doc.to_dict()}")
