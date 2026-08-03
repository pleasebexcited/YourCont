"""
application.py: Starts the YourCont website

YourCont starts from this file on my PC,
and Elastic Beanstalk can use the same entry point later in the cloud.
create_app in app/__init__.py builds the website,
then this file either hands that object to a production server or runs Flask's small local server while I check screens and auth.
One start file keeps PC and cloud startup aligned for the assessment.
"""

from app import create_app

# application is the Flask object the rest of the stack talks to.
# Local runs and Elastic Beanstalk both expect this name, so I create it once here.

application = create_app()

if __name__ == "__main__":

    # debug=True reloads the app when I edit code, which speeds up UI work on my PC.
    # In AWS a production server imports "application" instead of calling run().

    application.run(debug=True)
