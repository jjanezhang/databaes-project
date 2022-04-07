from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import DecimalField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, InputRequired

from .models.product import Product

bp = Blueprint('products', __name__, url_prefix='/products')

class CreateProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = DecimalField('Price', validators=[InputRequired(), NumberRange(min=0)], places=2)
    image = FileField('Image', validators=[FileRequired(), FileAllowed(["png", "jpg", "jpeg"], "This file is not a valid image!",)])
    submit = SubmitField('Create Product')

@bp.route('/create', methods=['GET', 'POST'])
def create():
    create_product_form = CreateProductForm()
    if request.method == 'POST' and create_product_form.validate_on_submit():
        # TODO: Upload `create_product_form.image` to S3, then get a URL change the placeholder
        image_url = 'https://i0.wp.com/petmassage.com/wp-content/uploads/profile-pic-placeholder.png?w=512&ssl=1'
        if Product.create_product(create_product_form.name.data, round(create_product_form.price.data, 2), True, image_url) == 0:
            flash("Product name already taken!")
        else:
            flash("Product successfully created!")
            return redirect(url_for('products.create'))
    return render_template('create_product.html', create_product_form=create_product_form)
