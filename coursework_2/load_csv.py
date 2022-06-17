import pandas as pd
from sqlalchemy.exc import IntegrityError

from coursework_2.models import Questions
from coursework_2.extensions import db
from pathlib import Path

fp = Path(__file__).parent.parent.joinpath('questions.csv')
df = pd.read_csv(fp)

# helper function to fill database with questions from csv file
def load_questions():
    try:
        for index, row in df.iterrows():
            question = Questions(
                ques=row['ques'],
                option_a=row['option_a'],
                option_b=row['option_b'],
                option_c=row['option_c'],
                ans=row['ans'],
                hint=row['hint']
            )

            db.session.add(question)
        db.session.commit()
    except IntegrityError:
        # questions already exist
        db.session.rollback
        pass
