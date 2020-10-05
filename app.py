from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import os

############################################################
# SETUP
############################################################

# create flask app
app = Flask(__name__)

# configure mongodb
host = os.environ.get(
    'MONGODB_URI', "mongodb://localhost:27017/plantsDatabase"
) + "?retryWrites=false"

app.config["MONGO_URI"] = host

mongo = PyMongo(app)

############################################################
# ERROR
############################################################


@app.errorhandler(404)
def page_not_found(e):
    # display a 404 response page
    return render_template('404.html'), 404


############################################################
# ROUTES
############################################################


@app.route('/')
def plants_list():
    """Display the plants list page."""
    # find all plants in the db
    plants_data = mongo.db.plants.find()

    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)


@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')


@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':

        name = request.form.get("plant_name")
        variety = request.form.get("variety")
        photo_url = request.form.get("photo")
        date_planted = request.form.get("date_planted")

        new_plant = {
            'name': name,
            'variety': variety,
            'photo_url': photo_url,
            'date_planted': date_planted
        }

        # insert the plant into the db
        plant = mongo.db.plants.insert_one(new_plant)
        # get the id of the new plant
        plant_id = plant.inserted_id

        # pass the id of the new plant into the redirect url
        return redirect(url_for('detail', plant_id=plant_id))

    else:
        return render_template('create.html')


@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""

    # find the specified plant_id in the database
    plant_to_show = mongo.db.plants.find_one_or_404(
        {"_id": ObjectId(plant_id)})

    # find the harvests for the specified plant_id
    harvests = mongo.db.harvests.find({"plant_id": plant_id})

    context = {
        'plant': plant_to_show,
        'harvests': harvests
    }

    return render_template('detail.html', **context)


@ app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """

    quantity = request.form.get('harvested_amount')
    date = request.form.get('date_planted')

    new_harvest = {
        'quantity': quantity,  # e.g. '3 tomatoes'
        'date': date,
        'plant_id': plant_id
    }

    mongo.db.harvests.insert_one(new_harvest)

    return redirect(url_for('detail', plant_id=plant_id))


@ app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':

        # update plant with given id
        name = request.form.get("plant_name")
        variety = request.form.get("variety")
        photo_url = request.form.get("photo")
        date_planted = request.form.get("date_planted")

        mongo.db.plants.update_one({
            '_id': ObjectId(plant_id)
        },
            {
            '$set': {
                'name': name,
                'variety': variety,
                'photo_url': photo_url,
                'date_planted': date_planted
            }
        })

        return redirect(url_for('detail', plant_id=plant_id))
    else:

        # get the plant to be updated
        plant_to_show = mongo.db.plants.find_one_or_404(
            {"_id": ObjectId(plant_id)})

        context = {
            'plant': plant_to_show
        }

        return render_template('edit.html', **context)


@ app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):

    # delete a plant by the given id
    mongo.db.plants.delete_one({"_id": ObjectId(plant_id)})

    # delete all harvests associated with the deleted plant
    mongo.db.harvests.delete_many({"plant_id": plant_id})

    return redirect(url_for('plants_list'))


if __name__ == '__main__':
    app.run(debug=True)
